"""
Componentes de visualização para o Dashboard Ambiental
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List, Dict
import numpy as np


class ChartBuilder:
    """Construtor de gráficos interativos com Plotly"""

    def __init__(self, template: str = "plotly_white"):
        self.template = template
        self.color_palette = [
            '#1f7a1f', '#ff6b6b', '#4ecdc4', '#ffe66d', '#a8e6cf',
            '#95e1d3', '#f38181', '#aa96da', '#fcbad3', '#ffffd2'
        ]

    def create_time_series(self,
                          df: pd.DataFrame,
                          x_col: str,
                          y_col: str,
                          title: str,
                          group_col: Optional[str] = None,
                          height: int = 500) -> go.Figure:
        """
        Cria gráfico de série temporal

        Args:
            df: DataFrame com dados
            x_col: Coluna do eixo X (geralmente ano)
            y_col: Coluna do eixo Y (valor)
            title: Título do gráfico
            group_col: Coluna para agrupar linhas
            height: Altura do gráfico

        Returns:
            Figure do Plotly
        """
        if group_col:
            fig = px.line(
                df,
                x=x_col,
                y=y_col,
                color=group_col,
                title=title,
                template=self.template,
                markers=True,
                color_discrete_sequence=self.color_palette
            )
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='lines+markers',
                name=y_col,
                line=dict(color=self.color_palette[0], width=3),
                marker=dict(size=8)
            ))

            fig.update_layout(
                title=title,
                template=self.template
            )

        fig.update_layout(
            height=height,
            hovermode='x unified',
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    def create_bar_chart(self,
                        df: pd.DataFrame,
                        x_col: str,
                        y_col: str,
                        title: str,
                        orientation: str = 'v',
                        color_col: Optional[str] = None,
                        height: int = 500) -> go.Figure:
        """
        Cria gráfico de barras

        Args:
            df: DataFrame com dados
            x_col: Coluna do eixo X
            y_col: Coluna do eixo Y
            title: Título do gráfico
            orientation: 'v' para vertical, 'h' para horizontal
            color_col: Coluna para colorir barras
            height: Altura do gráfico

        Returns:
            Figure do Plotly
        """
        if color_col:
            fig = px.bar(
                df,
                x=x_col if orientation == 'v' else y_col,
                y=y_col if orientation == 'v' else x_col,
                color=color_col,
                title=title,
                template=self.template,
                orientation=orientation,
                color_discrete_sequence=self.color_palette
            )
        else:
            fig = px.bar(
                df,
                x=x_col if orientation == 'v' else y_col,
                y=y_col if orientation == 'v' else x_col,
                title=title,
                template=self.template,
                orientation=orientation,
                color_discrete_sequence=[self.color_palette[0]]
            )

        fig.update_layout(
            height=height,
            xaxis_title=x_col.replace('_', ' ').title() if orientation == 'v' else y_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title() if orientation == 'v' else x_col.replace('_', ' ').title()
        )

        return fig

    def create_comparison_chart(self,
                               df: pd.DataFrame,
                               title: str,
                               year1: int,
                               year2: int,
                               top_n: int = 10,
                               height: int = 500) -> go.Figure:
        """
        Cria gráfico de comparação entre dois anos

        Args:
            df: DataFrame com dados de comparação
            title: Título do gráfico
            year1: Ano 1
            year2: Ano 2
            top_n: Número de estados a mostrar
            height: Altura do gráfico

        Returns:
            Figure do Plotly
        """
        # Pegar top N estados
        df_top = df.nlargest(top_n, f'ano_{year2}')

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name=str(year1),
            x=df_top['estado_nome'],
            y=df_top[f'ano_{year1}'],
            marker_color=self.color_palette[0]
        ))

        fig.add_trace(go.Bar(
            name=str(year2),
            x=df_top['estado_nome'],
            y=df_top[f'ano_{year2}'],
            marker_color=self.color_palette[1]
        ))

        fig.update_layout(
            title=title,
            template=self.template,
            barmode='group',
            height=height,
            xaxis_title="Estado",
            yaxis_title="Área Desmatada (km²)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    def create_pie_chart(self,
                        df: pd.DataFrame,
                        values_col: str,
                        names_col: str,
                        title: str,
                        height: int = 500) -> go.Figure:
        """
        Cria gráfico de pizza

        Args:
            df: DataFrame com dados
            values_col: Coluna com valores
            names_col: Coluna com nomes
            title: Título do gráfico
            height: Altura do gráfico

        Returns:
            Figure do Plotly
        """
        fig = px.pie(
            df,
            values=values_col,
            names=names_col,
            title=title,
            template=self.template,
            color_discrete_sequence=self.color_palette
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )

        fig.update_layout(height=height)

        return fig

    def create_area_chart(self,
                         df: pd.DataFrame,
                         x_col: str,
                         y_col: str,
                         title: str,
                         group_col: Optional[str] = None,
                         height: int = 500) -> go.Figure:
        """
        Cria gráfico de área empilhada

        Args:
            df: DataFrame com dados
            x_col: Coluna do eixo X
            y_col: Coluna do eixo Y
            title: Título do gráfico
            group_col: Coluna para agrupar áreas
            height: Altura do gráfico

        Returns:
            Figure do Plotly
        """
        if group_col:
            fig = px.area(
                df,
                x=x_col,
                y=y_col,
                color=group_col,
                title=title,
                template=self.template,
                color_discrete_sequence=self.color_palette
            )
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                fill='tozeroy',
                mode='lines',
                line=dict(color=self.color_palette[0])
            ))

            fig.update_layout(title=title, template=self.template)

        fig.update_layout(
            height=height,
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )

        return fig

    def create_heatmap(self,
                      df: pd.DataFrame,
                      x_col: str,
                      y_col: str,
                      z_col: str,
                      title: str,
                      height: int = 500) -> go.Figure:
        """
        Cria mapa de calor

        Args:
            df: DataFrame com dados
            x_col: Coluna do eixo X
            y_col: Coluna do eixo Y
            z_col: Coluna com valores
            title: Título do gráfico
            height: Altura do gráfico

        Returns:
            Figure do Plotly
        """
        # Criar pivot table para o heatmap
        pivot_df = df.pivot_table(
            values=z_col,
            index=y_col,
            columns=x_col,
            aggfunc='sum'
        ).fillna(0)

        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='RdYlGn_r',
            hoverongaps=False
        ))

        fig.update_layout(
            title=title,
            template=self.template,
            height=height,
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )

        return fig

    def create_trend_with_forecast(self,
                                   df: pd.DataFrame,
                                   x_col: str,
                                   y_col: str,
                                   title: str,
                                   forecast_years: int = 3,
                                   height: int = 500) -> go.Figure:
        """
        Cria gráfico de tendência com projeção

        Args:
            df: DataFrame com dados
            x_col: Coluna do eixo X (anos)
            y_col: Coluna do eixo Y (valores)
            title: Título do gráfico
            forecast_years: Número de anos para projetar
            height: Altura do gráfico

        Returns:
            Figure do Plotly
        """
        # Dados históricos
        x = df[x_col].values
        y = df[y_col].values

        # Calcular linha de tendência
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)

        # Criar projeção
        last_year = x[-1]
        future_years = np.arange(last_year + 1, last_year + forecast_years + 1)
        all_years = np.concatenate([x, future_years])
        trend_line = p(all_years)

        fig = go.Figure()

        # Dados reais
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines+markers',
            name='Dados Reais',
            line=dict(color=self.color_palette[0], width=3),
            marker=dict(size=8)
        ))

        # Linha de tendência
        fig.add_trace(go.Scatter(
            x=all_years,
            y=trend_line,
            mode='lines',
            name='Tendência',
            line=dict(color=self.color_palette[1], dash='dash', width=2)
        ))

        # Projeção
        fig.add_trace(go.Scatter(
            x=future_years,
            y=p(future_years),
            mode='markers',
            name='Projeção',
            marker=dict(color=self.color_palette[2], size=10, symbol='diamond')
        ))

        fig.update_layout(
            title=title,
            template=self.template,
            height=height,
            xaxis_title="Ano",
            yaxis_title=y_col.replace('_', ' ').title(),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    def create_gauge_chart(self,
                          value: float,
                          title: str,
                          max_value: float,
                          threshold_good: float,
                          threshold_warning: float,
                          height: int = 400) -> go.Figure:
        """
        Cria gráfico de gauge (medidor)

        Args:
            value: Valor atual
            title: Título do gráfico
            max_value: Valor máximo
            threshold_good: Limite para "bom"
            threshold_warning: Limite para "atenção"
            height: Altura do gráfico

        Returns:
            Figure do Plotly
        """
        # Determinar cor baseado nos thresholds
        if value <= threshold_good:
            color = "#1f7a1f"  # Verde
        elif value <= threshold_warning:
            color = "#ffe66d"  # Amarelo
        else:
            color = "#ff6b6b"  # Vermelho

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title},
            delta={'reference': threshold_good},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, threshold_good], 'color': "lightgray"},
                    {'range': [threshold_good, threshold_warning], 'color': "lightyellow"},
                    {'range': [threshold_warning, max_value], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': threshold_warning
                }
            }
        ))

        fig.update_layout(
            template=self.template,
            height=height
        )

        return fig
