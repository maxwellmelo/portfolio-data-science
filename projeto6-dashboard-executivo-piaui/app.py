"""
Dashboard Executivo - Indicadores Socioeconomicos do Piaui
===========================================================
Aplicacao Dash para visualizacao interativa de dados governamentais
do Estado do Piaui, desenvolvida para apoiar tomada de decisao em
politicas publicas.

Autor: Maxwell Melo - Especialista em Dados
Portfolio: https://maxwellmelo.github.io/portfolio-data-science/
"""

import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Importar modulos do projeto
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from data.load_data import carregar_dados_completos
from components.charts import (
    criar_kpi_cards,
    grafico_top_municipios_pib,
    grafico_distribuicao_mesorregiao,
    grafico_scatter_pib_populacao,
    grafico_evolucao_pib,
    grafico_ranking_municipio,
    grafico_mapa_calor_indicadores,
    grafico_tabela_municipios,
    grafico_comparativo_regioes,
    CORES
)

# ============================================================
# CARREGAR DADOS
# ============================================================
print("Carregando dados...")
DADOS = carregar_dados_completos()
DF_CONSOLIDADO = DADOS['consolidado']
DF_PIB = DADOS['pib']
DF_POPULACAO = DADOS['populacao']

# ============================================================
# INICIALIZAR APP
# ============================================================
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
app.title = "Dashboard Piaui - Indicadores Socioeconomicos"
server = app.server

# ============================================================
# ESTILOS
# ============================================================
ESTILO_HEADER = {
    'backgroundColor': CORES['primaria'],
    'padding': '20px',
    'marginBottom': '20px',
    'borderRadius': '0 0 10px 10px',
    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
}

ESTILO_CARD_KPI = {
    'textAlign': 'center',
    'padding': '20px',
    'borderRadius': '10px',
    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
    'backgroundColor': 'white',
    'height': '100%'
}

ESTILO_CARD_GRAFICO = {
    'padding': '15px',
    'borderRadius': '10px',
    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
    'backgroundColor': 'white',
    'marginBottom': '20px'
}

# ============================================================
# COMPONENTES
# ============================================================

def criar_header():
    """Header do dashboard."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H1("Dashboard Executivo",
                       style={'color': 'white', 'marginBottom': '5px', 'fontWeight': 'bold'}),
                html.H4("Indicadores Socioeconomicos do Piaui",
                       style={'color': CORES['secundaria'], 'marginBottom': '10px'}),
                html.P("Dados oficiais do IBGE para apoio a decisao em politicas publicas",
                      style={'color': '#ecf0f1', 'marginBottom': '0'})
            ], width=8),
            dbc.Col([
                html.Div([
                    html.Img(src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Bandeira_do_Piau%C3%AD.svg/200px-Bandeira_do_Piau%C3%AD.svg.png",
                            style={'height': '80px', 'marginRight': '15px'}),
                ], style={'textAlign': 'right'})
            ], width=4)
        ])
    ], style=ESTILO_HEADER)


def criar_kpis():
    """Cards de KPIs principais."""
    kpis = criar_kpi_cards(DF_CONSOLIDADO)

    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2(f"{kpis['populacao_total']:,}".replace(',', '.'),
                           style={'color': CORES['primaria'], 'fontWeight': 'bold'}),
                    html.P("Populacao Total", style={'color': CORES['neutro_escuro'], 'marginBottom': 0})
                ])
            ], style=ESTILO_CARD_KPI)
        ], width=3, className='mb-3'),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2(f"R$ {kpis['pib_total']:.1f} bi",
                           style={'color': CORES['primaria'], 'fontWeight': 'bold'}),
                    html.P("PIB Total (2021)", style={'color': CORES['neutro_escuro'], 'marginBottom': 0})
                ])
            ], style=ESTILO_CARD_KPI)
        ], width=3, className='mb-3'),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2(f"R$ {kpis['pib_per_capita_medio']:,.0f}".replace(',', '.'),
                           style={'color': CORES['primaria'], 'fontWeight': 'bold'}),
                    html.P("PIB per Capita Medio", style={'color': CORES['neutro_escuro'], 'marginBottom': 0})
                ])
            ], style=ESTILO_CARD_KPI)
        ], width=3, className='mb-3'),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2(f"{kpis['num_municipios']}",
                           style={'color': CORES['primaria'], 'fontWeight': 'bold'}),
                    html.P("Municipios", style={'color': CORES['neutro_escuro'], 'marginBottom': 0})
                ])
            ], style=ESTILO_CARD_KPI)
        ], width=3, className='mb-3'),
    ], className='mb-4')


def criar_filtros():
    """Filtros interativos."""
    mesorregioes = ['Todas'] + sorted(DF_CONSOLIDADO['mesorregiao_nome'].unique().tolist())

    return dbc.Card([
        dbc.CardBody([
            html.H5("Filtros", style={'color': CORES['primaria'], 'marginBottom': '15px'}),
            dbc.Row([
                dbc.Col([
                    html.Label("Mesorregiao:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='filtro-mesorregiao',
                        options=[{'label': m, 'value': m} for m in mesorregioes],
                        value='Todas',
                        clearable=False,
                        style={'marginBottom': '10px'}
                    )
                ], width=4),
                dbc.Col([
                    html.Label("Faixa de Populacao:", style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='filtro-populacao',
                        min=0,
                        max=900000,
                        step=10000,
                        value=[0, 900000],
                        marks={
                            0: '0',
                            100000: '100k',
                            500000: '500k',
                            900000: '900k'
                        },
                        tooltip={'placement': 'bottom', 'always_visible': False}
                    )
                ], width=5),
                dbc.Col([
                    html.Label("Acoes:", style={'fontWeight': 'bold'}),
                    html.Br(),
                    dbc.Button("Exportar CSV", id='btn-exportar', color='success', size='sm',
                              style={'marginRight': '10px'}),
                    dcc.Download(id='download-csv')
                ], width=3)
            ])
        ])
    ], style={'marginBottom': '20px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'})


def criar_pagina_visao_geral():
    """Pagina 1: Visao Geral do Estado."""
    return html.Div([
        criar_kpis(),
        criar_filtros(),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-top-pib',
                            figure=grafico_top_municipios_pib(DF_CONSOLIDADO)
                        )
                    ])
                ], style=ESTILO_CARD_GRAFICO)
            ], width=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-mesorregiao',
                            figure=grafico_distribuicao_mesorregiao(DF_CONSOLIDADO)
                        )
                    ])
                ], style=ESTILO_CARD_GRAFICO)
            ], width=6),
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-evolucao',
                            figure=grafico_evolucao_pib(DF_PIB)
                        )
                    ])
                ], style=ESTILO_CARD_GRAFICO)
            ], width=12),
        ])
    ])


def criar_pagina_multissetorial():
    """Pagina 2: Analise Multissetorial."""
    return html.Div([
        html.H4("Analise Multissetorial", style={'color': CORES['primaria'], 'marginBottom': '20px'}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-scatter',
                            figure=grafico_scatter_pib_populacao(DF_CONSOLIDADO)
                        )
                    ])
                ], style=ESTILO_CARD_GRAFICO)
            ], width=7),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-correlacao',
                            figure=grafico_mapa_calor_indicadores(DF_CONSOLIDADO)
                        )
                    ])
                ], style=ESTILO_CARD_GRAFICO)
            ], width=5),
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-comparativo',
                            figure=grafico_comparativo_regioes(DF_CONSOLIDADO)
                        )
                    ])
                ], style=ESTILO_CARD_GRAFICO)
            ], width=12),
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-tabela',
                            figure=grafico_tabela_municipios(DF_CONSOLIDADO)
                        )
                    ])
                ], style=ESTILO_CARD_GRAFICO)
            ], width=12),
        ])
    ])


def criar_pagina_municipal():
    """Pagina 3: Foco Municipal."""
    municipios_opcoes = [
        {'label': row['municipio_nome'], 'value': row['municipio_id']}
        for _, row in DF_CONSOLIDADO.sort_values('municipio_nome').iterrows()
    ]

    return html.Div([
        html.H4("Analise Municipal", style={'color': CORES['primaria'], 'marginBottom': '20px'}),

        dbc.Row([
            dbc.Col([
                html.Label("Selecione o Municipio:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='filtro-municipio',
                    options=municipios_opcoes,
                    value=2211001,  # Teresina
                    clearable=False
                )
            ], width=4)
        ], className='mb-4'),

        html.Div(id='conteudo-municipal')
    ])


def criar_sidebar():
    """Sidebar de navegacao."""
    return html.Div([
        dbc.Nav([
            dbc.NavLink([
                html.I(className="fas fa-chart-pie me-2"),
                "Visao Geral"
            ], href="/", active="exact", style={'color': 'white'}),

            dbc.NavLink([
                html.I(className="fas fa-chart-bar me-2"),
                "Multissetorial"
            ], href="/multissetorial", active="exact", style={'color': 'white'}),

            dbc.NavLink([
                html.I(className="fas fa-city me-2"),
                "Municipal"
            ], href="/municipal", active="exact", style={'color': 'white'}),
        ], vertical=True, pills=True, className='flex-column')
    ], style={
        'backgroundColor': CORES['neutro_escuro'],
        'padding': '20px',
        'borderRadius': '10px',
        'height': '100%',
        'minHeight': '300px'
    })


# ============================================================
# LAYOUT PRINCIPAL
# ============================================================
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    criar_header(),

    dbc.Container([
        dbc.Row([
            dbc.Col([
                criar_sidebar()
            ], width=2, className='d-none d-lg-block'),

            dbc.Col([
                html.Div(id='conteudo-pagina')
            ], width=12, lg=10)
        ])
    ], fluid=True),

    # Footer
    html.Footer([
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.P([
                    "Fonte: IBGE - Sistema SIDRA | ",
                    html.A("Projeto Pilares II", href="#", style={'color': CORES['primaria']}),
                    " | Desenvolvido por ",
                    html.A("Maxwell Melo", href="https://maxwellmelo.github.io/portfolio-data-science/",
                          target="_blank", style={'color': CORES['primaria']})
                ], style={'textAlign': 'center', 'color': CORES['neutro_escuro'], 'fontSize': '0.9rem'})
            ])
        ])
    ], style={'padding': '20px', 'marginTop': '30px'})
])


# ============================================================
# CALLBACKS
# ============================================================

@callback(
    Output('conteudo-pagina', 'children'),
    Input('url', 'pathname')
)
def renderizar_pagina(pathname):
    """Renderiza pagina baseado na URL."""
    if pathname == '/multissetorial':
        return criar_pagina_multissetorial()
    elif pathname == '/municipal':
        return criar_pagina_municipal()
    else:
        return criar_pagina_visao_geral()


@callback(
    Output('conteudo-municipal', 'children'),
    Input('filtro-municipio', 'value')
)
def atualizar_pagina_municipal(municipio_id):
    """Atualiza conteudo da pagina municipal."""
    if not municipio_id:
        return html.P("Selecione um municipio")

    mun = DF_CONSOLIDADO[DF_CONSOLIDADO['municipio_id'] == municipio_id]
    if len(mun) == 0:
        return html.P("Municipio nao encontrado")

    mun = mun.iloc[0]

    # Cards do municipio
    cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(mun['municipio_nome'], style={'color': CORES['primaria']}),
                    html.P(mun['mesorregiao_nome'], style={'marginBottom': 0})
                ])
            ], style=ESTILO_CARD_KPI)
        ], width=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{mun['populacao']:,}".replace(',', '.'),
                           style={'color': CORES['primaria']}),
                    html.P("Populacao", style={'marginBottom': 0})
                ])
            ], style=ESTILO_CARD_KPI)
        ], width=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"R$ {mun['pib_mil_reais']/1000:.1f} M",
                           style={'color': CORES['primaria']}),
                    html.P("PIB (Milhoes)", style={'marginBottom': 0})
                ])
            ], style=ESTILO_CARD_KPI)
        ], width=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"R$ {mun['pib_per_capita']:,.0f}".replace(',', '.'),
                           style={'color': CORES['primaria']}),
                    html.P("PIB per Capita", style={'marginBottom': 0})
                ])
            ], style=ESTILO_CARD_KPI)
        ], width=3),
    ], className='mb-4')

    # Grafico comparativo
    grafico = dbc.Card([
        dbc.CardBody([
            dcc.Graph(
                figure=grafico_ranking_municipio(DF_CONSOLIDADO, municipio_id)
            )
        ])
    ], style=ESTILO_CARD_GRAFICO)

    # Ranking na mesorregiao
    meso = mun['mesorregiao_nome']
    df_meso = DF_CONSOLIDADO[DF_CONSOLIDADO['mesorregiao_nome'] == meso].sort_values('pib_mil_reais', ascending=False)
    ranking = df_meso['municipio_id'].tolist().index(municipio_id) + 1

    info_ranking = dbc.Alert([
        html.Strong(f"Ranking na {meso}: "),
        f"{ranking}o lugar de {len(df_meso)} municipios (por PIB)"
    ], color='info')

    return html.Div([cards, info_ranking, grafico])


@callback(
    [Output('grafico-top-pib', 'figure'),
     Output('grafico-mesorregiao', 'figure')],
    [Input('filtro-mesorregiao', 'value'),
     Input('filtro-populacao', 'value')]
)
def atualizar_graficos_filtrados(mesorregiao, faixa_pop):
    """Atualiza graficos baseado nos filtros."""
    df_filtrado = DF_CONSOLIDADO.copy()

    if mesorregiao and mesorregiao != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['mesorregiao_nome'] == mesorregiao]

    if faixa_pop:
        df_filtrado = df_filtrado[
            (df_filtrado['populacao'] >= faixa_pop[0]) &
            (df_filtrado['populacao'] <= faixa_pop[1])
        ]

    return (
        grafico_top_municipios_pib(df_filtrado),
        grafico_distribuicao_mesorregiao(df_filtrado)
    )


@callback(
    Output('download-csv', 'data'),
    Input('btn-exportar', 'n_clicks'),
    prevent_initial_call=True
)
def exportar_dados(n_clicks):
    """Exporta dados para CSV."""
    return dcc.send_data_frame(
        DF_CONSOLIDADO.to_csv,
        "dados_piaui.csv",
        index=False
    )


# ============================================================
# EXECUTAR
# ============================================================
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("DASHBOARD EXECUTIVO - PIAUI")
    print("=" * 60)
    print("Acesse: http://localhost:8050")
    print("=" * 60 + "\n")

    app.run_server(debug=True, host='0.0.0.0', port=8050)
