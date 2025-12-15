"""
Extrator de dados de PIB do IBGE.
Utiliza agregados do SIDRA para PIB municipal e per capita.
"""

from typing import Optional
from datetime import datetime
import pandas as pd

from .ibge_client import IBGEClient
from src.utils.logger import get_logger
from src.utils.sidra_parser import parse_sidra_response
from config.constants import AGREGADO_PIB, VARIAVEL_PIB_PERCAPITA

logger = get_logger(__name__)


class PIBExtractor:
    """
    Extrator de dados de PIB do IBGE.

    Agregados utilizados:
    - 5938: PIB Municipal (Produto Interno Bruto dos Municípios)
           - Variavel 37: PIB a precos correntes
           - Variavel 513: PIB per capita
    """

    AGREGADO_PIB = AGREGADO_PIB
    VARIAVEL_PIB_PERCAPITA = VARIAVEL_PIB_PERCAPITA

    def __init__(self, client: Optional[IBGEClient] = None):
        """
        Inicializa o extrator.

        Args:
            client: Cliente IBGE (cria um novo se não fornecido)
        """
        self._client = client or IBGEClient()
        self._owns_client = client is None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._owns_client:
            self._client.close()

    def extract_pib_por_estado(
        self,
        anos: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extrai PIB por estado.

        Args:
            anos: Anos específicos (ex: '2019|2020|2021') ou None para todos

        Returns:
            DataFrame com PIB por estado e ano
        """
        logger.info("Extraindo PIB por estado")
        start_time = datetime.now()

        data = self._client.get_pib_municipal(
            nivel="N3",  # N3 = Estados
            anos=anos
        )

        df = parse_sidra_response(data)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Extração de PIB por estado concluída | "
            f"registros={len(df)} | tempo={elapsed:.2f}s"
        )

        return df

    def extract_pib_por_municipio(
        self,
        uf_sigla: Optional[str] = None,
        anos: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extrai PIB por município.

        Args:
            uf_sigla: Sigla do estado para filtrar (ex: 'PI')
            anos: Anos específicos ou None para todos

        Returns:
            DataFrame com PIB por município e ano
        """
        if uf_sigla:
            logger.info(f"Extraindo PIB por município do estado {uf_sigla}")
        else:
            logger.info("Extraindo PIB por município (todos)")

        start_time = datetime.now()

        data = self._client.get_pib_municipal(
            nivel="N6",  # N6 = Municípios
            anos=anos
        )

        df = parse_sidra_response(data)

        # Filtrar por UF se especificado
        if uf_sigla and not df.empty:
            # O código do município começa com o código da UF
            df = df[df["localidade_nome"].str.contains(f" - {uf_sigla}$", regex=True)]

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Extração de PIB por município concluída | "
            f"registros={len(df)} | tempo={elapsed:.2f}s"
        )

        return df

    def extract_pib_percapita_por_estado(
        self,
        anos: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extrai PIB per capita por estado.

        Args:
            anos: Anos específicos ou None para todos

        Returns:
            DataFrame com PIB per capita por estado e ano
        """
        logger.info("Extraindo PIB per capita por estado")
        start_time = datetime.now()

        data = self._client.get_pib_per_capita(
            nivel="N3",  # N3 = Estados
            anos=anos
        )

        df = parse_sidra_response(data)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Extração de PIB per capita por estado concluída | "
            f"registros={len(df)} | tempo={elapsed:.2f}s"
        )

        return df

    def extract_pib_percapita_por_municipio(
        self,
        uf_sigla: Optional[str] = None,
        anos: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extrai PIB per capita por município.

        Args:
            uf_sigla: Sigla do estado para filtrar
            anos: Anos específicos ou None para todos

        Returns:
            DataFrame com PIB per capita por município e ano
        """
        if uf_sigla:
            logger.info(f"Extraindo PIB per capita por município do estado {uf_sigla}")
        else:
            logger.info("Extraindo PIB per capita por município (todos)")

        start_time = datetime.now()

        data = self._client.get_pib_per_capita(
            nivel="N6",  # N6 = Municípios
            anos=anos
        )

        df = parse_sidra_response(data)

        # Filtrar por UF se especificado
        if uf_sigla and not df.empty:
            df = df[df["localidade_nome"].str.contains(f" - {uf_sigla}$", regex=True)]

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Extração de PIB per capita por município concluída | "
            f"registros={len(df)} | tempo={elapsed:.2f}s"
        )

        return df


# Exemplo de uso
if __name__ == "__main__":
    from src.utils.logger import setup_logger

    setup_logger(log_level="INFO")

    with PIBExtractor() as extractor:
        # Extrair PIB por estado
        pib_estados = extractor.extract_pib_por_estado(anos="2020|2021")
        print("\n=== PIB por Estado ===")
        print(pib_estados.head(10))

        # Extrair PIB per capita
        pib_pc = extractor.extract_pib_percapita_por_estado(anos="2021")
        print("\n=== PIB per capita por Estado (2021) ===")
        print(pib_pc.head(10))
