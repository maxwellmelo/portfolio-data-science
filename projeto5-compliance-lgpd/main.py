"""
Sistema de Compliance LGPD - Script Principal.

Ferramenta CLI para auditoria de dados pessoais.

Uso:
    python main.py scan <arquivo.csv>
    python main.py scan <arquivo.csv> --report
    python main.py anonymize <arquivo.csv> --config config.json
    python main.py --help
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
from loguru import logger

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.scanners import PIIScanner, ScanResult
from src.anonymizers import DataAnonymizer
from src.reporters import LGPDReporter


def setup_logging(level: str = "INFO") -> None:
    """Configura logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level=level
    )


def scan_file(filepath: str, generate_report: bool = False) -> ScanResult:
    """
    Escaneia um arquivo em busca de dados pessoais.

    Args:
        filepath: Caminho do arquivo
        generate_report: Se deve gerar relatório HTML

    Returns:
        ScanResult com descobertas
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

    # Carregar dados
    logger.info(f"Carregando arquivo: {filepath}")

    if path.suffix == ".csv":
        df = pd.read_csv(filepath)
    elif path.suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(filepath)
    elif path.suffix == ".parquet":
        df = pd.read_parquet(filepath)
    else:
        raise ValueError(f"Formato não suportado: {path.suffix}")

    logger.info(f"Arquivo carregado: {len(df)} linhas, {len(df.columns)} colunas")

    # Escanear
    scanner = PIIScanner()
    result = scanner.scan(df, source_name=path.name)

    # Exibir resultados
    print("\n" + "=" * 60)
    print("RESULTADO DO SCAN DE DADOS PESSOAIS")
    print("=" * 60)
    print(f"Arquivo: {path.name}")
    print(f"Linhas: {result.total_rows:,}")
    print(f"Colunas analisadas: {result.columns_scanned}")
    print(f"PIIs encontrados: {len(result.pii_found)}")
    print(f"\nResumo de Risco:")

    for level, count in result.risk_summary.items():
        if count > 0:
            print(f"  - {level.upper()}: {count}")

    if result.pii_found:
        print("\nDetalhes:")
        for pii in result.pii_found:
            print(f"  [{pii.risk_level.value.upper()}] {pii.column}: {pii.pii_type.value} ({pii.count} ocorrências)")

    print("\nRecomendações:")
    for rec in result.recommendations:
        print(f"  • {rec}")

    # Gerar relatório se solicitado
    if generate_report:
        reporter = LGPDReporter()
        report_path = reporter.generate_audit_report([result])
        print(f"\nRelatório gerado: {report_path}")

    return result


def anonymize_file(
    filepath: str,
    config_path: str = None,
    output_path: str = None
) -> str:
    """
    Anonimiza dados de um arquivo.

    Args:
        filepath: Arquivo de entrada
        config_path: Arquivo de configuração JSON
        output_path: Caminho de saída

    Returns:
        Caminho do arquivo anonimizado
    """
    import json

    path = Path(filepath)

    # Carregar dados
    if path.suffix == ".csv":
        df = pd.read_csv(filepath)
    elif path.suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(filepath)
    else:
        raise ValueError(f"Formato não suportado: {path.suffix}")

    # Carregar configuração
    if config_path:
        with open(config_path) as f:
            config = json.load(f)
    else:
        # Configuração padrão baseada em scan
        scanner = PIIScanner()
        result = scanner.scan(df, source_name=path.name)

        config = {}
        for pii in result.pii_found:
            if pii.risk_level.value in ["critico", "alto"]:
                config[pii.column] = {"method": "hash", "truncate": 12}
            elif pii.risk_level.value == "medio":
                config[pii.column] = {"method": "mask"}
            else:
                config[pii.column] = {"method": "generalize"}

    # Anonimizar
    anonymizer = DataAnonymizer()
    df_anon = anonymizer.anonymize_dataframe(df, config)

    # Salvar
    if output_path is None:
        output_path = path.parent / f"{path.stem}_anonimizado{path.suffix}"

    if str(output_path).endswith(".csv"):
        df_anon.to_csv(output_path, index=False)
    else:
        df_anon.to_excel(output_path, index=False)

    logger.info(f"Arquivo anonimizado salvo: {output_path}")
    print(f"\nArquivo anonimizado: {output_path}")
    print(f"Colunas processadas: {len(config)}")

    return str(output_path)


def generate_sample_data(output_path: str = "data/input/sample_data.csv") -> str:
    """Gera dados de exemplo para teste."""
    from faker import Faker
    import numpy as np

    fake = Faker('pt_BR')

    df = pd.DataFrame({
        "id": range(1, 101),
        "nome_completo": [fake.name() for _ in range(100)],
        "cpf": [fake.cpf() for _ in range(100)],
        "email": [fake.email() for _ in range(100)],
        "telefone": [fake.phone_number() for _ in range(100)],
        "endereco": [fake.address().replace("\n", ", ") for _ in range(100)],
        "data_nascimento": [fake.date_of_birth().strftime("%d/%m/%Y") for _ in range(100)],
        "salario": [round(np.random.uniform(1500, 20000), 2) for _ in range(100)],
        "cargo": [fake.job() for _ in range(100)],
        "departamento": [np.random.choice(["TI", "RH", "Financeiro", "Comercial", "Operações"]) for _ in range(100)]
    })

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

    print(f"Dados de exemplo gerados: {path}")
    return str(path)


def main():
    """Função principal do CLI."""
    parser = argparse.ArgumentParser(
        description="Sistema de Compliance LGPD - Auditoria de Dados Pessoais",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py scan dados.csv
  python main.py scan dados.csv --report
  python main.py anonymize dados.csv
  python main.py anonymize dados.csv --config config.json
  python main.py generate-sample
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Comando: scan
    scan_parser = subparsers.add_parser("scan", help="Escanear arquivo em busca de PII")
    scan_parser.add_argument("file", help="Arquivo a escanear (CSV, XLSX, Parquet)")
    scan_parser.add_argument("--report", action="store_true", help="Gerar relatório HTML")

    # Comando: anonymize
    anon_parser = subparsers.add_parser("anonymize", help="Anonimizar dados")
    anon_parser.add_argument("file", help="Arquivo a anonimizar")
    anon_parser.add_argument("--config", help="Arquivo de configuração JSON")
    anon_parser.add_argument("--output", help="Caminho do arquivo de saída")

    # Comando: generate-sample
    subparsers.add_parser("generate-sample", help="Gerar dados de exemplo")

    # Argumentos globais
    parser.add_argument("--log-level", default="INFO", help="Nível de log")

    args = parser.parse_args()

    setup_logging(args.log_level)

    print("\n" + "=" * 60)
    print("SISTEMA DE COMPLIANCE LGPD")
    print(f"Versão: {settings.version}")
    print("=" * 60)

    if args.command == "scan":
        scan_file(args.file, args.report)

    elif args.command == "anonymize":
        anonymize_file(args.file, args.config, args.output)

    elif args.command == "generate-sample":
        generate_sample_data()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
