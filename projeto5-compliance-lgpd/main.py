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
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

import pandas as pd
from loguru import logger
from pydantic import BaseModel, field_validator, ValidationError

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings, PROJECT_ROOT
from src.scanners import PIIScanner, ScanResult
from src.anonymizers import DataAnonymizer, AnonymizationMethod
from src.reporters import LGPDReporter


# ========== Modelos de Validação de Configuração ==========

class ColumnConfig(BaseModel):
    """Configuração de anonimização para uma coluna."""
    method: str
    truncate: Optional[int] = None
    algorithm: Optional[str] = None
    visible_start: Optional[int] = None
    visible_end: Optional[int] = None
    mask_char: Optional[str] = None
    pattern: Optional[str] = None
    pii_type: Optional[str] = None
    noise_level: Optional[float] = None
    bins: Optional[int] = None
    labels: Optional[List[str]] = None
    prefix: Optional[str] = None
    replacement: Optional[Any] = None

    @field_validator('method')
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Valida se o método de anonimização é suportado."""
        valid_methods = [m.value for m in AnonymizationMethod]
        if v not in valid_methods:
            raise ValueError(
                f"Metodo '{v}' nao suportado. "
                f"Metodos validos: {', '.join(valid_methods)}"
            )
        return v

    @field_validator('truncate')
    @classmethod
    def validate_truncate(cls, v: Optional[int]) -> Optional[int]:
        """Valida valor de truncate."""
        if v is not None and v < 1:
            raise ValueError("truncate deve ser >= 1")
        return v

    @field_validator('noise_level')
    @classmethod
    def validate_noise_level(cls, v: Optional[float]) -> Optional[float]:
        """Valida nível de ruído."""
        if v is not None and (v < 0 or v > 1):
            raise ValueError("noise_level deve estar entre 0 e 1")
        return v


def validate_config(config: Dict[str, Any]) -> Dict[str, Dict]:
    """
    Valida configuração de anonimização completa.

    Args:
        config: Dicionário de configuração {coluna: {method: ..., ...}}

    Returns:
        Configuração validada

    Raises:
        ValidationError: Se a configuração for inválida
    """
    validated_config = {}
    errors = []

    for column, col_config in config.items():
        try:
            validated = ColumnConfig(**col_config)
            validated_config[column] = col_config
        except ValidationError as e:
            errors.append(f"Coluna '{column}': {e}")

    if errors:
        error_msg = "Erros de validacao na configuracao:\n" + "\n".join(errors)
        raise ValueError(error_msg)

    return validated_config


def load_config_file(config_path: str) -> Dict[str, Dict]:
    """
    Carrega e valida arquivo de configuração JSON.

    Args:
        config_path: Caminho do arquivo JSON

    Returns:
        Configuração validada

    Raises:
        FileNotFoundError: Se arquivo não existir
        json.JSONDecodeError: Se JSON for inválido
        ValueError: Se configuração for inválida
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo de configuracao nao encontrado: {config_path}")

    logger.info(f"Carregando configuracao: {config_path}")

    try:
        with open(path, encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"JSON invalido em {config_path}: {e.msg}",
            e.doc,
            e.pos
        )

    if not isinstance(config, dict):
        raise ValueError("Configuracao deve ser um dicionario {coluna: {method: ...}}")

    if not config:
        raise ValueError("Configuracao vazia")

    # Validar configuração
    validated_config = validate_config(config)

    logger.info(f"Configuracao validada: {len(validated_config)} colunas")

    return validated_config


# ========== Logging Estruturado ==========

def setup_logging(level: str = "INFO", log_to_file: bool = True) -> None:
    """
    Configura logging estruturado com saída para console e arquivo.

    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Se deve salvar logs em arquivo
    """
    logger.remove()

    # Console output
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level=level
    )

    # File output com rotação
    if log_to_file:
        log_dir = PROJECT_ROOT / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "lgpd_audit_{time:YYYY-MM-DD}.log"

        logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8"
        )

        # Log de auditoria separado
        audit_file = log_dir / "audit_trail_{time:YYYY-MM-DD}.log"
        logger.add(
            str(audit_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | AUDIT | {message}",
            level="INFO",
            rotation="10 MB",
            retention="90 days",
            filter=lambda record: "AUDIT" in record["message"]
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

    Raises:
        FileNotFoundError: Se arquivo não existir
        ValueError: Se formato não suportado ou config inválida
        json.JSONDecodeError: Se JSON da config for inválido
    """
    path = Path(filepath)

    if not path.exists():
        logger.error(f"Arquivo nao encontrado: {filepath}")
        raise FileNotFoundError(f"Arquivo nao encontrado: {filepath}")

    # Log de auditoria - início
    logger.info(f"AUDIT: Iniciando anonimizacao do arquivo {path.name}")

    # Carregar dados
    logger.info(f"Carregando arquivo: {filepath}")

    try:
        if path.suffix == ".csv":
            df = pd.read_csv(filepath)
        elif path.suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath)
        else:
            raise ValueError(f"Formato nao suportado: {path.suffix}")
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo: {e}")
        raise

    logger.info(f"Arquivo carregado: {len(df)} linhas, {len(df.columns)} colunas")

    # Carregar e validar configuração
    if config_path:
        try:
            config = load_config_file(config_path)
            logger.info(f"AUDIT: Usando configuracao do arquivo {config_path}")
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Erro na configuracao: {e}")
            raise
    else:
        # Configuração padrão baseada em scan
        logger.info("Gerando configuracao automatica baseada em scan...")
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

        logger.info(f"AUDIT: Configuracao automatica gerada para {len(config)} colunas")

    # Log das colunas que serão processadas
    for col, params in config.items():
        logger.info(f"AUDIT: Coluna '{col}' sera anonimizada com metodo '{params.get('method')}'")

    # Anonimizar
    anonymizer = DataAnonymizer()
    df_anon = anonymizer.anonymize_dataframe(df, config)

    # Salvar
    if output_path is None:
        output_path = path.parent / f"{path.stem}_anonimizado{path.suffix}"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if str(output_path).endswith(".csv"):
        df_anon.to_csv(output_path, index=False)
    else:
        df_anon.to_excel(output_path, index=False)

    # Log de auditoria - conclusão
    logger.info(f"AUDIT: Anonimizacao concluida. Arquivo salvo: {output_path}")
    logger.info(f"AUDIT: {len(config)} colunas processadas, {len(df)} registros anonimizados")

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
