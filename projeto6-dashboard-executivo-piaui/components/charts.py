"""
Componentes de Graficos - Dashboard Executivo Piaui
====================================================
Funcoes para criar visualizacoes Plotly para o dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Paleta de cores do Piaui
CORES = {
    'primaria': '#1e5631',      # Verde (bandeira PI)
    'secundaria': '#f4d03f',    # Amarelo dourado
    'destaque': '#c0392b',      # Vermelho
    'neutro_escuro': '#2c3e50',
    'neutro_claro': '#ecf0f1',
    'gradiente': ['#1e5631', '#27ae60', '#2ecc71', '#82e0aa', '#d5f5e3']
}


def criar_kpi_cards(df: pd.DataFrame) -> dict:
    """
    Calcula KPIs principais do estado.

    Returns:
        Dicionario com valores dos KPIs
    """
    return {
        'populacao_total': df['populacao'].sum(),
        'pib_total': df['pib_mil_reais'].sum() / 1_000_000,  # Em bilhoes
        'pib_per_capita_medio': df['pib_per_capita'].mean(),
        'num_municipios': len(df),
        'maior_cidade': df.loc[df['populacao'].idxmax(), 'municipio_nome'] if len(df) > 0 else '-'
    }


def grafico_top_municipios_pib(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """
    Grafico de barras horizontal dos maiores PIBs.
    """
    df_top = df.nlargest(top_n, 'pib_mil_reais').copy()
    df_top['pib_bilhoes'] = df_top['pib_mil_reais'] / 1_000_000

    fig = px.bar(
        df_top,
        x='pib_bilhoes',
        y='municipio_nome',
        orientation='h',
        color='pib_bilhoes',
        color_continuous_scale=[[0, CORES['neutro_claro']], [1, CORES['primaria']]],
        text=df_top['pib_bilhoes'].apply(lambda x: f'R$ {x:.1f} bi')
    )

    fig.update_layout(
        title={
            'text': f'Top {top_n} Municipios por PIB',
            'x': 0.5,
            'font': {'size': 16, 'color': CORES['neutro_escuro']}
        },
        xaxis_title='PIB (Bilhoes R$)',
        yaxis_title='',
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=False,
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    fig.update_traces(textposition='outside')

    return fig


def grafico_distribuicao_mesorregiao(df: pd.DataFrame) -> go.Figure:
    """
    Grafico de pizza da distribuicao populacional por mesorregiao.
    """
    df_meso = df.groupby('mesorregiao_nome').agg({
        'populacao': 'sum',
        'municipio_id': 'count'
    }).reset_index()
    df_meso.columns = ['mesorregiao', 'populacao', 'num_municipios']

    fig = px.pie(
        df_meso,
        values='populacao',
        names='mesorregiao',
        color_discrete_sequence=[CORES['primaria'], CORES['secundaria'], '#3498db', '#e74c3c'],
        hole=0.4
    )

    fig.update_traces(
        textposition='outside',
        textinfo='label+percent',
        textfont_size=11
    )

    fig.update_layout(
        title={
            'text': 'Populacao por Mesorregiao',
            'x': 0.5,
            'font': {'size': 16, 'color': CORES['neutro_escuro']}
        },
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.2)
    )

    return fig


def grafico_scatter_pib_populacao(df: pd.DataFrame) -> go.Figure:
    """
    Scatter plot PIB x Populacao com tamanho proporcional.
    """
    df_plot = df[df['populacao'] > 0].copy()

    fig = px.scatter(
        df_plot,
        x='populacao',
        y='pib_mil_reais',
        size='pib_per_capita',
        color='mesorregiao_nome',
        hover_name='municipio_nome',
        hover_data={
            'populacao': ':,.0f',
            'pib_mil_reais': ':,.0f',
            'pib_per_capita': ':,.2f',
            'mesorregiao_nome': True
        },
        color_discrete_sequence=[CORES['primaria'], CORES['secundaria'], '#3498db', '#e74c3c'],
        log_x=True,
        log_y=True
    )

    fig.update_layout(
        title={
            'text': 'Relacao PIB x Populacao por Municipio',
            'x': 0.5,
            'font': {'size': 16, 'color': CORES['neutro_escuro']}
        },
        xaxis_title='Populacao (escala log)',
        yaxis_title='PIB em Mil R$ (escala log)',
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.25,
            title=''
        )
    )

    return fig


def grafico_evolucao_pib(df_pib: pd.DataFrame) -> go.Figure:
    """
    Grafico de linha da evolucao do PIB estadual.
    """
    df_evolucao = df_pib.groupby('ano')['pib_mil_reais'].sum().reset_index()
    df_evolucao['pib_bilhoes'] = df_evolucao['pib_mil_reais'] / 1_000_000

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_evolucao['ano'],
        y=df_evolucao['pib_bilhoes'],
        mode='lines+markers+text',
        line=dict(color=CORES['primaria'], width=3),
        marker=dict(size=12, color=CORES['primaria']),
        text=df_evolucao['pib_bilhoes'].apply(lambda x: f'R$ {x:.1f} bi'),
        textposition='top center',
        name='PIB Piaui'
    ))

    fig.update_layout(
        title={
            'text': 'Evolucao do PIB do Piaui',
            'x': 0.5,
            'font': {'size': 16, 'color': CORES['neutro_escuro']}
        },
        xaxis_title='Ano',
        yaxis_title='PIB (Bilhoes R$)',
        height=350,
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(tickmode='array', tickvals=df_evolucao['ano'].tolist())
    )

    return fig


def grafico_ranking_municipio(df: pd.DataFrame, municipio_id: int) -> go.Figure:
    """
    Grafico comparando municipio selecionado com media estadual.
    """
    mun = df[df['municipio_id'] == municipio_id]
    if len(mun) == 0:
        return go.Figure()

    mun = mun.iloc[0]
    media_pop = df['populacao'].mean()
    media_pib = df['pib_per_capita'].mean()

    categorias = ['Populacao', 'PIB per Capita']
    valores_mun = [mun['populacao'], mun['pib_per_capita']]
    valores_media = [media_pop, media_pib]

    # Normalizar para comparacao
    norm_mun = [v / m * 100 if m > 0 else 0 for v, m in zip(valores_mun, valores_media)]
    norm_media = [100, 100]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name=mun['municipio_nome'],
        x=categorias,
        y=norm_mun,
        marker_color=CORES['primaria'],
        text=[f'{v:,.0f}' for v in valores_mun],
        textposition='outside'
    ))

    fig.add_trace(go.Bar(
        name='Media Estadual',
        x=categorias,
        y=norm_media,
        marker_color=CORES['neutro_claro'],
        text=[f'{v:,.0f}' for v in valores_media],
        textposition='outside'
    ))

    fig.update_layout(
        title={
            'text': f'{mun["municipio_nome"]} vs Media Estadual',
            'x': 0.5,
            'font': {'size': 16, 'color': CORES['neutro_escuro']}
        },
        barmode='group',
        yaxis_title='% em relacao a media',
        height=350,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    return fig


def grafico_mapa_calor_indicadores(df: pd.DataFrame) -> go.Figure:
    """
    Heatmap de correlacao entre indicadores.
    """
    cols = ['populacao', 'pib_mil_reais', 'pib_per_capita']
    df_corr = df[cols].corr()

    labels = ['Populacao', 'PIB Total', 'PIB per Capita']

    fig = px.imshow(
        df_corr,
        x=labels,
        y=labels,
        color_continuous_scale='Greens',
        text_auto='.2f',
        zmin=-1,
        zmax=1
    )

    fig.update_layout(
        title={
            'text': 'Correlacao entre Indicadores',
            'x': 0.5,
            'font': {'size': 16, 'color': CORES['neutro_escuro']}
        },
        height=400,
        paper_bgcolor='white'
    )

    return fig


def grafico_tabela_municipios(df: pd.DataFrame) -> go.Figure:
    """
    Tabela interativa com dados dos municipios.
    """
    df_tabela = df[['municipio_nome', 'mesorregiao_nome', 'populacao', 'pib_mil_reais', 'pib_per_capita']].copy()
    df_tabela = df_tabela.sort_values('pib_mil_reais', ascending=False).head(50)

    df_tabela['pib_milhoes'] = (df_tabela['pib_mil_reais'] / 1000).round(1)
    df_tabela['pib_per_capita'] = df_tabela['pib_per_capita'].round(0)
    df_tabela['populacao'] = df_tabela['populacao'].apply(lambda x: f'{x:,}')

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Municipio</b>', '<b>Mesorregiao</b>', '<b>Populacao</b>',
                    '<b>PIB (Milhoes)</b>', '<b>PIB per Capita</b>'],
            fill_color=CORES['primaria'],
            font=dict(color='white', size=12),
            align='left',
            height=35
        ),
        cells=dict(
            values=[
                df_tabela['municipio_nome'],
                df_tabela['mesorregiao_nome'],
                df_tabela['populacao'],
                df_tabela['pib_milhoes'].apply(lambda x: f'R$ {x:,.1f} M'),
                df_tabela['pib_per_capita'].apply(lambda x: f'R$ {x:,.0f}')
            ],
            fill_color=[['white', CORES['neutro_claro']] * 25],
            font=dict(size=11),
            align='left',
            height=28
        )
    )])

    fig.update_layout(
        title={
            'text': 'Dados dos Municipios (Top 50 por PIB)',
            'x': 0.5,
            'font': {'size': 16, 'color': CORES['neutro_escuro']}
        },
        height=600,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


def grafico_comparativo_regioes(df: pd.DataFrame) -> go.Figure:
    """
    Grafico comparativo entre mesorregioes.
    """
    df_meso = df.groupby('mesorregiao_nome').agg({
        'populacao': 'sum',
        'pib_mil_reais': 'sum',
        'pib_per_capita': 'mean',
        'municipio_id': 'count'
    }).reset_index()

    df_meso.columns = ['mesorregiao', 'populacao', 'pib_total', 'pib_per_capita_medio', 'num_municipios']
    df_meso['pib_bilhoes'] = df_meso['pib_total'] / 1_000_000

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('PIB por Mesorregiao (Bilhoes)', 'PIB per Capita Medio'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )

    fig.add_trace(
        go.Bar(
            x=df_meso['mesorregiao'],
            y=df_meso['pib_bilhoes'],
            marker_color=CORES['primaria'],
            text=df_meso['pib_bilhoes'].apply(lambda x: f'R$ {x:.1f}'),
            textposition='outside',
            name='PIB'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=df_meso['mesorregiao'],
            y=df_meso['pib_per_capita_medio'],
            marker_color=CORES['secundaria'],
            text=df_meso['pib_per_capita_medio'].apply(lambda x: f'R$ {x:,.0f}'),
            textposition='outside',
            name='PIB per Capita'
        ),
        row=1, col=2
    )

    fig.update_layout(
        title={
            'text': 'Comparativo entre Mesorregioes do Piaui',
            'x': 0.5,
            'font': {'size': 16, 'color': CORES['neutro_escuro']}
        },
        height=400,
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    fig.update_xaxes(tickangle=45)

    return fig
