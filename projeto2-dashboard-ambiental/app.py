"""
Dashboard Ambiental - Desmatamento no Brasil
Análise interativa de dados do PRODES/INPE com foco no Cerrado e Piauí

Autor: Maxwell
Data: 2025-12-14
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.config import TEXTOS, BIOMAS, ESTADOS_BRASIL, ESTADOS_CERRADO, DADOS_2025_PRELIM
from utils.data_loader import DataLoaderPRODES, get_piaui_data
from utils.data_processor import DataProcessor, create_kpis
from components.charts import ChartBuilder
from components.maps import MapBuilder
from streamlit_folium import st_folium


# Configuração da página
st.set_page_config(
    page_title="Dashboard Ambiental - Desmatamento Brasil",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f7a1f;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f7a1f;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_data():
    """Carrega dados com cache"""
    loader = DataLoaderPRODES()
    df = loader.load_data(use_synthetic=True)
    # Garantir que estado_nome existe
    if 'estado_nome' not in df.columns:
        df['estado_nome'] = df['estado'].map(ESTADOS_BRASIL)
    return df


def main():
    # Header
    st.markdown(f'<div class="main-header">{TEXTOS["titulo"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #666;">{TEXTOS["subtitulo"]}</p>', unsafe_allow_html=True)

    # Aviso sobre dados preliminares
    st.markdown(f'''
    <div class="warning-box">
        {TEXTOS["aviso_dados_preliminares"]}
    </div>
    ''', unsafe_allow_html=True)

    # Sidebar - Filtros
    st.sidebar.title("Filtros")

    # Carregar dados
    with st.spinner("Carregando dados do PRODES/INPE..."):
        df = load_data()

    # Filtros
    anos_disponiveis = sorted(df['ano'].unique())
    biomas_disponiveis = sorted(df['bioma'].unique())
    estados_disponiveis = sorted(df['estado'].unique())

    # Seleção de bioma
    bioma_selecionado = st.sidebar.selectbox(
        "Bioma",
        options=["Todos"] + biomas_disponiveis,
        index=biomas_disponiveis.index("Cerrado") + 1 if "Cerrado" in biomas_disponiveis else 0
    )

    # Seleção de estado
    estado_selecionado = st.sidebar.selectbox(
        "Estado",
        options=["Todos"] + estados_disponiveis,
        index=estados_disponiveis.index("PI") + 1 if "PI" in estados_disponiveis else 0
    )

    # Seleção de período
    ano_inicio, ano_fim = st.sidebar.select_slider(
        "Período",
        options=anos_disponiveis,
        value=(anos_disponiveis[0], anos_disponiveis[-1])
    )

    # Aplicar filtros
    df_filtered = df.copy()

    if bioma_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered['bioma'] == bioma_selecionado]

    if estado_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered['estado'] == estado_selecionado]

    df_filtered = df_filtered[(df_filtered['ano'] >= ano_inicio) & (df_filtered['ano'] <= ano_fim)]

    # Informações do dataset
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Informações do Dataset")
    st.sidebar.metric("Total de Registros", f"{len(df_filtered):,}")
    st.sidebar.metric("Estados", df_filtered['estado'].nunique())
    st.sidebar.metric("Biomas", df_filtered['bioma'].nunique())
    st.sidebar.metric("Anos", df_filtered['ano'].nunique())

    # Botões de exportação
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💾 Exportar Dados")

    # Exportar dados filtrados como CSV
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Baixar Dados (CSV)",
        data=csv_data,
        file_name=f"dados_desmatamento_{ano_inicio}_{ano_fim}.csv",
        mime="text/csv",
        help="Baixar dados filtrados em formato CSV"
    )

    # Criar processador de dados
    processor = DataProcessor(df_filtered)
    chart_builder = ChartBuilder()
    map_builder = MapBuilder()

    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Visão Geral",
        "🗺️ Mapas Interativos",
        "📊 Análises Detalhadas",
        "🌳 Foco: Piauí",
        "ℹ️ Sobre"
    ])

    # TAB 1: Visão Geral
    with tab1:
        st.header("Visão Geral do Desmatamento")

        # KPIs principais
        ano_atual = df_filtered['ano'].max()
        kpis = create_kpis(
            df_filtered,
            ano_atual=ano_atual,
            estado=None if estado_selecionado == "Todos" else estado_selecionado,
            bioma=None if bioma_selecionado == "Todos" else bioma_selecionado
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            delta_color = "inverse" if kpis['variacao_anual_percentual'] < 0 else "normal"
            st.metric(
                "Desmatamento Atual",
                f"{kpis['desmatamento_atual_km2']:,.0f} km²",
                f"{kpis['variacao_anual_percentual']:.1f}%",
                delta_color=delta_color
            )

        with col2:
            st.metric(
                "Ano Anterior",
                f"{kpis['desmatamento_anterior_km2']:,.0f} km²"
            )

        with col3:
            st.metric(
                "Média Histórica",
                f"{kpis['media_historica_km2']:,.0f} km²"
            )

        with col4:
            st.metric(
                "Estados Afetados",
                kpis['num_estados_afetados']
            )

        # Informação de tendência
        if kpis['tendencia']:
            trend_value = kpis['tendencia']['tendencia_anual_km2']
            trend_direction = "📈 Crescente" if trend_value > 0 else "📉 Decrescente"
            st.markdown(f'''
            <div class="info-box">
                <strong>Tendência Histórica:</strong> {trend_direction}
                ({abs(trend_value):,.2f} km²/ano)
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("---")

        # Gráfico de série temporal
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Evolução Temporal do Desmatamento")
            yearly_metrics = processor.calculate_yearly_metrics(
                bioma=None if bioma_selecionado == "Todos" else bioma_selecionado
            )

            fig_timeline = chart_builder.create_trend_with_forecast(
                yearly_metrics,
                x_col='ano',
                y_col='total_km2',
                title="Desmatamento Anual com Projeção",
                forecast_years=3,
                height=400
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

            # Botão para exportar gráfico
            html_chart = fig_timeline.to_html(include_plotlyjs='cdn')
            st.download_button(
                label="💾 Exportar Gráfico (HTML)",
                data=html_chart.encode('utf-8'),
                file_name="evolucao_temporal_desmatamento.html",
                mime="text/html",
                key="download_timeline"
            )

        with col2:
            st.subheader("Distribuição por Bioma")
            biome_metrics = processor.calculate_biome_metrics()

            fig_bioma = chart_builder.create_pie_chart(
                biome_metrics,
                values_col='total_km2',
                names_col='bioma',
                title="",
                height=400
            )
            st.plotly_chart(fig_bioma, use_container_width=True)

            # Botão para exportar gráfico
            html_bioma = fig_bioma.to_html(include_plotlyjs='cdn')
            st.download_button(
                label="💾 Exportar Gráfico (HTML)",
                data=html_bioma.encode('utf-8'),
                file_name="distribuicao_bioma.html",
                mime="text/html",
                key="download_bioma"
            )

        # Ranking de estados
        st.markdown("---")
        st.subheader(f"Top 10 Estados - Desmatamento em {ano_atual}")

        top_states = processor.get_top_states(n=10, ano=ano_atual)

        fig_ranking = chart_builder.create_bar_chart(
            top_states,
            x_col='estado_nome',
            y_col='area_desmatada_km2',
            title="",
            orientation='h',
            height=400
        )
        st.plotly_chart(fig_ranking, use_container_width=True)

    # TAB 2: Mapas Interativos
    with tab2:
        st.header("Mapas Interativos de Desmatamento")

        map_type = st.selectbox(
            "Tipo de Mapa",
            ["Mapa Coroplético", "Mapa de Calor", "Mapa de Marcadores"]
        )

        # Preparar dados para o mapa
        if estado_selecionado == "Todos":
            df_map = processor.calculate_state_metrics(ano=ano_atual)
        else:
            df_map = df_filtered[df_filtered['ano'] == ano_atual].groupby(['estado', 'estado_nome']).agg({
                'area_desmatada_km2': 'sum'
            }).reset_index()

        if map_type == "Mapa Coroplético":
            mapa = map_builder.create_choropleth_map(
                df_map,
                value_col='total_km2' if 'total_km2' in df_map.columns else 'area_desmatada_km2',
                title=f"Desmatamento por Estado - {ano_atual}"
            )
        elif map_type == "Mapa de Calor":
            mapa = map_builder.create_heat_map(
                df_filtered[df_filtered['ano'] == ano_atual],
                title=f"Intensidade de Desmatamento - {ano_atual}"
            )
        else:
            mapa = map_builder.create_marker_map(
                df_map,
                title=f"Desmatamento por Estado - {ano_atual}"
            )

        st_folium(mapa, width=1200, height=600)

        # Comparação de biomas no mapa
        if bioma_selecionado != "Todos":
            st.markdown("---")
            st.subheader(f"Mapa Específico: {bioma_selecionado}")

            mapa_bioma = map_builder.create_biome_comparison_map(
                df_filtered,
                bioma=bioma_selecionado,
                title=f"Desmatamento no {bioma_selecionado}"
            )
            st_folium(mapa_bioma, width=1200, height=500)

    # TAB 3: Análises Detalhadas
    with tab3:
        st.header("Análises Detalhadas")

        # Comparação entre anos
        st.subheader("Comparação Entre Anos")

        col1, col2 = st.columns(2)
        with col1:
            year1 = st.selectbox("Ano 1", anos_disponiveis, index=len(anos_disponiveis)-3 if len(anos_disponiveis) > 2 else 0)
        with col2:
            year2 = st.selectbox("Ano 2", anos_disponiveis, index=len(anos_disponiveis)-1)

        if year1 != year2:
            comparison = processor.create_comparison_matrix(year1, year2)

            fig_comparison = chart_builder.create_comparison_chart(
                comparison,
                title=f"Comparação de Desmatamento: {year1} vs {year2}",
                year1=year1,
                year2=year2,
                top_n=10
            )
            st.plotly_chart(fig_comparison, use_container_width=True)

            # Tabela de comparação
            st.dataframe(
                comparison[['estado_nome', f'ano_{year1}', f'ano_{year2}', 'variacao_absoluta', 'variacao_percentual']]
                .sort_values('variacao_absoluta', ascending=False)
                .head(10)
                .style.format({
                    f'ano_{year1}': '{:.2f}',
                    f'ano_{year2}': '{:.2f}',
                    'variacao_absoluta': '{:.2f}',
                    'variacao_percentual': '{:.2f}%'
                })
                .background_gradient(subset=['variacao_percentual'], cmap='RdYlGn_r'),
                use_container_width=True
            )

        st.markdown("---")

        # Heatmap temporal
        st.subheader("Heatmap Temporal por Estado")

        # Criar pivot para heatmap
        df_pivot = df_filtered.pivot_table(
            values='area_desmatada_km2',
            index='estado',
            columns='ano',
            aggfunc='sum'
        ).fillna(0)

        # Pegar top 15 estados
        top_15_states = df_filtered.groupby('estado')['area_desmatada_km2'].sum().nlargest(15).index
        df_pivot_top = df_pivot.loc[top_15_states]

        fig_heatmap = chart_builder.create_heatmap(
            df_filtered[df_filtered['estado'].isin(top_15_states)],
            x_col='ano',
            y_col='estado',
            z_col='area_desmatada_km2',
            title="Intensidade de Desmatamento ao Longo do Tempo (Top 15 Estados)"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Estatísticas por bioma
        st.markdown("---")
        st.subheader("Estatísticas por Bioma")

        biome_stats = processor.calculate_biome_metrics()
        st.dataframe(
            biome_stats.style.format({
                'total_km2': '{:,.2f}',
                'media_anual_km2': '{:,.2f}',
                'participacao_percentual': '{:.2f}%'
            })
            .background_gradient(subset=['total_km2'], cmap='Reds'),
            use_container_width=True
        )

    # TAB 4: Foco Piauí
    with tab4:
        st.header("🌳 Foco: Piauí")

        # Dados do Piauí
        df_piaui = df[df['estado'] == 'PI'].copy()

        if len(df_piaui) > 0:
            # KPIs do Piauí
            st.subheader("Indicadores do Piauí")

            kpis_pi = create_kpis(df_piaui, ano_atual=ano_atual)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Desmatamento Atual (PI)",
                    f"{kpis_pi['desmatamento_atual_km2']:,.0f} km²",
                    f"{kpis_pi['variacao_anual_percentual']:.1f}%",
                    delta_color="inverse" if kpis_pi['variacao_anual_percentual'] < 0 else "normal"
                )

            with col2:
                st.metric(
                    "Acumulado Histórico",
                    f"{df_piaui['area_desmatada_km2'].sum():,.0f} km²"
                )

            with col3:
                if kpis_pi['tendencia']:
                    st.metric(
                        "Tendência Anual",
                        f"{kpis_pi['tendencia']['tendencia_anual_km2']:.2f} km²/ano"
                    )

            # Informação contextual
            st.markdown(f'''
            <div class="info-box">
                <strong>Dados PRODES 2025 (Preliminares):</strong> O Piauí foi o 3º estado com maior
                desmatamento no Cerrado em 2025, com {DADOS_2025_PRELIM['cerrado']['estados_maiores_desmatadores']['PI']:,} km².
                O Cerrado registrou redução de {DADOS_2025_PRELIM['cerrado']['reducao_percentual']:.2f}% em relação ao ano anterior.
            </div>
            ''', unsafe_allow_html=True)

            st.markdown("---")

            # Série temporal do Piauí
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Evolução Temporal - Piauí")

                processor_pi = DataProcessor(df_piaui)
                yearly_pi = processor_pi.calculate_yearly_metrics()

                fig_pi_timeline = chart_builder.create_time_series(
                    yearly_pi,
                    x_col='ano',
                    y_col='total_km2',
                    title="Desmatamento Anual no Piauí",
                    height=400
                )
                st.plotly_chart(fig_pi_timeline, use_container_width=True)

            with col2:
                st.subheader("Mapa do Piauí")

                mapa_pi = map_builder.create_piaui_focus_map(
                    df_piaui,
                    title="Desmatamento no Piauí"
                )
                st_folium(mapa_pi, width=400, height=400)

            # Comparação PI com outros estados do Cerrado
            st.markdown("---")
            st.subheader("Piauí vs Outros Estados do Cerrado")

            df_cerrado = df[(df['bioma'] == 'Cerrado') & (df['ano'] == ano_atual)]
            df_cerrado_grouped = df_cerrado.groupby(['estado', 'estado_nome']).agg({
                'area_desmatada_km2': 'sum'
            }).reset_index().sort_values('area_desmatada_km2', ascending=False)

            # Destacar Piauí
            df_cerrado_grouped['destaque'] = df_cerrado_grouped['estado'] == 'PI'

            fig_pi_comparison = chart_builder.create_bar_chart(
                df_cerrado_grouped.head(10),
                x_col='estado_nome',
                y_col='area_desmatada_km2',
                title=f"Ranking Cerrado - {ano_atual}",
                color_col='destaque',
                orientation='h',
                height=400
            )
            st.plotly_chart(fig_pi_comparison, use_container_width=True)

            # Tabela detalhada
            st.subheader("Dados Detalhados - Piauí")
            st.dataframe(
                df_piaui[['ano', 'area_desmatada_km2', 'bioma', 'fonte']]
                .sort_values('ano', ascending=False)
                .style.format({'area_desmatada_km2': '{:.2f} km²'})
                .background_gradient(subset=['area_desmatada_km2'], cmap='Reds'),
                use_container_width=True
            )

        else:
            st.warning("Não há dados disponíveis para o Piauí no período selecionado.")

    # TAB 5: Sobre
    with tab5:
        st.header("ℹ️ Sobre o Dashboard")

        st.markdown("""
        ## Dashboard Ambiental - Desmatamento no Brasil

        Este dashboard apresenta análises interativas sobre o desmatamento no Brasil,
        com foco especial no bioma Cerrado e no estado do Piauí.

        ### 📊 Fontes de Dados

        - **PRODES (Programa de Monitoramento do Desmatamento)**: Sistema do INPE que monitora
          o desmatamento nos biomas brasileiros por meio de imagens de satélite.
        - **TerraBrasilis**: Plataforma de dados geográficos do INPE para acesso e análise de
          dados de desmatamento.

        ### 🎯 Objetivos

        1. Visualizar tendências históricas de desmatamento
        2. Comparar dados entre estados e biomas
        3. Identificar padrões e anomalias
        4. Fornecer insights para políticas públicas ambientais

        ### 🔗 Links Úteis

        - [TerraBrasilis](http://terrabrasilis.dpi.inpe.br/)
        - [INPE - Instituto Nacional de Pesquisas Espaciais](https://www.gov.br/inpe/)
        - [Portal de Dados Abertos INPE](https://www.gov.br/inpe/pt-br/acesso-a-informacao/dados-abertos)
        - [Base dos Dados - PRODES](https://basedosdados.org/dataset/e5c87240-ecce-4856-97c5-e6b84984bf42)

        ### 📈 Funcionalidades

        - **Filtros Interativos**: Selecione biomas, estados e períodos específicos
        - **Visualizações Dinâmicas**: Gráficos, mapas e tabelas interativas
        - **KPIs em Tempo Real**: Métricas atualizadas automaticamente
        - **Análises Comparativas**: Compare diferentes períodos e regiões
        - **Foco Regional**: Análise detalhada do Piauí

        ### 🛠️ Tecnologias Utilizadas

        - **Streamlit**: Framework para criação de dashboards interativos
        - **Plotly**: Biblioteca de visualização de dados
        - **Folium**: Mapas interativos
        - **Pandas**: Manipulação e análise de dados
        - **GeoPandas**: Processamento de dados geoespaciais

        ### 📝 Notas Importantes

        - Os dados de 2025 são preliminares e serão consolidados no primeiro semestre de 2026
        - As análises são baseadas em dados oficiais do INPE/PRODES
        - Este dashboard foi desenvolvido para fins educacionais e de pesquisa

        ### 👨‍💻 Desenvolvido por

        Maxwell - Portfólio de Ciência de Dados

        ---

        **Última atualização:** Dezembro 2025
        """)

        # Estatísticas do dataset
        st.markdown("---")
        st.subheader("📊 Estatísticas do Dataset")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de Registros", f"{len(df):,}")
            st.metric("Período Coberto", f"{df['ano'].min()} - {df['ano'].max()}")

        with col2:
            st.metric("Estados Monitorados", df['estado'].nunique())
            st.metric("Biomas Cobertos", df['bioma'].nunique())

        with col3:
            st.metric("Área Total Desmatada", f"{df['area_desmatada_km2'].sum():,.0f} km²")
            st.metric("Média Anual", f"{df.groupby('ano')['area_desmatada_km2'].sum().mean():,.0f} km²")


if __name__ == "__main__":
    main()
