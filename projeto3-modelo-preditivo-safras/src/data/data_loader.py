"""
Carregador e preparador de dados para modelagem.
"""

from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
import numpy as np
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings, REGIOES
from src.data.pam_extractor import PAMExtractor, generate_synthetic_pam_data
from src.features.multicollinearity import VIFAnalyzer


class DataLoader:
    """
    Carregador de dados para o pipeline de ML.

    Responsável por:
    - Carregar dados da API ou cache local
    - Preparar dados para modelagem
    - Dividir em treino/teste
    """

    def __init__(self, use_cache: bool = True):
        """
        Inicializa o loader.

        Args:
            use_cache: Se deve usar dados em cache
        """
        self.use_cache = use_cache
        self.data_dir = Path(settings.data.processed_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._cache_file = self.data_dir / "pam_data.parquet"

    def load_data(
        self,
        use_synthetic: bool = True,
        force_reload: bool = False
    ) -> pd.DataFrame:
        """
        Carrega dados da PAM.

        Args:
            use_synthetic: Se deve usar dados sintéticos (para demo)
            force_reload: Se deve forçar recarga dos dados

        Returns:
            DataFrame com dados de produção agrícola
        """
        # Verificar cache
        if self.use_cache and self._cache_file.exists() and not force_reload:
            logger.info(f"Carregando dados do cache: {self._cache_file}")
            return pd.read_parquet(self._cache_file)

        # Gerar ou extrair dados
        if use_synthetic:
            logger.info("Gerando dados sintéticos...")
            df = generate_synthetic_pam_data(
                anos=range(2000, 2024),
                n_municipios=200
            )
        else:
            logger.info("Extraindo dados da API SIDRA...")
            with PAMExtractor() as extractor:
                # Extrair principais culturas
                from config.settings import CODIGOS_CULTURAS
                codigos = list(CODIGOS_CULTURAS.values())[:5]

                df = extractor.extract_multiplas_culturas(
                    codigos_culturas=codigos,
                    anos="2015|2016|2017|2018|2019|2020|2021|2022|2023",
                    nivel="N3"  # Estados
                )

        # Adicionar features derivadas
        df = self._add_derived_features(df)

        # Salvar cache
        if self.use_cache:
            df.to_parquet(self._cache_file, index=False)
            logger.info(f"Dados salvos em cache: {self._cache_file}")

        return df

    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona features derivadas aos dados.

        Args:
            df: DataFrame original

        Returns:
            DataFrame com features adicionais
        """
        df = df.copy()

        # Adicionar região
        estado_para_regiao = {}
        for regiao, estados in REGIOES.items():
            for estado in estados:
                estado_para_regiao[estado] = regiao

        df["regiao"] = df["estado"].map(estado_para_regiao)

        # DATA LEAKAGE REMOVED: taxa_aproveitamento, produtividade_ton_ha, valor_por_ha
        # These features are derived from or highly correlated with the target variable.
        # - taxa_aproveitamento: area_colhida correlates with yield
        # - produtividade_ton_ha: direct calculation from producao_ton (target * area)
        # - valor_por_ha: depends on production which is derived from target

        # Lag features (ano anterior)
        df = df.sort_values(["estado", "cultura", "ano"])

        for col in ["rendimento_kg_ha", "area_plantada_ha", "producao_ton"]:
            if col in df.columns:
                df[f"{col}_lag1"] = df.groupby(["estado", "cultura"])[col].shift(1)

        # Tendência (diferença com ano anterior)
        # REMOVED: rendimento_tendencia uses current year rendimento (target variable)
        # This would leak the target into the features

        # Porte do município/estado (baseado em área)
        if "area_plantada_ha" in df.columns:
            df["porte"] = pd.cut(
                df["area_plantada_ha"],
                bins=[0, 1000, 10000, 50000, float("inf")],
                labels=["Pequeno", "Médio", "Grande", "Muito Grande"]
            )

        logger.info(f"Features derivadas adicionadas (sem data leakage). Total colunas: {len(df.columns)}")

        return df

    def prepare_for_modeling(
        self,
        df: pd.DataFrame,
        target: str = "rendimento_kg_ha",
        test_size: float = 0.2,
        use_time_series_split: bool = True,
        check_multicollinearity: bool = True,
        vif_threshold: float = 10.0,
        remove_high_vif: bool = False
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Prepara dados para modelagem com validação temporal adequada.

        Args:
            df: DataFrame com dados
            target: Coluna alvo
            test_size: Proporção do conjunto de teste
            use_time_series_split: Se True, usa split temporal (anos anteriores para treino)
                                  Se False, usa split aleatório (não recomendado)
            check_multicollinearity: Se True, verifica VIF das features
            vif_threshold: Limite de VIF para gerar warnings (default: 10.0)
            remove_high_vif: Se True, remove automaticamente features com VIF alto

        Returns:
            X_train, X_test, y_train, y_test
        """
        # Remover linhas com target nulo
        df_clean = df.dropna(subset=[target])

        # Remover colunas não utilizáveis
        cols_to_drop = [
            target,
            "localidade_id", "localidade", "nivel",
            "cultura_id", "variavel_id", "variavel", "unidade"
        ]
        cols_to_drop = [c for c in cols_to_drop if c in df_clean.columns]

        X = df_clean.drop(columns=cols_to_drop)
        y = df_clean[target]

        # Converter categóricas para dummies
        X = pd.get_dummies(X, columns=["estado", "cultura", "regiao", "porte"], drop_first=True)

        # Remover colunas com muitos nulos
        X = X.dropna(axis=1, thresh=len(X) * 0.5)

        # Preencher nulos restantes
        X = X.fillna(X.median(numeric_only=True))

        # MULTICOLLINEARITY CHECK: Detect and optionally remove highly correlated features
        if check_multicollinearity:
            vif_analyzer = VIFAnalyzer(threshold=vif_threshold, warning_threshold=5.0)

            # Calculate VIF for numeric features only
            numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()

            if len(numeric_features) > 0:
                vif_df = vif_analyzer.calculate_vif(X, numeric_features)

                # Log features with high VIF
                high_vif_features = vif_df[vif_df["vif"] > vif_threshold]

                if len(high_vif_features) > 0:
                    logger.warning(
                        f"\n{'='*60}\n"
                        f"MULTICOLLINEARITY DETECTED (VIF > {vif_threshold}):\n"
                        f"{high_vif_features[['feature', 'vif']].to_string(index=False)}\n"
                        f"{'='*60}"
                    )

                    if remove_high_vif:
                        # Remove high VIF features iteratively
                        X, removed_features = vif_analyzer.remove_high_vif_features(
                            X,
                            vif_df=vif_df,
                            max_iterations=10
                        )
                        logger.info(
                            f"Removed {len(removed_features)} high-VIF features: {removed_features}"
                        )
                    else:
                        logger.info(
                            "To automatically remove high-VIF features, set remove_high_vif=True"
                        )
                else:
                    logger.info(f"No multicollinearity issues detected (all VIF <= {vif_threshold})")

        # TIME SERIES SPLIT: Training data is always from years BEFORE test data
        # This prevents data leakage and simulates real-world prediction scenarios
        # where we use historical data to predict future outcomes
        if use_time_series_split and "ano" in X.columns:
            # Sort by year to ensure temporal ordering
            df_sorted = pd.concat([X, y], axis=1).sort_values("ano")
            X_sorted = df_sorted.drop(columns=[target])
            y_sorted = df_sorted[target]

            # Calculate split point based on test_size
            split_idx = int(len(X_sorted) * (1 - test_size))

            X_train = X_sorted.iloc[:split_idx]
            X_test = X_sorted.iloc[split_idx:]
            y_train = y_sorted.iloc[:split_idx]
            y_test = y_sorted.iloc[split_idx:]

            train_years = X_train["ano"].min(), X_train["ano"].max()
            test_years = X_test["ano"].min(), X_test["ano"].max()

            logger.info(
                f"Time Series Split | Train anos: {train_years[0]}-{train_years[1]} | "
                f"Test anos: {test_years[0]}-{test_years[1]}"
            )
        else:
            # Fallback to random split (not recommended for time series)
            from sklearn.model_selection import train_test_split

            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=test_size,
                random_state=settings.model.random_state
            )

            if not use_time_series_split:
                logger.warning(
                    "Using RANDOM split for time series data may cause data leakage! "
                    "Consider setting use_time_series_split=True"
                )

        logger.info(
            f"Dados preparados | X_train: {X_train.shape} | X_test: {X_test.shape}"
        )

        return X_train, X_test, y_train, y_test

    def get_feature_names(self, df: pd.DataFrame) -> dict:
        """
        Retorna nomes das features por tipo.

        Args:
            df: DataFrame

        Returns:
            Dicionário com listas de features por tipo
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        return {
            "numeric": numeric_cols,
            "categorical": categorical_cols,
            "all": numeric_cols + categorical_cols
        }
