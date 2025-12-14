"""
Avaliador de Modelos com Visualizações e Métricas.
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    mean_absolute_percentage_error
)
from loguru import logger

# Plotly para gráficos interativos
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class ModelEvaluator:
    """
    Avaliador de modelos com visualizações e análises.

    Gera:
    - Métricas de performance (RMSE, MAE, R², MAPE)
    - Gráficos de resíduos
    - Comparação de modelos
    - Análise de feature importance
    - Learning curves
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Inicializa o avaliador.

        Args:
            output_dir: Diretório para salvar visualizações
        """
        self.output_dir = Path(output_dir) if output_dir else Path("outputs/figures")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configurar estilo
        plt.style.use("seaborn-v0_8-whitegrid")
        plt.rcParams["figure.figsize"] = (12, 6)
        plt.rcParams["font.size"] = 12

    def calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Calcula métricas de regressão.

        Args:
            y_true: Valores reais
            y_pred: Valores preditos

        Returns:
            Dicionário com métricas
        """
        return {
            "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
            "mae": mean_absolute_error(y_true, y_pred),
            "r2": r2_score(y_true, y_pred),
            "mape": mean_absolute_percentage_error(y_true, y_pred) * 100,
            "max_error": np.max(np.abs(y_true - y_pred)),
            "median_ae": np.median(np.abs(y_true - y_pred))
        }

    def plot_predictions_vs_actual(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        title: str = "Predições vs Valores Reais",
        save: bool = True
    ) -> go.Figure:
        """
        Gráfico de dispersão: Predições vs Valores Reais.

        Args:
            y_true: Valores reais
            y_pred: Valores preditos
            title: Título do gráfico
            save: Se deve salvar o gráfico

        Returns:
            Figura Plotly
        """
        metrics = self.calculate_metrics(y_true, y_pred)

        fig = go.Figure()

        # Pontos de dispersão
        fig.add_trace(go.Scatter(
            x=y_true,
            y=y_pred,
            mode="markers",
            marker=dict(
                size=8,
                color=np.abs(y_true - y_pred),
                colorscale="RdYlGn_r",
                showscale=True,
                colorbar=dict(title="Erro Absoluto")
            ),
            name="Predições",
            hovertemplate="Real: %{x:.2f}<br>Predito: %{y:.2f}<extra></extra>"
        ))

        # Linha de referência (y = x)
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())

        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            line=dict(color="red", dash="dash", width=2),
            name="Linha Ideal (y=x)"
        ))

        # Anotação com métricas
        annotation_text = (
            f"R² = {metrics['r2']:.4f}<br>"
            f"RMSE = {metrics['rmse']:.2f}<br>"
            f"MAE = {metrics['mae']:.2f}<br>"
            f"MAPE = {metrics['mape']:.2f}%"
        )

        fig.add_annotation(
            x=0.05, y=0.95,
            xref="paper", yref="paper",
            text=annotation_text,
            showarrow=False,
            font=dict(size=12),
            bgcolor="white",
            bordercolor="gray",
            borderwidth=1
        )

        fig.update_layout(
            title=title,
            xaxis_title="Valores Reais",
            yaxis_title="Valores Preditos",
            hovermode="closest"
        )

        if save:
            fig.write_html(self.output_dir / "predictions_vs_actual.html")

        return fig

    def plot_residuals(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        title: str = "Análise de Resíduos",
        save: bool = True
    ) -> go.Figure:
        """
        Gráfico de análise de resíduos.

        Args:
            y_true: Valores reais
            y_pred: Valores preditos
            title: Título
            save: Se deve salvar

        Returns:
            Figura Plotly
        """
        residuals = y_true - y_pred

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Resíduos vs Preditos",
                "Distribuição dos Resíduos",
                "Q-Q Plot",
                "Resíduos ao Longo do Tempo"
            )
        )

        # 1. Resíduos vs Preditos
        fig.add_trace(
            go.Scatter(
                x=y_pred,
                y=residuals,
                mode="markers",
                marker=dict(size=6, opacity=0.6),
                name="Resíduos"
            ),
            row=1, col=1
        )
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)

        # 2. Histograma de resíduos
        fig.add_trace(
            go.Histogram(
                x=residuals,
                nbinsx=30,
                name="Distribuição",
                marker_color="steelblue"
            ),
            row=1, col=2
        )

        # 3. Q-Q Plot (aproximado)
        from scipy import stats
        theoretical_quantiles = stats.norm.ppf(
            np.linspace(0.01, 0.99, len(residuals))
        )
        sorted_residuals = np.sort(residuals)

        fig.add_trace(
            go.Scatter(
                x=theoretical_quantiles,
                y=sorted_residuals,
                mode="markers",
                name="Q-Q"
            ),
            row=2, col=1
        )
        # Linha de referência Q-Q
        fig.add_trace(
            go.Scatter(
                x=theoretical_quantiles,
                y=theoretical_quantiles * np.std(residuals) + np.mean(residuals),
                mode="lines",
                line=dict(color="red", dash="dash"),
                name="Normal"
            ),
            row=2, col=1
        )

        # 4. Resíduos sequenciais
        fig.add_trace(
            go.Scatter(
                x=list(range(len(residuals))),
                y=residuals,
                mode="lines+markers",
                marker=dict(size=4),
                name="Sequência"
            ),
            row=2, col=2
        )
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=2, col=2)

        fig.update_layout(
            title=title,
            height=800,
            showlegend=False
        )

        if save:
            fig.write_html(self.output_dir / "residuals_analysis.html")

        return fig

    def plot_model_comparison(
        self,
        results_df: pd.DataFrame,
        metric: str = "rmse",
        title: str = "Comparação de Modelos",
        save: bool = True
    ) -> go.Figure:
        """
        Gráfico de comparação entre modelos.

        Args:
            results_df: DataFrame com métricas por modelo
            metric: Métrica para comparação
            title: Título
            save: Se deve salvar

        Returns:
            Figura Plotly
        """
        df = results_df.sort_values(metric)

        # Cores baseadas na performance
        colors = px.colors.sample_colorscale(
            "RdYlGn_r",
            [i / len(df) for i in range(len(df))]
        )

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df["model"],
            y=df[metric],
            marker_color=colors,
            text=df[metric].round(2),
            textposition="outside"
        ))

        fig.update_layout(
            title=f"{title} ({metric.upper()})",
            xaxis_title="Modelo",
            yaxis_title=metric.upper(),
            xaxis_tickangle=-45
        )

        if save:
            fig.write_html(self.output_dir / "model_comparison.html")

        return fig

    def plot_feature_importance(
        self,
        importance_df: pd.DataFrame,
        top_n: int = 20,
        title: str = "Importância das Features",
        save: bool = True
    ) -> go.Figure:
        """
        Gráfico de importância das features.

        Args:
            importance_df: DataFrame com colunas [feature, importance]
            top_n: Número de features a mostrar
            title: Título
            save: Se deve salvar

        Returns:
            Figura Plotly
        """
        df = importance_df.head(top_n).sort_values("importance")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df["importance"],
            y=df["feature"],
            orientation="h",
            marker=dict(
                color=df["importance"],
                colorscale="Viridis"
            )
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Importância",
            yaxis_title="Feature",
            height=max(400, top_n * 25)
        )

        if save:
            fig.write_html(self.output_dir / "feature_importance.html")

        return fig

    def plot_learning_curve(
        self,
        train_sizes: np.ndarray,
        train_scores: np.ndarray,
        val_scores: np.ndarray,
        title: str = "Curva de Aprendizado",
        save: bool = True
    ) -> go.Figure:
        """
        Gráfico de curva de aprendizado.

        Args:
            train_sizes: Tamanhos de treino
            train_scores: Scores de treino (média por fold)
            val_scores: Scores de validação (média por fold)
            title: Título
            save: Se deve salvar

        Returns:
            Figura Plotly
        """
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        val_mean = np.mean(val_scores, axis=1)
        val_std = np.std(val_scores, axis=1)

        fig = go.Figure()

        # Treino
        fig.add_trace(go.Scatter(
            x=train_sizes,
            y=train_mean,
            mode="lines+markers",
            name="Treino",
            line=dict(color="blue")
        ))
        fig.add_trace(go.Scatter(
            x=np.concatenate([train_sizes, train_sizes[::-1]]),
            y=np.concatenate([
                train_mean - train_std,
                (train_mean + train_std)[::-1]
            ]),
            fill="toself",
            fillcolor="rgba(0,0,255,0.1)",
            line=dict(color="rgba(255,255,255,0)"),
            name="Treino ± std"
        ))

        # Validação
        fig.add_trace(go.Scatter(
            x=train_sizes,
            y=val_mean,
            mode="lines+markers",
            name="Validação",
            line=dict(color="green")
        ))
        fig.add_trace(go.Scatter(
            x=np.concatenate([train_sizes, train_sizes[::-1]]),
            y=np.concatenate([
                val_mean - val_std,
                (val_mean + val_std)[::-1]
            ]),
            fill="toself",
            fillcolor="rgba(0,255,0,0.1)",
            line=dict(color="rgba(255,255,255,0)"),
            name="Validação ± std"
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Tamanho do Conjunto de Treino",
            yaxis_title="Score"
        )

        if save:
            fig.write_html(self.output_dir / "learning_curve.html")

        return fig

    def generate_report(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        model_name: str,
        feature_importance: Optional[pd.DataFrame] = None
    ) -> str:
        """
        Gera relatório completo de avaliação.

        Args:
            y_true: Valores reais
            y_pred: Valores preditos
            model_name: Nome do modelo
            feature_importance: DataFrame de importância das features

        Returns:
            Texto do relatório em Markdown
        """
        metrics = self.calculate_metrics(y_true, y_pred)

        report = f"""
# Relatório de Avaliação do Modelo

## Modelo: {model_name}

### Métricas de Performance

| Métrica | Valor |
|---------|-------|
| R² (Coeficiente de Determinação) | {metrics['r2']:.4f} |
| RMSE (Raiz do Erro Quadrático Médio) | {metrics['rmse']:.2f} |
| MAE (Erro Médio Absoluto) | {metrics['mae']:.2f} |
| MAPE (Erro Percentual Absoluto Médio) | {metrics['mape']:.2f}% |
| Erro Máximo | {metrics['max_error']:.2f} |
| Mediana do Erro Absoluto | {metrics['median_ae']:.2f} |

### Interpretação

- **R² = {metrics['r2']:.4f}**: O modelo explica {metrics['r2']*100:.1f}% da variância dos dados
- **RMSE = {metrics['rmse']:.2f}**: Desvio médio das predições em relação aos valores reais
- **MAPE = {metrics['mape']:.2f}%**: Erro percentual médio das predições

### Diagnóstico

"""
        # Diagnóstico baseado nas métricas
        if metrics['r2'] >= 0.9:
            report += "- ✅ Excelente poder explicativo (R² >= 0.9)\n"
        elif metrics['r2'] >= 0.7:
            report += "- ✓ Bom poder explicativo (R² >= 0.7)\n"
        else:
            report += "- ⚠️ Poder explicativo moderado/baixo (R² < 0.7)\n"

        if metrics['mape'] <= 10:
            report += "- ✅ Erro percentual baixo (MAPE <= 10%)\n"
        elif metrics['mape'] <= 20:
            report += "- ✓ Erro percentual aceitável (MAPE <= 20%)\n"
        else:
            report += "- ⚠️ Erro percentual elevado (MAPE > 20%)\n"

        # Feature importance
        if feature_importance is not None:
            report += "\n### Top 10 Features Mais Importantes\n\n"
            report += "| Rank | Feature | Importância |\n"
            report += "|------|---------|-------------|\n"
            for i, row in feature_importance.head(10).iterrows():
                report += f"| {i+1} | {row['feature']} | {row['importance']:.4f} |\n"

        report += f"\n---\n*Relatório gerado automaticamente*\n"

        # Salvar relatório
        report_path = self.output_dir / f"report_{model_name}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Relatório salvo: {report_path}")

        return report
