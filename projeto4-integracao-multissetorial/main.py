"""
Sistema de Integração Multissetorial - Piauí.

Script principal para orquestração do pipeline ETL e API.

Uso:
    python main.py generate     # Gerar dados sintéticos
    python main.py api          # Iniciar API REST
    python main.py pipeline     # Executar pipeline ETL
"""

import argparse
import sys
from pathlib import Path

from loguru import logger

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings


def setup_logging(level: str = "INFO") -> None:
    """Configura logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level=level
    )
    logger.add(
        "logs/pipeline_{time}.log",
        rotation="10 MB",
        level="DEBUG"
    )


def generate_data() -> None:
    """Gera dados sintéticos multissetoriais."""
    from src.extractors import SyntheticDataGenerator
    import pandas as pd

    logger.info("Gerando dados sintéticos...")

    generator = SyntheticDataGenerator()
    datasets = generator.generate_all()

    # Salvar em arquivos
    output_dir = Path(settings.data_dir) / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, df in datasets.items():
        filepath = output_dir / f"{name}.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        logger.info(f"Salvo: {filepath} ({len(df)} registros)")

    total = sum(len(df) for df in datasets.values())
    print(f"\nDados gerados com sucesso!")
    print(f"Total: {total:,} registros em {len(datasets)} arquivos")
    print(f"Diretório: {output_dir}")


def start_api() -> None:
    """Inicia a API REST."""
    import uvicorn
    from src.api import app

    logger.info("Iniciando API REST...")

    print(f"\nAPI disponível em: http://{settings.api.host}:{settings.api.port}")
    print(f"Documentação: http://{settings.api.host}:{settings.api.port}/docs")

    uvicorn.run(
        app,
        host=settings.api.host,
        port=settings.api.port,
        log_level="info"
    )


def run_pipeline() -> None:
    """Executa pipeline ETL completo."""
    logger.info("Executando pipeline ETL...")

    # 1. Gerar/Extrair dados
    generate_data()

    # 2. Transformar (já feito no generator)
    logger.info("Transformações aplicadas durante a geração")

    # 3. Carregar (dados já salvos em CSV)
    logger.info("Dados carregados em arquivos CSV")

    print("\nPipeline ETL concluído!")
    print("Para consultar os dados, inicie a API: python main.py api")


def show_info() -> None:
    """Exibe informações do sistema."""
    from config.settings import FONTES_DADOS, MUNICIPIOS_PIAUI

    print("\n" + "=" * 60)
    print("SISTEMA DE INTEGRAÇÃO MULTISSETORIAL - PIAUÍ")
    print("=" * 60)

    print(f"\nVersão: {settings.version}")
    print(f"Ambiente: {settings.environment}")

    print("\nFontes de Dados Integradas:")
    for key, fonte in FONTES_DADOS.items():
        print(f"  • {fonte['nome']}: {fonte['descricao']}")
        print(f"    Datasets: {', '.join(fonte['datasets'][:2])}...")

    print(f"\nMunicípios Cobertos: {len(MUNICIPIOS_PIAUI)}")
    for codigo, nome in list(MUNICIPIOS_PIAUI.items())[:5]:
        print(f"  • {nome} ({codigo})")
    print("  ...")

    print("\nComandos Disponíveis:")
    print("  python main.py generate  - Gerar dados sintéticos")
    print("  python main.py api       - Iniciar API REST")
    print("  python main.py pipeline  - Executar pipeline ETL")


def main():
    """Função principal do CLI."""
    parser = argparse.ArgumentParser(
        description="Sistema de Integração Multissetorial - Piauí",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py generate     # Gerar dados sintéticos
  python main.py api          # Iniciar API REST na porta 8000
  python main.py pipeline     # Executar pipeline completo
  python main.py info         # Informações do sistema
        """
    )

    parser.add_argument(
        "command",
        choices=["generate", "api", "pipeline", "info"],
        nargs="?",
        default="info",
        help="Comando a executar"
    )

    parser.add_argument("--log-level", default="INFO", help="Nível de log")

    args = parser.parse_args()

    setup_logging(args.log_level)

    if args.command == "generate":
        generate_data()
    elif args.command == "api":
        start_api()
    elif args.command == "pipeline":
        run_pipeline()
    else:
        show_info()


if __name__ == "__main__":
    main()
