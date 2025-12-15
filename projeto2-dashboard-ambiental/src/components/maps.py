"""
Componentes de mapas interativos para o Dashboard Ambiental
"""

import folium
from folium import plugins
import pandas as pd
import geopandas as gpd
from typing import Optional, Dict, List
import json
import sys
from pathlib import Path

# Adicionar src ao path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import MAP_CONFIG


class MapBuilder:
    """Construtor de mapas interativos com Folium"""

    # Coordenadas centrais do Brasil e estados
    COORDINATES = {
        "Brasil": [-14.2350, -51.9253],
        "PI": [-7.7183, -42.7289],
        "MA": [-4.9609, -45.2744],
        "TO": [-10.1753, -48.2982],
        "GO": [-15.8270, -49.8362],
        "MT": [-12.6819, -56.9211],
        "MS": [-20.7722, -54.7852],
        "BA": [-12.5797, -41.7007],
        "MG": [-18.5122, -44.5550]
    }

    def __init__(self):
        self.default_zoom = MAP_CONFIG["zoom_brazil"]
        self.center_brasil = self.COORDINATES["Brasil"]

    def create_choropleth_map(self,
                             df: pd.DataFrame,
                             value_col: str,
                             title: str,
                             center: Optional[List[float]] = None,
                             zoom: int = 4) -> folium.Map:
        """
        Cria mapa coroplético por estado

        Args:
            df: DataFrame com dados por estado
            value_col: Coluna com valores para colorir
            title: Título do mapa
            center: Coordenadas centrais [lat, lon]
            zoom: Nível de zoom inicial

        Returns:
            Mapa Folium
        """
        if center is None:
            center = self.center_brasil

        # Criar mapa base
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )

        # Adicionar título
        title_html = f'''
        <div style="position: fixed;
                    top: 10px; left: 50px; width: 400px; height: 50px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:16px; font-weight: bold; padding: 10px">
            {title}
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        # Criar GeoJSON simplificado para estados brasileiros
        # (Em produção, você usaria um arquivo GeoJSON real dos estados)
        # Por enquanto, vamos adicionar marcadores por estado

        for _, row in df.iterrows():
            estado = row.get('estado', '')
            estado_nome = row.get('estado_nome', estado)
            valor = row[value_col]

            if estado in self.COORDINATES:
                coords = self.COORDINATES[estado]

                # Determinar cor baseado no valor (usando constantes de config)
                if valor > df[value_col].quantile(0.75):
                    color = MAP_CONFIG["color_high"]
                elif valor > df[value_col].quantile(0.5):
                    color = MAP_CONFIG["color_medium_high"]
                elif valor > df[value_col].quantile(0.25):
                    color = MAP_CONFIG["color_medium_low"]
                else:
                    color = MAP_CONFIG["color_low"]

                # Adicionar marcador circular (usando constantes de config)
                radius = (MAP_CONFIG["marker_radius_base"] +
                         (valor / df[value_col].max()) * MAP_CONFIG["marker_radius_multiplier"])

                folium.CircleMarker(
                    location=coords,
                    radius=radius,
                    popup=f"<b>{estado_nome}</b><br>{value_col}: {valor:.2f} km²",
                    tooltip=estado_nome,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=MAP_CONFIG["circle_fill_opacity"]
                ).add_to(m)

        # Adicionar legenda
        legend_html = f'''
        <div style="position: fixed;
                    bottom: 50px; right: 50px; width: 200px; height: 150px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:12px; padding: 10px">
            <p><b>Legenda - {value_col}</b></p>
            <p><span style="color:red">●</span> Alto (&gt; 75%)</p>
            <p><span style="color:orange">●</span> Médio-Alto (50-75%)</p>
            <p><span style="color:yellow">●</span> Médio-Baixo (25-50%)</p>
            <p><span style="color:green">●</span> Baixo (&lt; 25%)</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))

        return m

    def create_heat_map(self,
                       df: pd.DataFrame,
                       title: str,
                       center: Optional[List[float]] = None,
                       zoom: int = 4) -> folium.Map:
        """
        Cria mapa de calor

        Args:
            df: DataFrame com colunas 'latitude', 'longitude', 'intensity'
            title: Título do mapa
            center: Coordenadas centrais
            zoom: Nível de zoom

        Returns:
            Mapa Folium
        """
        if center is None:
            center = self.center_brasil

        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='CartoDB positron'
        )

        # Preparar dados para heatmap
        heat_data = []
        for estado, coords in self.COORDINATES.items():
            if estado != "Brasil":
                estado_data = df[df['estado'] == estado]
                if len(estado_data) > 0:
                    intensity = estado_data['area_desmatada_km2'].sum()
                    heat_data.append([coords[0], coords[1], intensity])

        # Adicionar camada de calor (usando constantes de config)
        if heat_data:
            plugins.HeatMap(
                heat_data,
                radius=MAP_CONFIG["heatmap_radius"],
                blur=MAP_CONFIG["heatmap_blur"]
            ).add_to(m)

        # Adicionar título
        title_html = f'''
        <div style="position: fixed;
                    top: 10px; left: 50px; width: 400px; height: 50px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:16px; font-weight: bold; padding: 10px">
            {title}
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        return m

    def create_marker_map(self,
                         df: pd.DataFrame,
                         title: str,
                         center: Optional[List[float]] = None,
                         zoom: int = 4) -> folium.Map:
        """
        Cria mapa com marcadores por estado

        Args:
            df: DataFrame com dados por estado
            title: Título do mapa
            center: Coordenadas centrais
            zoom: Nível de zoom

        Returns:
            Mapa Folium
        """
        if center is None:
            center = self.center_brasil

        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )

        # Adicionar marcadores
        for _, row in df.iterrows():
            estado = row.get('estado', '')
            estado_nome = row.get('estado_nome', estado)

            if estado in self.COORDINATES:
                coords = self.COORDINATES[estado]
                valor = row.get('area_desmatada_km2', 0)

                # Criar popup com informações detalhadas
                popup_html = f"""
                <div style="width: 200px">
                    <h4>{estado_nome} ({estado})</h4>
                    <p><b>Desmatamento:</b> {valor:.2f} km²</p>
                </div>
                """

                folium.Marker(
                    location=coords,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=estado_nome,
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)

        # Adicionar título
        title_html = f'''
        <div style="position: fixed;
                    top: 10px; left: 50px; width: 400px; height: 50px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:16px; font-weight: bold; padding: 10px">
            {title}
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        return m

    def create_piaui_focus_map(self,
                               df: pd.DataFrame,
                               title: str = "Foco: Piauí") -> folium.Map:
        """
        Cria mapa focado no Piauí

        Args:
            df: DataFrame com dados do Piauí
            title: Título do mapa

        Returns:
            Mapa Folium
        """
        center = self.COORDINATES["PI"]
        zoom = MAP_CONFIG["zoom_state"]

        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )

        # Adicionar informações do Piauí
        if len(df) > 0:
            total_desmatamento = df['area_desmatada_km2'].sum()
            anos = df['ano'].nunique()

            popup_html = f"""
            <div style="width: 250px">
                <h3>Piauí - Desmatamento</h3>
                <p><b>Total acumulado:</b> {total_desmatamento:.2f} km²</p>
                <p><b>Anos de dados:</b> {anos}</p>
                <p><b>Média anual:</b> {(total_desmatamento/anos if anos > 0 else 0):.2f} km²</p>
            </div>
            """

            folium.Marker(
                location=center,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip="Piauí",
                icon=folium.Icon(color='green', icon='tree', prefix='fa')
            ).add_to(m)

        # Adicionar título
        title_html = f'''
        <div style="position: fixed;
                    top: 10px; left: 50px; width: 300px; height: 50px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:16px; font-weight: bold; padding: 10px">
            🌳 {title}
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        return m

    def create_biome_comparison_map(self,
                                   df: pd.DataFrame,
                                   bioma: str,
                                   title: str) -> folium.Map:
        """
        Cria mapa comparativo de um bioma específico

        Args:
            df: DataFrame com dados do bioma
            bioma: Nome do bioma
            title: Título do mapa

        Returns:
            Mapa Folium
        """
        m = folium.Map(
            location=self.center_brasil,
            zoom_start=4,
            tiles='OpenStreetMap'
        )

        # Filtrar dados do bioma
        df_bioma = df[df['bioma'] == bioma].copy()

        # Agrupar por estado
        df_grouped = df_bioma.groupby(['estado', 'estado_nome']).agg({
            'area_desmatada_km2': 'sum'
        }).reset_index()

        # Adicionar marcadores
        for _, row in df_grouped.iterrows():
            estado = row['estado']
            estado_nome = row['estado_nome']
            valor = row['area_desmatada_km2']

            if estado in self.COORDINATES:
                coords = self.COORDINATES[estado]

                # Tamanho do círculo proporcional ao desmatamento (usando constantes)
                radius = (MAP_CONFIG["marker_radius_base"] +
                         (valor / df_grouped['area_desmatada_km2'].max()) * MAP_CONFIG["marker_size_max"])

                folium.CircleMarker(
                    location=coords,
                    radius=radius,
                    popup=f"<b>{estado_nome}</b><br>Desmatamento: {valor:.2f} km²",
                    tooltip=estado_nome,
                    color=MAP_CONFIG["color_darkred"],
                    fill=True,
                    fillColor=MAP_CONFIG["color_high"],
                    fillOpacity=MAP_CONFIG["circle_fill_opacity"]
                ).add_to(m)

        # Adicionar título
        title_html = f'''
        <div style="position: fixed;
                    top: 10px; left: 50px; width: 400px; height: 50px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:16px; font-weight: bold; padding: 10px">
            {title}
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        return m
