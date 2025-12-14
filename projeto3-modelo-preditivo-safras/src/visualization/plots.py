"""
Visualizações para análise de dados agrícolas.
"""

from typing import Optional, List
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns


class AgricultureVisualizer:
    """
    Visualizador para dados de produção agrícola.

    Gera gráficos interativos para:
    - Séries temporais de produção
    - Comparações entre culturas e estados
    - Mapas de produtividade
    - Análises de tendências
    """

    # Paleta de cores para culturas
    COLORS_CULTURAS = {
        "Soja (em grão)": "#2E8B57",
        "Milho (em grão)": "#FFD700",
        "Arroz (em casca)": "#DEB887",
        "Feijão (em grão)": "#8B4513",
        "Cana-de-açúcar": "#228B22",
        "Café (em grão) Total": "#4A2C2A",
        "Algodão herbáceo (em caroço)": "#F5F5F5",
        "Mandioca": "#D2691E"
    }

    def __init__(self):
        """Inicializa o visualizador."""
        plt.style.use("seaborn-v0_8-whitegrid")

    def plot_producao_temporal(
        self,
        df: pd.DataFrame,
        cultura: Optional[str] = None,
        estado: Optional[str] = None,
        metric: str = "producao_ton"
    ) -> go.Figure:
        """
        Gráfico de série temporal de produção.

        Args:
            df: DataFrame com dados
            cultura: Filtrar por cultura
            estado: Filtrar por estado
            metric: Métrica a visualizar

        Returns:
            Figura Plotly
        """
        df_plot = df.copy()

        if cultura:
            df_plot = df_plot[df_plot["cultura"] == cultura]
        if estado:
            df_plot = df_plot[df_plot["estado"] == estado]

        # Agregar por ano
        agg_df = df_plot.groupby("ano")[metric].sum().reset_index()

        titulo = f"Evolução da {metric.replace('_', ' ').title()}"
        if cultura:
            titulo += f" - {cultura}"
        if estado:
            titulo += f" ({estado})"

        fig = px.area(
            agg_df,
            x="ano",
            y=metric,
            title=titulo,
            labels={"ano": "Ano", metric: metric.replace("_", " ").title()}
        )

        fig.update_traces(
            line=dict(width=2),
            fillcolor="rgba(46, 139, 87, 0.3)"
        )

        return fig

    def plot_comparacao_culturas(
        self,
        df: pd.DataFrame,
        ano: int,
        metric: str = "producao_ton",
        top_n: int = 10
    ) -> go.Figure:
        """
        Gráfico de barras comparando culturas.

        Args:
            df: DataFrame com dados
            ano: Ano para comparação
            metric: Métrica a visualizar
            top_n: Número de culturas a mostrar

        Returns:
            Figura Plotly
        """
        df_ano = df[df["ano"] == ano]

        agg_df = df_ano.groupby("cultura")[metric].sum().reset_index()
        agg_df = agg_df.nlargest(top_n, metric)

        fig = px.bar(
            agg_df,
            x="cultura",
            y=metric,
            title=f"Top {top_n} Culturas por {metric.replace('_', ' ').title()} ({ano})",
            labels={"cultura": "Cultura", metric: metric.replace("_", " ").title()},
            color="cultura",
            color_discrete_map=self.COLORS_CULTURAS
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False
        )

        return fig

    def plot_comparacao_estados(
        self,
        df: pd.DataFrame,
        cultura: str,
        ano: int,
        metric: str = "rendimento_kg_ha"
    ) -> go.Figure:
        """
        Gráfico de barras comparando estados.

        Args:
            df: DataFrame com dados
            cultura: Cultura para comparar
            ano: Ano
            metric: Métrica

        Returns:
            Figura Plotly
        """
        df_filtered = df[(df["cultura"] == cultura) & (df["ano"] == ano)]

        agg_df = df_filtered.groupby("estado")[metric].mean().reset_index()
        agg_df = agg_df.sort_values(metric, ascending=True)

        fig = px.bar(
            agg_df,
            x=metric,
            y="estado",
            orientation="h",
            title=f"{metric.replace('_', ' ').title()} por Estado - {cultura} ({ano})",
            labels={"estado": "Estado", metric: metric.replace("_", " ").title()},
            color=metric,
            color_continuous_scale="Viridis"
        )

        fig.update_layout(height=max(400, len(agg_df) * 25))

        return fig

    def plot_evolucao_culturas(
        self,
        df: pd.DataFrame,
        culturas: List[str],
        metric: str = "rendimento_kg_ha"
    ) -> go.Figure:
        """
        Gráfico de linhas comparando evolução de múltiplas culturas.

        Args:
            df: DataFrame com dados
            culturas: Lista de culturas
            metric: Métrica

        Returns:
            Figura Plotly
        """
        df_filtered = df[df["cultura"].isin(culturas)]

        agg_df = df_filtered.groupby(["ano", "cultura"])[metric].mean().reset_index()

        fig = px.line(
            agg_df,
            x="ano",
            y=metric,
            color="cultura",
            title=f"Evolução do {metric.replace('_', ' ').title()} por Cultura",
            labels={"ano": "Ano", metric: metric.replace("_", " ").title(), "cultura": "Cultura"},
            color_discrete_map=self.COLORS_CULTURAS,
            markers=True
        )

        fig.update_traces(line=dict(width=2))

        return fig

    def plot_heatmap_estado_ano(
        self,
        df: pd.DataFrame,
        cultura: str,
        metric: str = "rendimento_kg_ha"
    ) -> go.Figure:
        """
        Heatmap de métrica por estado e ano.

        Args:
            df: DataFrame
            cultura: Cultura
            metric: Métrica

        Returns:
            Figura Plotly
        """
        df_filtered = df[df["cultura"] == cultura]

        pivot = df_filtered.pivot_table(
            values=metric,
            index="estado",
            columns="ano",
            aggfunc="mean"
        )

        # Ordenar por média
        pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

        fig = px.imshow(
            pivot,
            title=f"Heatmap: {metric.replace('_', ' ').title()} - {cultura}",
            labels={"x": "Ano", "y": "Estado", "color": metric.replace("_", " ").title()},
            color_continuous_scale="YlOrRd",
            aspect="auto"
        )

        fig.update_layout(height=max(400, len(pivot) * 20))

        return fig

    def plot_distribuicao_rendimento(
        self,
        df: pd.DataFrame,
        cultura: str,
        ano: Optional[int] = None
    ) -> go.Figure:
        """
        Distribuição do rendimento de uma cultura.

        Args:
            df: DataFrame
            cultura: Cultura
            ano: Ano (None = todos)

        Returns:
            Figura Plotly
        """
        df_filtered = df[df["cultura"] == cultura]
        if ano:
            df_filtered = df_filtered[df_filtered["ano"] == ano]

        titulo = f"Distribuição do Rendimento - {cultura}"
        if ano:
            titulo += f" ({ano})"

        fig = make_subplots(rows=1, cols=2, subplot_titles=("Histograma", "Box Plot"))

        # Histograma
        fig.add_trace(
            go.Histogram(
                x=df_filtered["rendimento_kg_ha"],
                nbinsx=30,
                name="Frequência",
                marker_color="steelblue"
            ),
            row=1, col=1
        )

        # Box plot
        fig.add_trace(
            go.Box(
                y=df_filtered["rendimento_kg_ha"],
                name="Distribuição",
                marker_color="steelblue",
                boxpoints="outliers"
            ),
            row=1, col=2
        )

        fig.update_layout(
            title=titulo,
            showlegend=False,
            height=400
        )

        return fig

    def plot_correlacao(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None
    ) -> go.Figure:
        """
        Matriz de correlação.

        Args:
            df: DataFrame
            columns: Colunas para incluir

        Returns:
            Figura Plotly
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        corr = df[columns].corr()

        fig = px.imshow(
            corr,
            title="Matriz de Correlação",
            labels={"color": "Correlação"},
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            text_auto=".2f"
        )

        fig.update_layout(
            width=max(600, len(columns) * 50),
            height=max(600, len(columns) * 50)
        )

        return fig

    def plot_scatter_matrix(
        self,
        df: pd.DataFrame,
        columns: List[str],
        color_by: Optional[str] = None
    ) -> go.Figure:
        """
        Matriz de dispersão.

        Args:
            df: DataFrame
            columns: Colunas para incluir
            color_by: Coluna para colorir

        Returns:
            Figura Plotly
        """
        fig = px.scatter_matrix(
            df,
            dimensions=columns,
            color=color_by,
            title="Matriz de Dispersão",
            opacity=0.6
        )

        fig.update_layout(
            width=1000,
            height=1000
        )

        return fig

    def create_dashboard_summary(
        self,
        df: pd.DataFrame,
        cultura: str,
        estado: str
    ) -> go.Figure:
        """
        Dashboard resumo com múltiplos gráficos.

        Args:
            df: DataFrame
            cultura: Cultura foco
            estado: Estado foco

        Returns:
            Figura Plotly
        """
        df_filtered = df[(df["cultura"] == cultura) & (df["estado"] == estado)]

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                f"Evolução do Rendimento - {cultura} ({estado})",
                "Área Plantada vs Produção",
                "Distribuição do Rendimento",
                "Tendência com Média Móvel"
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "histogram"}, {"type": "scatter"}]
            ]
        )

        # 1. Evolução temporal
        agg_ano = df_filtered.groupby("ano")["rendimento_kg_ha"].mean().reset_index()
        fig.add_trace(
            go.Scatter(
                x=agg_ano["ano"],
                y=agg_ano["rendimento_kg_ha"],
                mode="lines+markers",
                name="Rendimento",
                line=dict(color="green")
            ),
            row=1, col=1
        )

        # 2. Área vs Produção
        fig.add_trace(
            go.Scatter(
                x=df_filtered["area_plantada_ha"],
                y=df_filtered["producao_ton"],
                mode="markers",
                name="Área x Produção",
                marker=dict(
                    size=8,
                    color=df_filtered["ano"],
                    colorscale="Viridis",
                    showscale=True
                )
            ),
            row=1, col=2
        )

        # 3. Histograma
        fig.add_trace(
            go.Histogram(
                x=df_filtered["rendimento_kg_ha"],
                nbinsx=20,
                name="Frequência",
                marker_color="steelblue"
            ),
            row=2, col=1
        )

        # 4. Tendência
        agg_ano["ma3"] = agg_ano["rendimento_kg_ha"].rolling(3).mean()
        fig.add_trace(
            go.Scatter(
                x=agg_ano["ano"],
                y=agg_ano["rendimento_kg_ha"],
                mode="markers",
                name="Real",
                marker=dict(color="blue")
            ),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(
                x=agg_ano["ano"],
                y=agg_ano["ma3"],
                mode="lines",
                name="MA(3)",
                line=dict(color="red", width=2)
            ),
            row=2, col=2
        )

        fig.update_layout(
            title=f"Dashboard: {cultura} - {estado}",
            height=800,
            showlegend=True
        )

        return fig
