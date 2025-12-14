"""
Pipeline ETL Principal - Dados Socioeconômicos do IBGE.

Este script orquestra todo o processo de ETL:
1. Extração de dados da API do IBGE
2. Transformação e validação
3. Carregamento para banco de dados ou CSV

Uso:
    python main.py --help
    python main.py --extract localidades
    python main.py --extract all --output csv
    python main.py --extract all --output database
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.utils.logger import setup_logger, get_logger
from src.extractors import (
    IBGEClient,
    LocalidadesExtractor,
    PopulacaoExtractor,
    PIBExtractor
)
from src.transformers import DataCleaner
from src.loaders import CSVLoader

logger = get_logger(__name__)


class ETLPipeline:
    """
    Orquestrador do pipeline ETL.

    Coordena a execução de:
    - Extração de dados do IBGE
    - Limpeza e transformação
    - Carregamento para destino (CSV ou banco de dados)
    """

    def __init__(self, output_type: str = "csv"):
        """
        Inicializa o pipeline.

        Args:
            output_type: 'csv' ou 'database'
        """
        self.output_type = output_type
        self.client = IBGEClient()
        self.cleaner = DataCleaner()

        if output_type == "csv":
            self.loader = CSVLoader()
        else:
            from src.loaders import DatabaseLoader, create_tables
            create_tables()
            self.loader = DatabaseLoader()

        self.stats = {
            "extraidos": 0,
            "transformados": 0,
            "carregados": 0,
            "erros": 0
        }

        logger.info(f"Pipeline ETL inicializado | output={output_type}")

    def run_localidades(self) -> dict:
        """
        Executa ETL de localidades (regiões, estados, municípios).

        Returns:
            Estatísticas da execução
        """
        logger.info("=" * 60)
        logger.info("INICIANDO ETL: LOCALIDADES")
        logger.info("=" * 60)

        start_time = datetime.now()
        results = {"regioes": 0, "estados": 0, "municipios": 0}

        try:
            with LocalidadesExtractor(self.client) as extractor:
                # Extrair regiões
                logger.info("-" * 40)
                logger.info("Extraindo regiões...")
                df_regioes = extractor.extract_regioes()
                df_regioes = self.cleaner.clean_localidades(df_regioes)

                if self.output_type == "csv":
                    self.loader.save_regioes(df_regioes)
                else:
                    self.loader.load_regioes(df_regioes)

                results["regioes"] = len(df_regioes)
                logger.info(f"Regiões processadas: {len(df_regioes)}")

                # Extrair estados
                logger.info("-" * 40)
                logger.info("Extraindo estados...")
                df_estados = extractor.extract_estados()
                df_estados = self.cleaner.clean_localidades(df_estados)

                if self.output_type == "csv":
                    self.loader.save_estados(df_estados)
                else:
                    self.loader.load_estados(df_estados)

                results["estados"] = len(df_estados)
                logger.info(f"Estados processados: {len(df_estados)}")

                # Extrair municípios
                logger.info("-" * 40)
                logger.info("Extraindo municípios...")
                df_municipios = extractor.extract_municipios()
                df_municipios = self.cleaner.clean_localidades(df_municipios)

                if self.output_type == "csv":
                    self.loader.save_municipios(df_municipios)
                else:
                    self.loader.load_municipios(df_municipios)

                results["municipios"] = len(df_municipios)
                logger.info(f"Municípios processados: {len(df_municipios)}")

        except Exception as e:
            logger.error(f"Erro no ETL de localidades: {str(e)}")
            self.stats["erros"] += 1
            raise

        elapsed = (datetime.now() - start_time).total_seconds()
        total = sum(results.values())

        logger.info("=" * 60)
        logger.info(f"ETL LOCALIDADES CONCLUÍDO | total={total} | tempo={elapsed:.2f}s")
        logger.info("=" * 60)

        self.stats["extraidos"] += total
        self.stats["carregados"] += total

        return results

    def run_populacao(self, anos: Optional[str] = None) -> dict:
        """
        Executa ETL de dados populacionais.

        Args:
            anos: Anos específicos (ex: '2020|2021|2022') ou None para todos

        Returns:
            Estatísticas da execução
        """
        logger.info("=" * 60)
        logger.info("INICIANDO ETL: POPULAÇÃO")
        logger.info("=" * 60)

        start_time = datetime.now()
        results = {"brasil": 0, "estados": 0}

        try:
            with PopulacaoExtractor(self.client) as extractor:
                # Extrair população do Brasil
                logger.info("-" * 40)
                logger.info("Extraindo população do Brasil...")
                df_brasil = extractor.extract_brasil(anos=anos)

                if not df_brasil.empty:
                    df_brasil = self.cleaner.clean_populacao(df_brasil)
                    if self.output_type == "csv":
                        self.loader.save(df_brasil, "populacao_brasil")

                    results["brasil"] = len(df_brasil)
                    logger.info(f"Registros Brasil: {len(df_brasil)}")

                # Extrair população por estado
                logger.info("-" * 40)
                logger.info("Extraindo população por estado...")
                df_estados = extractor.extract_por_estado(anos=anos)

                if not df_estados.empty:
                    df_estados = self.cleaner.clean_populacao(df_estados)
                    if self.output_type == "csv":
                        self.loader.save(df_estados, "populacao_estados")

                    results["estados"] = len(df_estados)
                    logger.info(f"Registros Estados: {len(df_estados)}")

        except Exception as e:
            logger.error(f"Erro no ETL de população: {str(e)}")
            self.stats["erros"] += 1
            raise

        elapsed = (datetime.now() - start_time).total_seconds()
        total = sum(results.values())

        logger.info("=" * 60)
        logger.info(f"ETL POPULAÇÃO CONCLUÍDO | total={total} | tempo={elapsed:.2f}s")
        logger.info("=" * 60)

        self.stats["extraidos"] += total
        self.stats["carregados"] += total

        return results

    def run_pib(self, anos: Optional[str] = None) -> dict:
        """
        Executa ETL de dados de PIB.

        Args:
            anos: Anos específicos ou None para todos

        Returns:
            Estatísticas da execução
        """
        logger.info("=" * 60)
        logger.info("INICIANDO ETL: PIB")
        logger.info("=" * 60)

        start_time = datetime.now()
        results = {"estados": 0, "percapita": 0}

        try:
            with PIBExtractor(self.client) as extractor:
                # Extrair PIB por estado
                logger.info("-" * 40)
                logger.info("Extraindo PIB por estado...")
                df_pib = extractor.extract_pib_por_estado(anos=anos)

                if not df_pib.empty:
                    df_pib = self.cleaner.clean_pib(df_pib)
                    if self.output_type == "csv":
                        self.loader.save(df_pib, "pib_estados")

                    results["estados"] = len(df_pib)
                    logger.info(f"Registros PIB: {len(df_pib)}")

                # Extrair PIB per capita
                logger.info("-" * 40)
                logger.info("Extraindo PIB per capita por estado...")
                df_percapita = extractor.extract_pib_percapita_por_estado(anos=anos)

                if not df_percapita.empty:
                    df_percapita = self.cleaner.clean_pib(df_percapita)
                    if self.output_type == "csv":
                        self.loader.save(df_percapita, "pib_percapita_estados")

                    results["percapita"] = len(df_percapita)
                    logger.info(f"Registros PIB per capita: {len(df_percapita)}")

        except Exception as e:
            logger.error(f"Erro no ETL de PIB: {str(e)}")
            self.stats["erros"] += 1
            raise

        elapsed = (datetime.now() - start_time).total_seconds()
        total = sum(results.values())

        logger.info("=" * 60)
        logger.info(f"ETL PIB CONCLUÍDO | total={total} | tempo={elapsed:.2f}s")
        logger.info("=" * 60)

        self.stats["extraidos"] += total
        self.stats["carregados"] += total

        return results

    def run_all(self, anos: Optional[str] = None) -> dict:
        """
        Executa pipeline completo (localidades + população + PIB).

        Args:
            anos: Anos para dados de população e PIB

        Returns:
            Estatísticas consolidadas
        """
        logger.info("#" * 60)
        logger.info("# INICIANDO PIPELINE ETL COMPLETO")
        logger.info("#" * 60)

        start_time = datetime.now()

        results = {
            "localidades": self.run_localidades(),
            "populacao": self.run_populacao(anos=anos),
            "pib": self.run_pib(anos=anos)
        }

        elapsed = (datetime.now() - start_time).total_seconds()

        logger.info("#" * 60)
        logger.info("# PIPELINE ETL CONCLUÍDO")
        logger.info(f"# Tempo total: {elapsed:.2f}s")
        logger.info(f"# Extraídos: {self.stats['extraidos']}")
        logger.info(f"# Carregados: {self.stats['carregados']}")
        logger.info(f"# Erros: {self.stats['erros']}")
        logger.info("#" * 60)

        return results

    def close(self) -> None:
        """Fecha conexões."""
        self.client.close()
        if hasattr(self.loader, "close"):
            self.loader.close()


def main():
    """Função principal do CLI."""
    parser = argparse.ArgumentParser(
        description="Pipeline ETL - Dados Socioeconômicos do IBGE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py --extract localidades
  python main.py --extract populacao --anos 2020|2021|2022
  python main.py --extract all --output csv
  python main.py --extract all --output database

Dados extraídos:
  - localidades: Regiões, estados e municípios do Brasil
  - populacao: Estimativas populacionais (IBGE)
  - pib: PIB municipal e per capita
  - all: Todos os dados acima
        """
    )

    parser.add_argument(
        "--extract",
        choices=["localidades", "populacao", "pib", "all"],
        default="all",
        help="Tipo de dados a extrair (default: all)"
    )

    parser.add_argument(
        "--output",
        choices=["csv", "database"],
        default="csv",
        help="Destino dos dados (default: csv)"
    )

    parser.add_argument(
        "--anos",
        type=str,
        default=None,
        help="Anos para população e PIB (ex: 2020|2021|2022)"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Nível de log (default: INFO)"
    )

    args = parser.parse_args()

    # Configurar logging
    setup_logger(
        log_level=args.log_level,
        log_file="logs/etl.log"
    )

    logger.info(f"Iniciando ETL | extract={args.extract} | output={args.output}")

    # Executar pipeline
    pipeline = ETLPipeline(output_type=args.output)

    try:
        if args.extract == "localidades":
            pipeline.run_localidades()
        elif args.extract == "populacao":
            pipeline.run_populacao(anos=args.anos)
        elif args.extract == "pib":
            pipeline.run_pib(anos=args.anos)
        else:  # all
            pipeline.run_all(anos=args.anos)

        logger.info("Pipeline finalizado com sucesso!")
        return 0

    except Exception as e:
        logger.error(f"Erro no pipeline: {str(e)}")
        return 1

    finally:
        pipeline.close()


if __name__ == "__main__":
    sys.exit(main())
