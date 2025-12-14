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

        # Taxa de aproveitamento (área colhida / área plantada)
        if "area_plantada_ha" in df.columns and "area_colhida_ha" in df.columns:
            df["taxa_aproveitamento"] = (
                df["area_colhida_ha"] / df["area_plantada_ha"]
            ).clip(0, 1)

        # Produtividade relativa (produção / área plantada)
        if "producao_ton" in df.columns and "area_plantada_ha" in df.columns:
            df["produtividade_ton_ha"] = df["producao_ton"] / df["area_plantada_ha"]

        # Valor por hectare
        if "valor_producao_mil_reais" in df.columns and "area_colhida_ha" in df.columns:
            df["valor_por_ha"] = (df["valor_producao_mil_reais"] * 1000) / df["area_colhida_ha"]

        # Lag features (ano anterior)
        df = df.sort_values(["estado", "cultura", "ano"])

        for col in ["rendimento_kg_ha", "area_plantada_ha", "producao_ton"]:
            if col in df.columns:
                df[f"{col}_lag1"] = df.groupby(["estado", "cultura"])[col].shift(1)

        # Tendência (diferença com ano anterior)
        if "rendimento_kg_ha" in df.columns:
            df["rendimento_tendencia"] = df["rendimento_kg_ha"] - df["rendimento_kg_ha_lag1"]

        # Porte do município/estado (baseado em área)
        if "area_plantada_ha" in df.columns:
            df["porte"] = pd.cut(
                df["area_plantada_ha"],
                bins=[0, 1000, 10000, 50000, float("inf")],
                labels=["Pequeno", "Médio", "Grande", "Muito Grande"]
            )

        logger.info(f"Features derivadas adicionadas. Total colunas: {len(df.columns)}")

        return df

    def prepare_for_modeling(
        self,
        df: pd.DataFrame,
        target: str = "rendimento_kg_ha",
        test_size: float = 0.2
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Prepara dados para modelagem.

        Args:
            df: DataFrame com dados
            target: Coluna alvo
            test_size: Proporção do conjunto de teste

        Returns:
            X_train, X_test, y_train, y_test
        """
        from sklearn.model_selection import train_test_split

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

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=settings.model.random_state
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
