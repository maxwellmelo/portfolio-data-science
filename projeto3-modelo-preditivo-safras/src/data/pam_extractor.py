"""
Extrator de dados da Produção Agrícola Municipal (PAM) do IBGE.
Utiliza a API SIDRA para obter dados históricos de safras.
"""

import time
from typing import Dict, List, Optional, Union
from datetime import datetime
import pandas as pd
import numpy as np
import httpx
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings, CODIGOS_CULTURAS, CODIGOS_ESTADOS


class PAMExtractor:
    """
    Extrator de dados da Produção Agrícola Municipal (PAM).

    A PAM é a principal pesquisa do IBGE sobre produção agrícola,
    cobrindo área plantada, área colhida, quantidade produzida e
    rendimento médio das principais culturas temporárias e permanentes.

    Agregados SIDRA utilizados:
    - 1612: Área plantada, área colhida, quantidade produzida, rendimento médio
            e valor da produção das lavouras temporárias
    - 1613: Lavouras permanentes
    - 5457: Rendimento médio da produção
    """

    BASE_URL = "https://servicodados.ibge.gov.br/api/v3/agregados"

    def __init__(self, rate_limit_delay: float = 0.5):
        """
        Inicializa o extrator.

        Args:
            rate_limit_delay: Delay entre requisições (segundos)
        """
        self.rate_limit_delay = rate_limit_delay
        self._client = httpx.Client(timeout=60)
        self._last_request_time = 0.0

        logger.info("PAMExtractor inicializado")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Fecha conexão HTTP."""
        self._client.close()

    def _rate_limit(self):
        """Aplica rate limiting entre requisições."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _make_request(self, url: str) -> Union[Dict, List]:
        """
        Faz requisição à API SIDRA.

        Args:
            url: URL completa da requisição

        Returns:
            Dados JSON da resposta
        """
        self._rate_limit()
        logger.debug(f"Requisição: {url}")

        try:
            response = self._client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Erro HTTP: {str(e)}")
            raise

    def _parse_sidra_response(self, data: List[Dict]) -> pd.DataFrame:
        """
        Converte resposta SIDRA para DataFrame.

        Args:
            data: Resposta bruta da API

        Returns:
            DataFrame estruturado
        """
        if not data:
            return pd.DataFrame()

        records = []

        for variavel in data:
            variavel_id = variavel.get("id")
            variavel_nome = variavel.get("variavel", "")
            unidade = variavel.get("unidade", "")

            for resultado in variavel.get("resultados", []):
                # Extrair classificações (cultura)
                classificacoes = resultado.get("classificacoes", [])
                cultura_info = {}
                for classif in classificacoes:
                    for cat_id, cat_nome in classif.get("categoria", {}).items():
                        cultura_info["cultura_id"] = cat_id
                        cultura_info["cultura"] = cat_nome

                # Extrair séries por localidade
                for serie in resultado.get("series", []):
                    localidade = serie.get("localidade", {})
                    loc_id = localidade.get("id", "")
                    loc_nome = localidade.get("nome", "")
                    loc_nivel = localidade.get("nivel", {}).get("nome", "")

                    # Extrair valores por ano
                    for ano, valor in serie.get("serie", {}).items():
                        if valor and valor not in ["-", "...", "X"]:
                            try:
                                valor_float = float(str(valor).replace(".", "").replace(",", "."))
                            except ValueError:
                                continue

                            record = {
                                "variavel_id": variavel_id,
                                "variavel": variavel_nome,
                                "unidade": unidade,
                                "localidade_id": loc_id,
                                "localidade": loc_nome,
                                "nivel": loc_nivel,
                                "ano": int(ano),
                                "valor": valor_float,
                                **cultura_info
                            }
                            records.append(record)

        return pd.DataFrame(records)

    def extract_producao_municipal(
        self,
        cultura_codigo: int,
        anos: str = "all",
        nivel: str = "N6",  # N6 = Município
        localidades: str = "all"
    ) -> pd.DataFrame:
        """
        Extrai dados de produção agrícola municipal.

        Args:
            cultura_codigo: Código da cultura no SIDRA
            anos: Anos a extrair (ex: "2020|2021|2022" ou "all")
            nivel: Nível geográfico (N1=Brasil, N3=Estado, N6=Município)
            localidades: Códigos das localidades ou "all"

        Returns:
            DataFrame com dados de produção

        Variáveis extraídas:
            - 109: Área plantada (Hectares)
            - 216: Área colhida (Hectares)
            - 214: Quantidade produzida (Toneladas)
            - 112: Rendimento médio (kg/ha)
            - 215: Valor da produção (Mil Reais)
        """
        agregado = 1612  # Lavouras temporárias

        # Variáveis: área plantada, colhida, produção, rendimento, valor
        variaveis = "109|216|214|112|215"

        # Classificação: produto das lavouras temporárias
        classificacao = f"81[{cultura_codigo}]"

        url = (
            f"{self.BASE_URL}/{agregado}/periodos/{anos}/"
            f"variaveis/{variaveis}?"
            f"localidades={nivel}[{localidades}]&"
            f"classificacao={classificacao}"
        )

        logger.info(f"Extraindo dados de produção | cultura={cultura_codigo} | nivel={nivel}")

        data = self._make_request(url)
        df = self._parse_sidra_response(data)

        if not df.empty:
            # Pivotar para ter variáveis como colunas
            df_pivot = df.pivot_table(
                index=["localidade_id", "localidade", "nivel", "ano", "cultura_id", "cultura"],
                columns="variavel",
                values="valor",
                aggfunc="first"
            ).reset_index()

            # Renomear colunas
            col_map = {
                "Área plantada": "area_plantada_ha",
                "Área colhida": "area_colhida_ha",
                "Quantidade produzida": "producao_ton",
                "Rendimento médio da produção": "rendimento_kg_ha",
                "Valor da produção": "valor_producao_mil_reais"
            }

            for old, new in col_map.items():
                matching = [c for c in df_pivot.columns if old in str(c)]
                if matching:
                    df_pivot = df_pivot.rename(columns={matching[0]: new})

            logger.info(f"Dados extraídos: {len(df_pivot)} registros")
            return df_pivot

        return df

    def extract_producao_por_estado(
        self,
        cultura_codigo: int,
        anos: str = "all"
    ) -> pd.DataFrame:
        """
        Extrai dados de produção por estado.

        Args:
            cultura_codigo: Código da cultura
            anos: Anos a extrair

        Returns:
            DataFrame com dados por estado
        """
        return self.extract_producao_municipal(
            cultura_codigo=cultura_codigo,
            anos=anos,
            nivel="N3",  # Estado
            localidades="all"
        )

    def extract_multiplas_culturas(
        self,
        codigos_culturas: List[int],
        anos: str = "all",
        nivel: str = "N3"
    ) -> pd.DataFrame:
        """
        Extrai dados de múltiplas culturas.

        Args:
            codigos_culturas: Lista de códigos de culturas
            anos: Anos a extrair
            nivel: Nível geográfico

        Returns:
            DataFrame consolidado
        """
        dfs = []

        for codigo in codigos_culturas:
            logger.info(f"Extraindo cultura {codigo}...")
            try:
                df = self.extract_producao_municipal(
                    cultura_codigo=codigo,
                    anos=anos,
                    nivel=nivel
                )
                if not df.empty:
                    dfs.append(df)
            except Exception as e:
                logger.warning(f"Erro ao extrair cultura {codigo}: {str(e)}")
                continue

        if dfs:
            df_final = pd.concat(dfs, ignore_index=True)
            logger.info(f"Total extraído: {len(df_final)} registros de {len(dfs)} culturas")
            return df_final

        return pd.DataFrame()

    def extract_serie_historica(
        self,
        cultura: str,
        estado: str,
        ano_inicio: int = 2000,
        ano_fim: int = 2023
    ) -> pd.DataFrame:
        """
        Extrai série histórica de uma cultura em um estado.

        Args:
            cultura: Nome da cultura
            estado: Sigla do estado (ex: "PI")
            ano_inicio: Ano inicial
            ano_fim: Ano final

        Returns:
            DataFrame com série histórica
        """
        if cultura not in CODIGOS_CULTURAS:
            raise ValueError(f"Cultura '{cultura}' não encontrada. Opções: {list(CODIGOS_CULTURAS.keys())}")

        if estado not in CODIGOS_ESTADOS:
            raise ValueError(f"Estado '{estado}' não encontrado. Use sigla (ex: PI)")

        cultura_codigo = CODIGOS_CULTURAS[cultura]
        estado_codigo = CODIGOS_ESTADOS[estado]
        anos = "|".join(str(a) for a in range(ano_inicio, ano_fim + 1))

        df = self.extract_producao_municipal(
            cultura_codigo=cultura_codigo,
            anos=anos,
            nivel="N3",
            localidades=str(estado_codigo)
        )

        if not df.empty:
            df["estado"] = estado
            df = df.sort_values("ano")

        return df


def generate_synthetic_pam_data(
    anos: range = range(2000, 2024),
    n_municipios: int = 100
) -> pd.DataFrame:
    """
    Gera dados sintéticos baseados em padrões reais da PAM.
    Útil para testes e demonstração quando a API não está disponível.

    Args:
        anos: Range de anos
        n_municipios: Número de municípios a gerar

    Returns:
        DataFrame com dados sintéticos
    """
    np.random.seed(42)

    culturas = list(CODIGOS_CULTURAS.keys())[:5]  # Top 5 culturas
    estados = list(CODIGOS_ESTADOS.keys())

    # Rendimentos médios base por cultura (kg/ha)
    rendimentos_base = {
        "Soja (em grão)": 3200,
        "Milho (em grão)": 5500,
        "Arroz (em casca)": 6000,
        "Feijão (em grão)": 1100,
        "Algodão herbáceo (em caroço)": 4000,
        "Cana-de-açúcar": 75000,
        "Café (em grão) Total": 1500,
        "Mandioca": 14000
    }

    records = []

    for ano in anos:
        for _ in range(n_municipios):
            estado = np.random.choice(estados)
            cultura = np.random.choice(culturas)

            # Área plantada com variação por estado e ano
            area_base = np.random.lognormal(mean=7, sigma=1.5)  # 100 a 50000 ha
            tendencia_ano = 1 + (ano - 2000) * 0.02  # Crescimento 2% ao ano
            area_plantada = area_base * tendencia_ano * np.random.uniform(0.8, 1.2)

            # Área colhida (geralmente 90-100% da plantada)
            taxa_colheita = np.random.uniform(0.85, 1.0)
            area_colhida = area_plantada * taxa_colheita

            # Rendimento com variação climática
            rend_base = rendimentos_base.get(cultura, 3000)
            variacao_clima = np.random.normal(1, 0.15)  # ±15%
            tendencia_tecnologia = 1 + (ano - 2000) * 0.01  # Ganho 1% ao ano
            rendimento = rend_base * variacao_clima * tendencia_tecnologia

            # Produção
            producao = (area_colhida * rendimento) / 1000  # Toneladas

            # Valor (preço médio por tonelada varia por cultura)
            preco_ton = np.random.uniform(500, 2000)
            valor = producao * preco_ton / 1000  # Mil reais

            # Coordenadas aproximadas do estado
            lat = np.random.uniform(-33, 5)
            lon = np.random.uniform(-73, -35)

            records.append({
                "ano": ano,
                "estado": estado,
                "cultura": cultura,
                "area_plantada_ha": round(area_plantada, 2),
                "area_colhida_ha": round(area_colhida, 2),
                "producao_ton": round(producao, 2),
                "rendimento_kg_ha": round(rendimento, 2),
                "valor_producao_mil_reais": round(valor, 2),
                "latitude": round(lat, 4),
                "longitude": round(lon, 4)
            })

    df = pd.DataFrame(records)
    logger.info(f"Dados sintéticos gerados: {len(df)} registros")

    return df


# Exemplo de uso
if __name__ == "__main__":
    from loguru import logger
    import sys

    logger.remove()
    logger.add(sys.stderr, level="INFO")

    # Gerar dados sintéticos para teste
    df = generate_synthetic_pam_data()
    print(df.head(10))
    print(f"\nTotal: {len(df)} registros")
    print(f"Culturas: {df['cultura'].unique()}")
    print(f"Anos: {df['ano'].min()} - {df['ano'].max()}")
