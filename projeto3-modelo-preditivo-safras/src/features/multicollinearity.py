"""
Módulo para detecção e tratamento de multicolinearidade usando VIF.

VIF (Variance Inflation Factor) mede o quanto a variância de um coeficiente de
regressão é inflada devido à multicolinearidade com outras features.

Interpretação do VIF:
- VIF = 1: Sem correlação com outras features
- VIF < 5: Multicolinearidade aceitável
- VIF 5-10: Multicolinearidade moderada (atenção necessária)
- VIF > 10: Multicolinearidade alta (remover feature recomendado)
- VIF > 20: Multicolinearidade severa (remover obrigatório)
"""

from typing import List, Optional, Tuple, Dict
import pandas as pd
import numpy as np
from statsmodels.stats.outliers_influence import variance_inflation_factor
from loguru import logger


class VIFAnalyzer:
    """
    Analisador de multicolinearidade usando Variance Inflation Factor (VIF).

    O VIF quantifica o quanto a variância de cada coeficiente estimado aumenta
    devido à correlação linear com outras features independentes.

    Fórmula: VIF_i = 1 / (1 - R²_i)
    onde R²_i é o R² da regressão da feature i contra todas as outras features.
    """

    def __init__(
        self,
        threshold: float = 10.0,
        warning_threshold: float = 5.0
    ):
        """
        Inicializa o analisador VIF.

        Args:
            threshold: Limite superior para VIF (features acima serão marcadas para remoção)
            warning_threshold: Limite de aviso (features acima serão marcadas com warning)
        """
        self.threshold = threshold
        self.warning_threshold = warning_threshold
        self.vif_results: Optional[pd.DataFrame] = None

    def calculate_vif(
        self,
        df: pd.DataFrame,
        features: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calcula VIF para todas as features numéricas.

        Args:
            df: DataFrame com features
            features: Lista de features a analisar (None = todas numéricas)

        Returns:
            DataFrame com feature, VIF e status
        """
        # Selecionar features numéricas
        if features is None:
            features = df.select_dtypes(include=[np.number]).columns.tolist()

        # Remover colunas com valores constantes (VIF infinito)
        df_clean = df[features].copy()
        constant_cols = [col for col in df_clean.columns if df_clean[col].nunique() <= 1]

        if constant_cols:
            logger.warning(f"Removendo colunas constantes: {constant_cols}")
            df_clean = df_clean.drop(columns=constant_cols)
            features = [f for f in features if f not in constant_cols]

        # Remover linhas com NaN
        df_clean = df_clean.dropna()

        if len(df_clean) == 0:
            logger.error("Nenhuma linha válida após remoção de NaN")
            return pd.DataFrame()

        # Calcular VIF para cada feature
        vif_data = []

        for i, feature in enumerate(features):
            try:
                vif_value = variance_inflation_factor(df_clean.values, i)

                # Determinar status
                if vif_value > self.threshold:
                    status = "REMOVER"
                    severity = "high"
                elif vif_value > self.warning_threshold:
                    status = "ATENÇÃO"
                    severity = "moderate"
                else:
                    status = "OK"
                    severity = "low"

                vif_data.append({
                    "feature": feature,
                    "vif": vif_value,
                    "status": status,
                    "severity": severity
                })

            except Exception as e:
                logger.warning(f"Erro ao calcular VIF para {feature}: {str(e)}")
                vif_data.append({
                    "feature": feature,
                    "vif": np.inf,
                    "status": "ERRO",
                    "severity": "error"
                })

        # Criar DataFrame e ordenar por VIF (maior primeiro)
        vif_df = pd.DataFrame(vif_data).sort_values("vif", ascending=False)
        self.vif_results = vif_df

        # Log resumo
        high_vif = (vif_df["vif"] > self.threshold).sum()
        moderate_vif = ((vif_df["vif"] > self.warning_threshold) &
                        (vif_df["vif"] <= self.threshold)).sum()

        logger.info(
            f"VIF calculado para {len(features)} features | "
            f"Alta multicolinearidade: {high_vif} | "
            f"Moderada: {moderate_vif}"
        )

        return vif_df

    def get_high_vif_features(
        self,
        vif_df: Optional[pd.DataFrame] = None
    ) -> List[str]:
        """
        Retorna lista de features com VIF alto (acima do threshold).

        Args:
            vif_df: DataFrame com VIF (None = usar último calculado)

        Returns:
            Lista de features com VIF alto
        """
        if vif_df is None:
            vif_df = self.vif_results

        if vif_df is None:
            logger.warning("Nenhum resultado VIF disponível")
            return []

        high_vif_features = vif_df[vif_df["vif"] > self.threshold]["feature"].tolist()

        return high_vif_features

    def remove_high_vif_features(
        self,
        df: pd.DataFrame,
        vif_df: Optional[pd.DataFrame] = None,
        max_iterations: int = 10
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Remove iterativamente features com VIF alto.

        O processo remove a feature com maior VIF, recalcula, e repete
        até que todas as features tenham VIF aceitável ou atingir max_iterations.

        Args:
            df: DataFrame original
            vif_df: DataFrame com VIF inicial (None = calcular novo)
            max_iterations: Número máximo de iterações

        Returns:
            Tuple (DataFrame sem features de alto VIF, lista de features removidas)
        """
        df_clean = df.copy()
        removed_features = []

        for iteration in range(max_iterations):
            # Calcular VIF atual
            current_vif = self.calculate_vif(df_clean)

            # Verificar se há features com VIF alto
            high_vif = current_vif[current_vif["vif"] > self.threshold]

            if len(high_vif) == 0:
                logger.info(
                    f"Convergência alcançada após {iteration} iterações. "
                    f"Todas features têm VIF <= {self.threshold}"
                )
                break

            # Remover feature com maior VIF
            worst_feature = high_vif.iloc[0]["feature"]
            worst_vif = high_vif.iloc[0]["vif"]

            logger.info(
                f"Iteração {iteration + 1}: Removendo '{worst_feature}' "
                f"(VIF = {worst_vif:.2f})"
            )

            df_clean = df_clean.drop(columns=[worst_feature])
            removed_features.append(worst_feature)
        else:
            logger.warning(
                f"Máximo de iterações ({max_iterations}) atingido. "
                f"Ainda existem features com VIF alto."
            )

        logger.info(
            f"Remoção VIF completa | Features removidas: {len(removed_features)} | "
            f"Features restantes: {len(df_clean.columns)}"
        )

        return df_clean, removed_features

    def get_correlation_matrix(
        self,
        df: pd.DataFrame,
        features: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calcula matriz de correlação para features.

        Args:
            df: DataFrame
            features: Lista de features (None = todas numéricas)

        Returns:
            Matriz de correlação
        """
        if features is None:
            features = df.select_dtypes(include=[np.number]).columns.tolist()

        corr_matrix = df[features].corr()

        return corr_matrix

    def get_highly_correlated_pairs(
        self,
        df: pd.DataFrame,
        threshold: float = 0.8,
        features: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Identifica pares de features altamente correlacionadas.

        Args:
            df: DataFrame
            threshold: Limite de correlação absoluta
            features: Lista de features (None = todas numéricas)

        Returns:
            DataFrame com pares correlacionados
        """
        corr_matrix = self.get_correlation_matrix(df, features)

        # Extrair apenas triangulo superior (evitar duplicatas)
        corr_pairs = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]

                if abs(corr_value) >= threshold:
                    corr_pairs.append({
                        "feature_1": corr_matrix.columns[i],
                        "feature_2": corr_matrix.columns[j],
                        "correlation": corr_value,
                        "abs_correlation": abs(corr_value)
                    })

        if len(corr_pairs) == 0:
            logger.info(f"Nenhum par com correlação >= {threshold}")
            return pd.DataFrame()

        corr_df = pd.DataFrame(corr_pairs).sort_values("abs_correlation", ascending=False)

        logger.info(f"Encontrados {len(corr_df)} pares com correlação >= {threshold}")

        return corr_df

    def generate_report(
        self,
        vif_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, any]:
        """
        Gera relatório completo de multicolinearidade.

        Args:
            vif_df: DataFrame com VIF (None = usar último calculado)

        Returns:
            Dicionário com estatísticas do relatório
        """
        if vif_df is None:
            vif_df = self.vif_results

        if vif_df is None:
            logger.error("Nenhum resultado VIF disponível para relatório")
            return {}

        report = {
            "total_features": len(vif_df),
            "high_vif_count": len(vif_df[vif_df["vif"] > self.threshold]),
            "moderate_vif_count": len(
                vif_df[(vif_df["vif"] > self.warning_threshold) &
                       (vif_df["vif"] <= self.threshold)]
            ),
            "low_vif_count": len(vif_df[vif_df["vif"] <= self.warning_threshold]),
            "mean_vif": vif_df["vif"].mean(),
            "median_vif": vif_df["vif"].median(),
            "max_vif": vif_df["vif"].max(),
            "max_vif_feature": vif_df.iloc[0]["feature"] if len(vif_df) > 0 else None,
            "features_to_remove": self.get_high_vif_features(vif_df)
        }

        return report


# Funções utilitárias standalone
def quick_vif_check(
    df: pd.DataFrame,
    features: Optional[List[str]] = None,
    threshold: float = 10.0
) -> pd.DataFrame:
    """
    Função rápida para checar VIF de um DataFrame.

    Args:
        df: DataFrame com features
        features: Lista de features (None = todas numéricas)
        threshold: Limite de VIF para alerta

    Returns:
        DataFrame com VIF de todas features
    """
    analyzer = VIFAnalyzer(threshold=threshold)
    vif_df = analyzer.calculate_vif(df, features)

    # Alertar sobre features problemáticas
    high_vif = vif_df[vif_df["vif"] > threshold]

    if len(high_vif) > 0:
        logger.warning(
            f"ATENÇÃO: {len(high_vif)} features com VIF > {threshold}:\n"
            f"{high_vif[['feature', 'vif']].to_string(index=False)}"
        )
    else:
        logger.info(f"Todas features têm VIF <= {threshold}")

    return vif_df


def auto_remove_multicollinearity(
    df: pd.DataFrame,
    threshold: float = 10.0,
    max_iterations: int = 10
) -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Remove automaticamente multicolinearidade de um DataFrame.

    Args:
        df: DataFrame original
        threshold: Limite de VIF
        max_iterations: Número máximo de iterações

    Returns:
        Tuple (DataFrame limpo, relatório de remoção)
    """
    analyzer = VIFAnalyzer(threshold=threshold)

    df_clean, removed_features = analyzer.remove_high_vif_features(
        df,
        max_iterations=max_iterations
    )

    # Gerar relatório final
    final_vif = analyzer.calculate_vif(df_clean)
    report = analyzer.generate_report(final_vif)
    report["removed_features"] = removed_features

    return df_clean, report


# Exemplo de uso
if __name__ == "__main__":
    # Dados de exemplo com multicolinearidade
    np.random.seed(42)
    n_samples = 1000

    # Features correlacionadas
    x1 = np.random.randn(n_samples)
    x2 = x1 + np.random.randn(n_samples) * 0.1  # Alta correlação com x1
    x3 = 2 * x1 + np.random.randn(n_samples) * 0.1  # Muito correlacionada
    x4 = np.random.randn(n_samples)  # Independente
    x5 = x4 + np.random.randn(n_samples) * 0.5  # Moderada correlação

    df_example = pd.DataFrame({
        "feature_1": x1,
        "feature_2": x2,
        "feature_3": x3,
        "feature_4": x4,
        "feature_5": x5
    })

    # Análise VIF
    print("=" * 50)
    print("VIF Analysis Example")
    print("=" * 50)

    analyzer = VIFAnalyzer(threshold=10.0, warning_threshold=5.0)
    vif_df = analyzer.calculate_vif(df_example)

    print("\nResultados VIF:")
    print(vif_df.to_string(index=False))

    print("\n" + "=" * 50)
    print("Relatório de Multicolinearidade")
    print("=" * 50)

    report = analyzer.generate_report()
    for key, value in report.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 50)
    print("Remoção Automática de Multicolinearidade")
    print("=" * 50)

    df_clean, removed = analyzer.remove_high_vif_features(df_example)
    print(f"\nFeatures removidas: {removed}")
    print(f"Features restantes: {list(df_clean.columns)}")
