"""
Pipeline ETL para processamento e transformação de dados de desmatamento
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .config import ESTADOS_BRASIL, BIOMAS, PROCESSED_DATA_DIR
from .logger import get_logger

# Configurar logger para este módulo
logger = get_logger(__name__)


class DataProcessor:
    """Processa e transforma dados de desmatamento para análises"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._validate_data()

    def _validate_data(self):
        """Valida estrutura e qualidade dos dados"""
        required_columns = ['ano', 'estado', 'bioma', 'area_desmatada_km2']

        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"Coluna obrigatória '{col}' não encontrada nos dados")

        # Remover valores nulos
        self.df = self.df.dropna(subset=required_columns)

        # Converter tipos
        self.df['ano'] = self.df['ano'].astype(int)
        self.df['area_desmatada_km2'] = pd.to_numeric(self.df['area_desmatada_km2'], errors='coerce')

        # Adicionar nome completo do estado
        self.df['estado_nome'] = self.df['estado'].map(ESTADOS_BRASIL)

    def calculate_yearly_metrics(self, bioma: Optional[str] = None) -> pd.DataFrame:
        """
        Calcula métricas agregadas por ano

        Args:
            bioma: Filtrar por bioma específico

        Returns:
            DataFrame com métricas anuais
        """
        df_filtered = self.df.copy()

        if bioma:
            df_filtered = df_filtered[df_filtered['bioma'] == bioma]

        yearly = df_filtered.groupby('ano').agg({
            'area_desmatada_km2': ['sum', 'mean', 'std', 'min', 'max', 'count']
        }).round(2)

        yearly.columns = ['total_km2', 'media_km2', 'desvio_padrao', 'minimo', 'maximo', 'num_registros']
        yearly = yearly.reset_index()

        # Calcular variação percentual anual
        yearly['variacao_percentual'] = yearly['total_km2'].pct_change() * 100
        yearly['variacao_absoluta'] = yearly['total_km2'].diff()

        # Calcular média móvel de 3 anos
        yearly['media_movel_3anos'] = yearly['total_km2'].rolling(window=3, min_periods=1).mean()

        return yearly

    def calculate_state_metrics(self, ano: Optional[int] = None) -> pd.DataFrame:
        """
        Calcula métricas agregadas por estado

        Args:
            ano: Filtrar por ano específico

        Returns:
            DataFrame com métricas por estado
        """
        df_filtered = self.df.copy()

        if ano:
            df_filtered = df_filtered[df_filtered['ano'] == ano]

        state_metrics = df_filtered.groupby(['estado', 'estado_nome', 'bioma']).agg({
            'area_desmatada_km2': ['sum', 'mean', 'count']
        }).round(2)

        state_metrics.columns = ['total_km2', 'media_km2', 'num_registros']
        state_metrics = state_metrics.reset_index()

        # Calcular participação percentual
        total_geral = state_metrics['total_km2'].sum()
        state_metrics['participacao_percentual'] = (state_metrics['total_km2'] / total_geral * 100).round(2)

        # Ordenar por total desmatado
        state_metrics = state_metrics.sort_values('total_km2', ascending=False)

        return state_metrics

    def calculate_biome_metrics(self) -> pd.DataFrame:
        """
        Calcula métricas agregadas por bioma

        Returns:
            DataFrame com métricas por bioma
        """
        biome_metrics = self.df.groupby('bioma').agg({
            'area_desmatada_km2': ['sum', 'mean', 'count'],
            'ano': ['min', 'max']
        }).round(2)

        biome_metrics.columns = ['total_km2', 'media_anual_km2', 'num_registros', 'ano_inicio', 'ano_fim']
        biome_metrics = biome_metrics.reset_index()

        # Calcular participação percentual
        total_geral = biome_metrics['total_km2'].sum()
        biome_metrics['participacao_percentual'] = (biome_metrics['total_km2'] / total_geral * 100).round(2)

        return biome_metrics

    def get_top_states(self,
                       n: int = 10,
                       ano: Optional[int] = None,
                       bioma: Optional[str] = None) -> pd.DataFrame:
        """
        Retorna os top N estados com maior desmatamento

        Args:
            n: Número de estados a retornar
            ano: Filtrar por ano específico
            bioma: Filtrar por bioma específico

        Returns:
            DataFrame com ranking de estados
        """
        df_filtered = self.df.copy()

        if ano:
            df_filtered = df_filtered[df_filtered['ano'] == ano]
        if bioma:
            df_filtered = df_filtered[df_filtered['bioma'] == bioma]

        ranking = df_filtered.groupby(['estado', 'estado_nome']).agg({
            'area_desmatada_km2': 'sum'
        }).reset_index()

        ranking = ranking.sort_values('area_desmatada_km2', ascending=False).head(n)
        ranking['ranking'] = range(1, len(ranking) + 1)

        return ranking

    def calculate_trends(self, estado: Optional[str] = None,
                        bioma: Optional[str] = None) -> Dict:
        """
        Calcula tendências e estatísticas de crescimento

        Args:
            estado: Filtrar por estado específico
            bioma: Filtrar por bioma específico

        Returns:
            Dicionário com métricas de tendência
        """
        df_filtered = self.df.copy()

        if estado:
            df_filtered = df_filtered[df_filtered['estado'] == estado]
        if bioma:
            df_filtered = df_filtered[df_filtered['bioma'] == bioma]

        yearly_totals = df_filtered.groupby('ano')['area_desmatada_km2'].sum()

        # Calcular regressão linear simples para tendência
        anos = yearly_totals.index.values
        valores = yearly_totals.values

        if len(anos) > 1:
            # Coeficientes da regressão linear
            coef = np.polyfit(anos, valores, 1)
            tendencia_anual = coef[0]

            # Calcular R²
            p = np.poly1d(coef)
            yhat = p(anos)
            ybar = np.mean(valores)
            ssreg = np.sum((yhat - ybar) ** 2)
            sstot = np.sum((valores - ybar) ** 2)
            r_squared = ssreg / sstot if sstot > 0 else 0

            # Variação período completo
            variacao_total = ((valores[-1] - valores[0]) / valores[0] * 100) if valores[0] != 0 else 0

            return {
                'tendencia_anual_km2': round(tendencia_anual, 2),
                'r_squared': round(r_squared, 4),
                'variacao_total_percentual': round(variacao_total, 2),
                'valor_inicial': round(valores[0], 2),
                'valor_final': round(valores[-1], 2),
                'media_periodo': round(np.mean(valores), 2),
                'desvio_padrao': round(np.std(valores), 2),
                'anos_analisados': len(anos)
            }
        else:
            return {}

    def detect_anomalies(self, threshold: float = 2.0) -> pd.DataFrame:
        """
        Detecta anomalias nos dados usando desvio padrão

        Args:
            threshold: Número de desvios padrão para considerar anomalia

        Returns:
            DataFrame com registros anômalos
        """
        # Calcular z-score por bioma
        anomalies = []

        for bioma in self.df['bioma'].unique():
            df_bioma = self.df[self.df['bioma'] == bioma].copy()

            mean = df_bioma['area_desmatada_km2'].mean()
            std = df_bioma['area_desmatada_km2'].std()

            if std > 0:
                df_bioma['z_score'] = (df_bioma['area_desmatada_km2'] - mean) / std
                df_anomalies = df_bioma[abs(df_bioma['z_score']) > threshold]
                anomalies.append(df_anomalies)

        if anomalies:
            return pd.concat(anomalies, ignore_index=True)
        else:
            return pd.DataFrame()

    def create_comparison_matrix(self, year1: int, year2: int) -> pd.DataFrame:
        """
        Cria matriz de comparação entre dois anos

        Args:
            year1: Ano base
            year2: Ano de comparação

        Returns:
            DataFrame com comparações por estado
        """
        df_y1 = self.df[self.df['ano'] == year1].groupby('estado').agg({
            'area_desmatada_km2': 'sum'
        }).rename(columns={'area_desmatada_km2': f'ano_{year1}'})

        df_y2 = self.df[self.df['ano'] == year2].groupby('estado').agg({
            'area_desmatada_km2': 'sum'
        }).rename(columns={'area_desmatada_km2': f'ano_{year2}'})

        comparison = df_y1.join(df_y2, how='outer').fillna(0)
        comparison['variacao_absoluta'] = comparison[f'ano_{year2}'] - comparison[f'ano_{year1}']
        comparison['variacao_percentual'] = (
            (comparison['variacao_absoluta'] / comparison[f'ano_{year1}'] * 100)
            .replace([np.inf, -np.inf], 0)
            .fillna(0)
        ).round(2)

        comparison = comparison.reset_index()
        comparison['estado_nome'] = comparison['estado'].map(ESTADOS_BRASIL)

        return comparison

    def export_processed_data(self, filename: str = "dados_processados.csv"):
        """Exporta dados processados"""
        output_path = PROCESSED_DATA_DIR / filename
        self.df.to_csv(output_path, index=False)
        logger.success(f"Dados exportados para: {output_path}")
        return output_path


def create_kpis(df: pd.DataFrame,
                ano_atual: int,
                estado: Optional[str] = None,
                bioma: Optional[str] = None) -> Dict:
    """
    Cria KPIs principais para o dashboard

    Args:
        df: DataFrame com dados
        ano_atual: Ano de referência
        estado: Filtrar por estado
        bioma: Filtrar por bioma

    Returns:
        Dicionário com KPIs
    """
    processor = DataProcessor(df)

    df_filtered = df.copy()
    if estado:
        df_filtered = df_filtered[df_filtered['estado'] == estado]
    if bioma:
        df_filtered = df_filtered[df_filtered['bioma'] == bioma]

    # Dados do ano atual e anterior
    df_atual = df_filtered[df_filtered['ano'] == ano_atual]
    df_anterior = df_filtered[df_filtered['ano'] == ano_atual - 1]

    total_atual = df_atual['area_desmatada_km2'].sum()
    total_anterior = df_anterior['area_desmatada_km2'].sum()

    # Calcular variação
    if total_anterior > 0:
        variacao = ((total_atual - total_anterior) / total_anterior) * 100
    else:
        variacao = 0

    # Tendências
    trends = processor.calculate_trends(estado=estado, bioma=bioma)

    # Métricas anuais
    yearly_metrics = processor.calculate_yearly_metrics(bioma=bioma)
    media_historica = yearly_metrics['total_km2'].mean()

    kpis = {
        'desmatamento_atual_km2': round(total_atual, 2),
        'desmatamento_anterior_km2': round(total_anterior, 2),
        'variacao_anual_percentual': round(variacao, 2),
        'variacao_anual_absoluta': round(total_atual - total_anterior, 2),
        'media_historica_km2': round(media_historica, 2),
        'tendencia': trends,
        'num_estados_afetados': df_atual['estado'].nunique(),
        'pior_estado': df_atual.groupby('estado')['area_desmatada_km2'].sum().idxmax() if len(df_atual) > 0 else None
    }

    return kpis
