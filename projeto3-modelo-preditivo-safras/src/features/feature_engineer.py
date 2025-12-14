"""
Engenharia de Features para Modelo de Predição de Safras.
"""

from typing import List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from loguru import logger


class FeatureEngineer:
    """
    Classe para engenharia de features agrícolas.

    Implementa transformações específicas para dados de produção agrícola:
    - Features temporais (lags, médias móveis, tendências)
    - Features de interação entre culturas
    - Normalização e encoding
    - Tratamento de outliers
    """

    def __init__(
        self,
        numeric_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        target: str = "rendimento_kg_ha"
    ):
        """
        Inicializa o engenheiro de features.

        Args:
            numeric_features: Lista de features numéricas
            categorical_features: Lista de features categóricas
            target: Nome da variável alvo
        """
        self.numeric_features = numeric_features or []
        self.categorical_features = categorical_features or []
        self.target = target

        self._scalers = {}
        self._encoders = {}
        self._fitted = False

    def create_temporal_features(
        self,
        df: pd.DataFrame,
        group_cols: List[str] = ["estado", "cultura"],
        value_col: str = "rendimento_kg_ha",
        lags: List[int] = [1, 2, 3]
    ) -> pd.DataFrame:
        """
        Cria features temporais (lag, média móvel, tendência).

        Args:
            df: DataFrame ordenado por tempo
            group_cols: Colunas para agrupar
            value_col: Coluna de valor
            lags: Lista de lags a criar

        Returns:
            DataFrame com features temporais
        """
        df = df.copy()
        df = df.sort_values(group_cols + ["ano"])

        # Lag features
        for lag in lags:
            col_name = f"{value_col}_lag{lag}"
            df[col_name] = df.groupby(group_cols)[value_col].shift(lag)

        # Média móvel (3 anos)
        df[f"{value_col}_ma3"] = df.groupby(group_cols)[value_col].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )

        # Desvio padrão móvel (volatilidade)
        df[f"{value_col}_std3"] = df.groupby(group_cols)[value_col].transform(
            lambda x: x.rolling(window=3, min_periods=1).std()
        )

        # Tendência (diferença com período anterior)
        df[f"{value_col}_diff"] = df.groupby(group_cols)[value_col].diff()

        # Taxa de crescimento
        df[f"{value_col}_pct_change"] = df.groupby(group_cols)[value_col].pct_change()

        # Máximo e mínimo histórico
        df[f"{value_col}_cummax"] = df.groupby(group_cols)[value_col].cummax()
        df[f"{value_col}_cummin"] = df.groupby(group_cols)[value_col].cummin()

        logger.info(f"Features temporais criadas para '{value_col}'")

        return df

    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features de interação.

        Args:
            df: DataFrame

        Returns:
            DataFrame com features de interação
        """
        df = df.copy()

        # Interação área x rendimento histórico
        if "area_plantada_ha" in df.columns and "rendimento_kg_ha_lag1" in df.columns:
            df["area_x_rend_lag"] = df["area_plantada_ha"] * df["rendimento_kg_ha_lag1"]

        # Eficiência (produção / área plantada)
        if "producao_ton" in df.columns and "area_plantada_ha" in df.columns:
            df["eficiencia"] = df["producao_ton"] / df["area_plantada_ha"].replace(0, np.nan)

        # Valor por tonelada
        if "valor_producao_mil_reais" in df.columns and "producao_ton" in df.columns:
            df["valor_por_ton"] = (df["valor_producao_mil_reais"] * 1000) / df["producao_ton"].replace(0, np.nan)

        # Razão área colhida / plantada (perda)
        if "area_colhida_ha" in df.columns and "area_plantada_ha" in df.columns:
            df["razao_colheita"] = df["area_colhida_ha"] / df["area_plantada_ha"].replace(0, np.nan)
            df["perda_area"] = 1 - df["razao_colheita"]

        logger.info("Features de interação criadas")

        return df

    def create_aggregated_features(
        self,
        df: pd.DataFrame,
        group_col: str = "estado"
    ) -> pd.DataFrame:
        """
        Cria features agregadas por grupo.

        Args:
            df: DataFrame
            group_col: Coluna para agrupar

        Returns:
            DataFrame com features agregadas
        """
        df = df.copy()

        # Média do grupo
        for col in ["rendimento_kg_ha", "area_plantada_ha"]:
            if col in df.columns:
                group_mean = df.groupby([group_col, "ano"])[col].transform("mean")
                df[f"{col}_{group_col}_mean"] = group_mean

                # Desvio em relação à média do grupo
                df[f"{col}_{group_col}_dev"] = df[col] - group_mean

        # Ranking dentro do grupo
        if "rendimento_kg_ha" in df.columns:
            df["ranking_rendimento"] = df.groupby([group_col, "ano"])["rendimento_kg_ha"].rank(
                ascending=False, method="dense"
            )

        logger.info(f"Features agregadas criadas para '{group_col}'")

        return df

    def handle_outliers(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = "clip",
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Trata outliers nas features numéricas.

        Args:
            df: DataFrame
            columns: Colunas a tratar (None = todas numéricas)
            method: 'clip' (limitar) ou 'remove' (remover linhas)
            threshold: Número de desvios padrão para considerar outlier

        Returns:
            DataFrame com outliers tratados
        """
        df = df.copy()

        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        outliers_count = 0

        for col in columns:
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()

                lower = mean - threshold * std
                upper = mean + threshold * std

                outliers = ((df[col] < lower) | (df[col] > upper)).sum()
                outliers_count += outliers

                if method == "clip":
                    df[col] = df[col].clip(lower=lower, upper=upper)
                elif method == "remove":
                    df = df[(df[col] >= lower) & (df[col] <= upper)]

        logger.info(f"Outliers tratados: {outliers_count} valores ({method})")

        return df

    def build_preprocessing_pipeline(
        self,
        numeric_features: List[str],
        categorical_features: List[str],
        scaler: str = "standard"
    ) -> ColumnTransformer:
        """
        Constrói pipeline de pré-processamento.

        Args:
            numeric_features: Features numéricas
            categorical_features: Features categóricas
            scaler: Tipo de scaler ('standard', 'minmax', 'robust')

        Returns:
            ColumnTransformer configurado
        """
        # Selecionar scaler
        scalers = {
            "standard": StandardScaler(),
            "minmax": MinMaxScaler(),
            "robust": RobustScaler()
        }
        selected_scaler = scalers.get(scaler, StandardScaler())

        # Pipeline numérico
        numeric_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", selected_scaler)
        ])

        # Pipeline categórico
        categorical_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])

        # Combinar pipelines
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_pipeline, numeric_features),
                ("cat", categorical_pipeline, categorical_features)
            ],
            remainder="drop"
        )

        logger.info(
            f"Pipeline criado | numeric: {len(numeric_features)} | "
            f"categorical: {len(categorical_features)}"
        )

        return preprocessor

    def fit_transform(
        self,
        df: pd.DataFrame,
        target_col: Optional[str] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Aplica todas as transformações e retorna dados prontos.

        Args:
            df: DataFrame original
            target_col: Coluna alvo (usa self.target se None)

        Returns:
            Tuple (X, y) com features e target
        """
        target_col = target_col or self.target

        # Aplicar transformações
        df_transformed = self.create_temporal_features(df)
        df_transformed = self.create_interaction_features(df_transformed)
        df_transformed = self.create_aggregated_features(df_transformed)
        df_transformed = self.handle_outliers(df_transformed)

        # Separar X e y
        y = df_transformed[target_col].copy()
        X = df_transformed.drop(columns=[target_col])

        # Remover colunas não úteis
        cols_to_drop = [
            "localidade_id", "localidade", "nivel",
            "cultura_id", "variavel_id", "variavel", "unidade"
        ]
        X = X.drop(columns=[c for c in cols_to_drop if c in X.columns])

        self._fitted = True

        logger.info(f"Transformação completa | X: {X.shape} | y: {len(y)}")

        return X, y


# Transformadores customizados para sklearn Pipeline
class TemporalFeatureTransformer(BaseEstimator, TransformerMixin):
    """Transformador de features temporais para uso em Pipeline."""

    def __init__(self, group_cols: List[str], value_col: str, lags: List[int] = [1, 2]):
        self.group_cols = group_cols
        self.value_col = value_col
        self.lags = lags

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        for lag in self.lags:
            col_name = f"{self.value_col}_lag{lag}"
            if all(c in X.columns for c in self.group_cols):
                X[col_name] = X.groupby(self.group_cols)[self.value_col].shift(lag)

        return X


class OutlierClipTransformer(BaseEstimator, TransformerMixin):
    """Transformador para clipar outliers."""

    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold
        self._bounds = {}

    def fit(self, X, y=None):
        X_numeric = X.select_dtypes(include=[np.number])

        for col in X_numeric.columns:
            mean = X_numeric[col].mean()
            std = X_numeric[col].std()
            self._bounds[col] = (
                mean - self.threshold * std,
                mean + self.threshold * std
            )

        return self

    def transform(self, X):
        X = X.copy()

        for col, (lower, upper) in self._bounds.items():
            if col in X.columns:
                X[col] = X[col].clip(lower=lower, upper=upper)

        return X
