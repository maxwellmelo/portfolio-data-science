"""
Extrator de dados populacionais do IBGE.
Utiliza o agregado 6579 (Estimativas populacionais).
"""

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from .ibge_client import IBGEClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PopulacaoExtractor:
    """
    Extrator de dados populacionais do IBGE.

    Utiliza o agregado SIDRA 6579 - Estimativas populacionais.
    Dados disponíveis a partir de 2001, atualizados anualmente.
    """

    AGREGADO_ID = 6579  # Estimativas populacionais

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

    def _parse_sidra_response(self, data: List[Dict]) -> pd.DataFrame:
        """
        Converte resposta da API SIDRA para DataFrame.

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
            variavel_nome = variavel.get("variavel")
            unidade = variavel.get("unidade")

            resultados = variavel.get("resultados", [])

            for resultado in resultados:
                series = resultado.get("series", [])

                for serie in series:
                    localidade = serie.get("localidade", {})
                    localidade_id = localidade.get("id")
                    localidade_nome = localidade.get("nome")
                    localidade_nivel = localidade.get("nivel", {}).get("nome")

                    valores = serie.get("serie", {})

                    for ano, valor in valores.items():
                        # Ignorar valores nulos ou marcados como "-"
                        if valor and valor != "-" and valor != "...":
                            records.append({
                                "variavel_id": variavel_id,
                                "variavel_nome": variavel_nome,
                                "unidade": unidade,
                                "localidade_id": localidade_id,
                                "localidade_nome": localidade_nome,
                                "localidade_nivel": localidade_nivel,
                                "ano": int(ano),
                                "valor": float(valor) if valor else None
                            })

        return pd.DataFrame(records)

    def extract_por_estado(
        self,
        anos: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extrai população estimada por estado.

        Args:
            anos: Anos específicos (ex: '2020|2021|2022') ou None para todos

        Returns:
            DataFrame com população por estado e ano
        """
        logger.info("Extraindo população por estado")
        start_time = datetime.now()

        data = self._client.get_populacao_estimada(
            nivel="N3",  # N3 = Estados
            anos=anos
        )

        df = self._parse_sidra_response(data)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Extração de população por estado concluída | "
            f"registros={len(df)} | tempo={elapsed:.2f}s"
        )

        return df

    def extract_por_municipio(
        self,
        uf_id: Optional[int] = None,
        anos: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extrai população estimada por município.

        Args:
            uf_id: ID do estado para filtrar (ex: 22 para PI)
            anos: Anos específicos ou None para todos

        Returns:
            DataFrame com população por município e ano
        """
        if uf_id:
            logger.info(f"Extraindo população por município do estado {uf_id}")
            # Para filtrar por UF, usamos o padrão de localidade específico
            # Os municípios de uma UF começam com o código da UF (2 dígitos)
            localidade = f"N6[{uf_id}]"
        else:
            logger.info("Extraindo população por município (todos)")
            localidade = "N6[all]"

        start_time = datetime.now()

        data = self._client.get_populacao_estimada(
            nivel="N6" if not uf_id else "",
            localidade="all" if not uf_id else str(uf_id),
            anos=anos
        )

        df = self._parse_sidra_response(data)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Extração de população por município concluída | "
            f"registros={len(df)} | tempo={elapsed:.2f}s"
        )

        return df

    def extract_brasil(
        self,
        anos: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extrai população total do Brasil.

        Args:
            anos: Anos específicos ou None para todos

        Returns:
            DataFrame com população do Brasil por ano
        """
        logger.info("Extraindo população do Brasil")
        start_time = datetime.now()

        data = self._client.get_populacao_estimada(
            nivel="N1",  # N1 = Brasil
            localidade="all",
            anos=anos
        )

        df = self._parse_sidra_response(data)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Extração de população do Brasil concluída | "
            f"registros={len(df)} | tempo={elapsed:.2f}s"
        )

        return df


# Exemplo de uso
if __name__ == "__main__":
    from src.utils.logger import setup_logger

    setup_logger(log_level="INFO")

    with PopulacaoExtractor() as extractor:
        # Extrair população do Brasil
        pop_brasil = extractor.extract_brasil(anos="2020|2021|2022|2023")
        print("\n=== População do Brasil ===")
        print(pop_brasil)

        # Extrair população por estado
        pop_estados = extractor.extract_por_estado(anos="2023")
        print("\n=== População por Estado (2023) ===")
        print(pop_estados.head(10))
