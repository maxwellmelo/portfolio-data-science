"""
Extrator de dados de localidades do IBGE.
Responsável por extrair regiões, estados e municípios.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from .ibge_client import IBGEClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ExtractionMetadata:
    """Metadados da extração."""
    source: str
    extracted_at: datetime
    record_count: int
    extraction_time_seconds: float


class LocalidadesExtractor:
    """
    Extrator de dados de localidades do IBGE.

    Responsável por:
    - Extrair regiões do Brasil
    - Extrair estados
    - Extrair municípios (todos ou por UF)
    """

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

    def extract_regioes(self) -> pd.DataFrame:
        """
        Extrai todas as regiões do Brasil.

        Returns:
            DataFrame com colunas: id, sigla, nome
        """
        logger.info("Iniciando extração de regiões")
        start_time = datetime.now()

        data = self._client.get_regioes()

        df = pd.DataFrame(data)
        df.columns = ["id", "sigla", "nome"]

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Extração de regiões concluída | "
            f"registros={len(df)} | tempo={elapsed:.2f}s"
        )

        return df

    def extract_estados(self) -> pd.DataFrame:
        """
        Extrai todos os estados do Brasil.

        Returns:
            DataFrame com colunas: id, sigla, nome, regiao_id
        """
        logger.info("Iniciando extração de estados")
        start_time = datetime.now()

        data = self._client.get_estados()

        # Transformar estrutura aninhada
        estados = []
        for item in data:
            estados.append({
                "id": item["id"],
                "sigla": item["sigla"],
                "nome": item["nome"],
                "regiao_id": item["regiao"]["id"],
                "regiao_sigla": item["regiao"]["sigla"],
                "regiao_nome": item["regiao"]["nome"]
            })

        df = pd.DataFrame(estados)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Extração de estados concluída | "
            f"registros={len(df)} | tempo={elapsed:.2f}s"
        )

        return df

    def extract_municipios(self, uf: Optional[str] = None) -> pd.DataFrame:
        """
        Extrai municípios do Brasil ou de um estado específico.

        Args:
            uf: Sigla do estado ou None para todos

        Returns:
            DataFrame com dados dos municípios
        """
        if uf:
            logger.info(f"Iniciando extração de municípios do estado: {uf}")
        else:
            logger.info("Iniciando extração de todos os municípios")

        start_time = datetime.now()

        data = self._client.get_municipios(uf)

        # Transformar estrutura aninhada
        municipios = []
        for item in data:
            municipio = {
                "id": item["id"],
                "nome": item["nome"]
            }

            # Extrair dados da microrregião
            micro = item.get("microrregiao")
            if micro:
                municipio["microrregiao_id"] = micro.get("id")
                municipio["microrregiao_nome"] = micro.get("nome")

                # Extrair mesorregião
                meso = micro.get("mesorregiao")
                if meso:
                    municipio["mesorregiao_id"] = meso.get("id")
                    municipio["mesorregiao_nome"] = meso.get("nome")

                    # Extrair UF
                    uf_data = meso.get("UF")
                    if uf_data:
                        municipio["uf_id"] = uf_data.get("id")
                        municipio["uf_sigla"] = uf_data.get("sigla")
                        municipio["uf_nome"] = uf_data.get("nome")

                        # Extrair região
                        regiao = uf_data.get("regiao")
                        if regiao:
                            municipio["regiao_id"] = regiao.get("id")
                            municipio["regiao_sigla"] = regiao.get("sigla")
                            municipio["regiao_nome"] = regiao.get("nome")

            municipios.append(municipio)

        df = pd.DataFrame(municipios)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Extração de municípios concluída | "
            f"registros={len(df)} | tempo={elapsed:.2f}s"
        )

        return df

    def extract_all(self) -> Dict[str, pd.DataFrame]:
        """
        Extrai todas as localidades (regiões, estados, municípios).

        Returns:
            Dicionário com DataFrames para cada entidade
        """
        logger.info("Iniciando extração completa de localidades")

        result = {
            "regioes": self.extract_regioes(),
            "estados": self.extract_estados(),
            "municipios": self.extract_municipios()
        }

        total_records = sum(len(df) for df in result.values())
        logger.info(f"Extração completa concluída | total_registros={total_records}")

        return result


# Exemplo de uso
if __name__ == "__main__":
    from src.utils.logger import setup_logger

    setup_logger(log_level="INFO")

    with LocalidadesExtractor() as extractor:
        # Extrair todas as localidades
        dados = extractor.extract_all()

        print("\n=== Resumo da Extração ===")
        for nome, df in dados.items():
            print(f"{nome}: {len(df)} registros")
            print(df.head(3))
            print()
