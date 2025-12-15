"""
Extrator de Dados Reais do IBGE.

Busca dados oficiais da API do IBGE (SIDRA) para os municípios do Piauí:
- População estimada
- PIB Municipal e componentes
- PIB per capita
"""

import requests
import pandas as pd
import time
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import MUNICIPIOS_PIAUI


class IBGEExtractor:
    """
    Extrator de dados reais da API do IBGE.

    APIs utilizadas:
    - SIDRA (Sistema IBGE de Recuperação Automática)
    - Agregados estatísticos
    """

    BASE_URL = "https://servicodados.ibge.gov.br/api/v3/agregados"

    # Códigos das tabelas/agregados do SIDRA
    AGREGADOS = {
        "populacao_estimada": 6579,      # Estimativas de população
        "pib_municipal": 5938,            # PIB dos Municípios
    }

    # Variáveis disponíveis
    VARIAVEIS = {
        "populacao": 9324,                # População residente estimada
        "pib_total": 37,                  # PIB a preços correntes (Mil Reais)
        "pib_per_capita": 38,             # PIB per capita (Reais)
        "impostos": 513,                  # Impostos sobre produtos líquidos
        "vab_total": 517,                 # VAB total
        "vab_agropecuaria": 525,          # VAB Agropecuária
        "vab_industria": 497,             # VAB Indústria
        "vab_servicos": 498,              # VAB Serviços (exceto APU)
        "vab_adm_publica": 505,           # VAB Administração pública
    }

    def __init__(self, delay: float = 0.5):
        """
        Inicializa o extrator.

        Args:
            delay: Tempo de espera entre requisições (rate limiting)
        """
        self.delay = delay
        self.municipios = MUNICIPIOS_PIAUI
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Portfolio Data Science Project)'
        })

        logger.info(f"IBGEExtractor inicializado | {len(self.municipios)} municípios")

    def _build_url(
        self,
        agregado: int,
        periodos: List[int],
        variaveis: List[int],
        municipios: List[int]
    ) -> str:
        """Constrói URL da API SIDRA."""
        periodos_str = "|".join(str(p) for p in periodos)
        variaveis_str = "|".join(str(v) for v in variaveis)
        municipios_str = ",".join(str(m) for m in municipios)

        return (
            f"{self.BASE_URL}/{agregado}/periodos/{periodos_str}"
            f"/variaveis/{variaveis_str}?localidades=N6[{municipios_str}]"
        )

    def _fetch_data(self, url: str) -> Optional[List[Dict]]:
        """Faz requisição à API com retry."""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=60)
                response.raise_for_status()
                time.sleep(self.delay)
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1}/{max_retries} falhou: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Falha ao buscar dados: {url}")
                    return None

        return None

    def extract_populacao(self, anos: List[int] = None) -> pd.DataFrame:
        """
        Extrai dados de população estimada.

        Args:
            anos: Lista de anos (padrão: últimos 5 anos disponíveis)

        Returns:
            DataFrame com população por município e ano
        """
        if anos is None:
            anos = [2019, 2020, 2021, 2022, 2023, 2024]

        logger.info(f"Extraindo população para {len(self.municipios)} municípios...")

        # Buscar em lotes de 50 municípios
        all_records = []
        municipio_ids = list(self.municipios.keys())
        batch_size = 50

        for i in range(0, len(municipio_ids), batch_size):
            batch = municipio_ids[i:i + batch_size]
            logger.info(f"Processando lote {i//batch_size + 1}/{(len(municipio_ids) + batch_size - 1)//batch_size}")

            url = self._build_url(
                agregado=self.AGREGADOS["populacao_estimada"],
                periodos=anos,
                variaveis=[self.VARIAVEIS["populacao"]],
                municipios=batch
            )

            data = self._fetch_data(url)

            if data:
                for variavel in data:
                    for resultado in variavel.get("resultados", []):
                        for serie in resultado.get("series", []):
                            municipio_id = int(serie["localidade"]["id"])
                            municipio_nome = serie["localidade"]["nome"].replace(" (PI)", "")

                            for ano, valor in serie.get("serie", {}).items():
                                if valor and valor != "-":
                                    all_records.append({
                                        "municipio_id": municipio_id,
                                        "municipio_nome": municipio_nome,
                                        "uf": "PI",
                                        "ano": int(ano),
                                        "populacao_estimada": int(valor)
                                    })

        df = pd.DataFrame(all_records)
        logger.info(f"População extraída: {len(df)} registros")

        return df

    def extract_pib(self, anos: List[int] = None) -> pd.DataFrame:
        """
        Extrai dados de PIB municipal.

        Args:
            anos: Lista de anos (padrão: últimos anos disponíveis)

        Returns:
            DataFrame com PIB por município e ano
        """
        if anos is None:
            anos = [2020, 2021]  # PIB tem defasagem de ~2 anos (2021 é o mais recente)

        logger.info(f"Extraindo PIB para {len(self.municipios)} municípios...")

        # Variáveis principais para PIB (uma por vez para evitar erro 500)
        variaveis_pib = {
            "pib_total": self.VARIAVEIS["pib_total"],
            "pib_per_capita": self.VARIAVEIS["pib_per_capita"],
        }

        all_records = {}  # {(municipio_id, ano): {dados}}
        municipio_ids = list(self.municipios.keys())
        batch_size = 50

        # Processar cada variável separadamente (IBGE API não suporta múltiplas variáveis)
        for var_nome, var_id in variaveis_pib.items():
            logger.info(f"Extraindo variável: {var_nome}")

            for i in range(0, len(municipio_ids), batch_size):
                batch = municipio_ids[i:i + batch_size]
                logger.info(f"  Lote {i//batch_size + 1}/{(len(municipio_ids) + batch_size - 1)//batch_size}")

                url = self._build_url(
                    agregado=self.AGREGADOS["pib_municipal"],
                    periodos=anos,
                    variaveis=[var_id],  # Uma variável por vez
                    municipios=batch
                )

                data = self._fetch_data(url)

                if data:
                    for variavel in data:
                        col_nome = self._get_var_name(int(variavel["id"]))

                        for resultado in variavel.get("resultados", []):
                            for serie in resultado.get("series", []):
                                municipio_id = int(serie["localidade"]["id"])
                                municipio_nome = serie["localidade"]["nome"].replace(" (PI)", "")

                                for ano, valor in serie.get("serie", {}).items():
                                    key = (municipio_id, int(ano))

                                    if key not in all_records:
                                        all_records[key] = {
                                            "municipio_id": municipio_id,
                                            "municipio_nome": municipio_nome,
                                            "uf": "PI",
                                            "ano": int(ano)
                                        }

                                    if valor and valor != "-":
                                        try:
                                            all_records[key][col_nome] = float(valor)
                                        except ValueError:
                                            pass

        df = pd.DataFrame(list(all_records.values()))
        logger.info(f"PIB extraído: {len(df)} registros")

        return df

    def _get_var_name(self, var_id: int) -> str:
        """Retorna nome da coluna para uma variável."""
        var_names = {
            37: "pib_total_mil_reais",
            38: "pib_per_capita_reais",
            525: "vab_agropecuaria_mil_reais",
            497: "vab_industria_mil_reais",
            498: "vab_servicos_mil_reais",
            505: "vab_adm_publica_mil_reais",
        }
        return var_names.get(var_id, f"variavel_{var_id}")

    def extract_all(self, save_dir: str = "data/real") -> Dict[str, pd.DataFrame]:
        """
        Extrai todos os dados disponíveis.

        Args:
            save_dir: Diretório para salvar os CSVs

        Returns:
            Dicionário com DataFrames
        """
        logger.info("Iniciando extração de dados reais do IBGE...")

        datasets = {}

        # População
        logger.info("=" * 50)
        logger.info("Extraindo POPULAÇÃO...")
        df_pop = self.extract_populacao()
        if not df_pop.empty:
            datasets["populacao"] = df_pop

        # PIB
        logger.info("=" * 50)
        logger.info("Extraindo PIB MUNICIPAL...")
        df_pib = self.extract_pib()
        if not df_pib.empty:
            datasets["pib_municipal"] = df_pib

        # Combinar população com PIB
        if "populacao" in datasets and "pib_municipal" in datasets:
            logger.info("Combinando dados...")
            df_combined = pd.merge(
                datasets["pib_municipal"],
                datasets["populacao"][["municipio_id", "ano", "populacao_estimada"]],
                on=["municipio_id", "ano"],
                how="left"
            )
            datasets["economia_completo"] = df_combined

        # Salvar arquivos
        if save_dir:
            save_path = Path(save_dir)
            save_path.mkdir(parents=True, exist_ok=True)

            for name, df in datasets.items():
                filepath = save_path / f"{name}.csv"
                df.to_csv(filepath, index=False, encoding="utf-8-sig")
                logger.info(f"Salvo: {filepath} ({len(df)} registros)")

        total = sum(len(df) for df in datasets.values())
        logger.info(f"Extração concluída! Total: {total} registros")

        return datasets


# Script de execução
if __name__ == "__main__":
    extractor = IBGEExtractor()

    print("\n" + "=" * 60)
    print("EXTRATOR DE DADOS REAIS - IBGE")
    print("=" * 60)

    datasets = extractor.extract_all(save_dir="data/real")

    print("\n" + "=" * 60)
    print("RESUMO DOS DADOS EXTRAÍDOS")
    print("=" * 60)

    for name, df in datasets.items():
        print(f"\n{name.upper()}:")
        print(f"  Registros: {len(df)}")
        print(f"  Colunas: {list(df.columns)}")
        if "municipio_id" in df.columns:
            print(f"  Municípios únicos: {df['municipio_id'].nunique()}")
        if "ano" in df.columns:
            print(f"  Anos: {sorted(df['ano'].unique())}")
