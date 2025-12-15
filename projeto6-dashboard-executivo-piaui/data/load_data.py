"""
Modulo de Carga de Dados - Dashboard Executivo Piaui
=====================================================
ETL para extrair dados do IBGE SIDRA focados no estado do Piaui (codigo 22).

Fontes:
- Tabela 6579: Populacao estimada
- Tabela 5938: PIB dos Municipios
- API Localidades: Informacoes geograficas
"""

import pandas as pd
import numpy as np
import requests
from typing import Dict, Optional
import json

# Constantes
CODIGO_PIAUI = "22"
SIDRA_BASE_URL = "https://apisidra.ibge.gov.br/values"
LOCALIDADES_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"

# Mesorregioes do Piaui
MESORREGIOES = {
    2201: "Norte Piauiense",
    2202: "Centro-Norte Piauiense",
    2203: "Sudoeste Piauiense",
    2204: "Sudeste Piauiense"
}


def carregar_municipios_piaui() -> pd.DataFrame:
    """
    Carrega lista dos 224 municipios do Piaui com informacoes geograficas.

    Returns:
        DataFrame com colunas: id, nome, mesorregiao_id, mesorregiao_nome, microrregiao
    """
    try:
        url = f"{LOCALIDADES_URL}/estados/{CODIGO_PIAUI}/municipios"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        municipios = []
        for m in data:
            municipios.append({
                'municipio_id': m['id'],
                'municipio_nome': m['nome'],
                'mesorregiao_id': m['microrregiao']['mesorregiao']['id'],
                'mesorregiao_nome': m['microrregiao']['mesorregiao']['nome'],
                'microrregiao_nome': m['microrregiao']['nome']
            })

        df = pd.DataFrame(municipios)
        print(f"Municipios carregados: {len(df)}")
        return df

    except Exception as e:
        print(f"Erro ao carregar municipios: {e}")
        return _gerar_municipios_exemplo()


def carregar_populacao_piaui(anos: str = "2021|2022|2023|2024") -> pd.DataFrame:
    """
    Carrega dados de populacao estimada dos municipios do Piaui.

    Args:
        anos: Anos separados por pipe (ex: "2021|2022|2023")

    Returns:
        DataFrame com populacao por municipio e ano
    """
    try:
        # Tabela 6579 - Populacao estimada - Nivel municipal (N6) para Piaui
        url = f"{SIDRA_BASE_URL}/t/6579/n6/all/v/9324/p/{anos}/d/v9324%200"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Processar resposta (pular header)
        records = []
        for row in data[1:]:
            cod_mun = row.get('D1C', '')
            # Filtrar apenas Piaui (codigo comeca com 22)
            if cod_mun.startswith('22'):
                try:
                    pop = int(row.get('V', 0)) if row.get('V') and row.get('V') != '-' else 0
                    records.append({
                        'municipio_id': int(cod_mun),
                        'municipio_nome': row.get('D1N', ''),
                        'ano': int(row.get('D2C', 0)),
                        'populacao': pop
                    })
                except (ValueError, TypeError):
                    continue

        df = pd.DataFrame(records)
        print(f"Populacao carregada: {len(df)} registros")
        return df

    except Exception as e:
        print(f"Erro ao carregar populacao: {e}")
        return _gerar_populacao_exemplo()


def carregar_pib_piaui(anos: str = "2020|2021") -> pd.DataFrame:
    """
    Carrega dados de PIB dos municipios do Piaui.

    Args:
        anos: Anos separados por pipe

    Returns:
        DataFrame com PIB por municipio e ano
    """
    try:
        # Tabela 5938 - PIB Municipal
        # v37 = PIB a precos correntes (mil reais)
        # v93 = PIB per capita
        url = f"{SIDRA_BASE_URL}/t/5938/n6/all/v/37,93/p/{anos}"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Agrupar por municipio/ano
        pib_dict = {}
        for row in data[1:]:
            cod_mun = row.get('D1C', '')
            if cod_mun.startswith('22'):
                key = (cod_mun, row.get('D3C', ''))
                if key not in pib_dict:
                    pib_dict[key] = {
                        'municipio_id': int(cod_mun),
                        'municipio_nome': row.get('D1N', ''),
                        'ano': int(row.get('D3C', 0))
                    }

                var_cod = row.get('D2C', '')
                valor = row.get('V', '')
                try:
                    valor_num = float(valor) if valor and valor != '-' else 0
                except:
                    valor_num = 0

                if var_cod == '37':
                    pib_dict[key]['pib_mil_reais'] = valor_num
                elif var_cod == '93':
                    pib_dict[key]['pib_per_capita'] = valor_num

        df = pd.DataFrame(list(pib_dict.values()))
        print(f"PIB carregado: {len(df)} registros")
        return df

    except Exception as e:
        print(f"Erro ao carregar PIB: {e}")
        return _gerar_pib_exemplo()


def carregar_dados_completos() -> Dict[str, pd.DataFrame]:
    """
    Carrega todos os dados necessarios para o dashboard.

    Returns:
        Dicionario com DataFrames: municipios, populacao, pib, consolidado
    """
    print("=" * 60)
    print("CARREGANDO DADOS DO IBGE - PIAUI")
    print("=" * 60)

    # Carregar dados base
    df_municipios = carregar_municipios_piaui()
    df_populacao = carregar_populacao_piaui()
    df_pib = carregar_pib_piaui()

    # Criar dataset consolidado (ano mais recente)
    ano_pop = df_populacao['ano'].max() if len(df_populacao) > 0 else 2023
    ano_pib = df_pib['ano'].max() if len(df_pib) > 0 else 2021

    df_pop_recente = df_populacao[df_populacao['ano'] == ano_pop][['municipio_id', 'populacao']]
    df_pib_recente = df_pib[df_pib['ano'] == ano_pib][['municipio_id', 'pib_mil_reais', 'pib_per_capita']]

    df_consolidado = df_municipios.merge(df_pop_recente, on='municipio_id', how='left')
    df_consolidado = df_consolidado.merge(df_pib_recente, on='municipio_id', how='left')

    # Preencher valores nulos
    df_consolidado['populacao'] = df_consolidado['populacao'].fillna(0).astype(int)
    df_consolidado['pib_mil_reais'] = df_consolidado['pib_mil_reais'].fillna(0)
    df_consolidado['pib_per_capita'] = df_consolidado['pib_per_capita'].fillna(0)

    # Calcular metricas adicionais
    df_consolidado['pib_bilhoes'] = df_consolidado['pib_mil_reais'] / 1_000_000

    print(f"\nDataset consolidado: {len(df_consolidado)} municipios")
    print(f"Populacao total: {df_consolidado['populacao'].sum():,}")
    print(f"PIB total: R$ {df_consolidado['pib_mil_reais'].sum()/1_000_000:.1f} bilhoes")
    print("=" * 60)

    return {
        'municipios': df_municipios,
        'populacao': df_populacao,
        'pib': df_pib,
        'consolidado': df_consolidado
    }


# ============================================================
# DADOS DE EXEMPLO (fallback quando API nao disponivel)
# ============================================================

def _gerar_municipios_exemplo() -> pd.DataFrame:
    """Gera dados de exemplo dos municipios do Piaui."""
    np.random.seed(42)

    # Principais municipios do Piaui
    principais = [
        (2211001, "Teresina", 2202, "Centro-Norte Piauiense"),
        (2207702, "Parnaiba", 2201, "Norte Piauiense"),
        (2208007, "Picos", 2204, "Sudeste Piauiense"),
        (2203206, "Floriano", 2203, "Sudoeste Piauiense"),
        (2208403, "Piripiri", 2201, "Norte Piauiense"),
        (2202109, "Campo Maior", 2202, "Centro-Norte Piauiense"),
        (2201408, "Barras", 2201, "Norte Piauiense"),
        (2205003, "Jose de Freitas", 2202, "Centro-Norte Piauiense"),
        (2200202, "Altos", 2202, "Centro-Norte Piauiense"),
        (2201200, "Bom Jesus", 2203, "Sudoeste Piauiense"),
    ]

    municipios = []
    for i, (cod, nome, meso_id, meso_nome) in enumerate(principais):
        municipios.append({
            'municipio_id': cod,
            'municipio_nome': nome,
            'mesorregiao_id': meso_id,
            'mesorregiao_nome': meso_nome,
            'microrregiao_nome': f"Microrregiao {nome}"
        })

    # Adicionar municipios genericos para completar 224
    mesos = list(MESORREGIOES.items())
    for i in range(10, 224):
        meso_id, meso_nome = mesos[i % 4]
        municipios.append({
            'municipio_id': 2200000 + i,
            'municipio_nome': f"Municipio PI {i}",
            'mesorregiao_id': meso_id,
            'mesorregiao_nome': meso_nome,
            'microrregiao_nome': f"Microrregiao {i // 10}"
        })

    return pd.DataFrame(municipios)


def _gerar_populacao_exemplo() -> pd.DataFrame:
    """Gera dados de exemplo de populacao."""
    np.random.seed(42)

    df_mun = _gerar_municipios_exemplo()
    records = []

    pop_base = {
        2211001: 868000,  # Teresina
        2207702: 153000,  # Parnaiba
        2208007: 78000,   # Picos
        2203206: 59000,   # Floriano
        2208403: 63000,   # Piripiri
    }

    for _, mun in df_mun.iterrows():
        base = pop_base.get(mun['municipio_id'], np.random.randint(3000, 30000))
        for ano in [2021, 2022, 2023, 2024]:
            pop = int(base * (1 + (ano - 2021) * 0.005 + np.random.uniform(-0.01, 0.01)))
            records.append({
                'municipio_id': mun['municipio_id'],
                'municipio_nome': mun['municipio_nome'],
                'ano': ano,
                'populacao': pop
            })

    return pd.DataFrame(records)


def _gerar_pib_exemplo() -> pd.DataFrame:
    """Gera dados de exemplo de PIB."""
    np.random.seed(42)

    df_mun = _gerar_municipios_exemplo()
    records = []

    pib_base = {
        2211001: 24000000,  # Teresina - 24 bi
        2207702: 3200000,   # Parnaiba
        2208007: 1800000,   # Picos
        2203206: 1200000,   # Floriano
        2208403: 900000,    # Piripiri
    }

    for _, mun in df_mun.iterrows():
        pib = pib_base.get(mun['municipio_id'], np.random.randint(50000, 500000))
        pop = 868000 if mun['municipio_id'] == 2211001 else np.random.randint(5000, 50000)

        for ano in [2020, 2021]:
            pib_ano = pib * (1 + (ano - 2020) * 0.08)
            records.append({
                'municipio_id': mun['municipio_id'],
                'municipio_nome': mun['municipio_nome'],
                'ano': ano,
                'pib_mil_reais': pib_ano,
                'pib_per_capita': (pib_ano * 1000) / pop
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    # Teste do modulo
    dados = carregar_dados_completos()

    print("\n--- RESUMO DOS DADOS ---")
    for nome, df in dados.items():
        print(f"{nome}: {len(df)} registros, colunas: {list(df.columns)}")
