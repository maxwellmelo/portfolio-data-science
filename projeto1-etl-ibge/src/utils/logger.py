"""
Configuração de logging para o projeto ETL IBGE.
Utiliza loguru para logging estruturado e colorido.
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional

# Remove o handler padrão
logger.remove()


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "1 week"
) -> None:
    """
    Configura o logger global do projeto.

    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho para arquivo de log (opcional)
        rotation: Tamanho para rotação do arquivo
        retention: Tempo de retenção dos logs
    """
    # Formato para console (colorido)
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Formato para arquivo (sem cores)
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    # Handler para console
    logger.add(
        sys.stderr,
        format=console_format,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # Handler para arquivo (se especificado)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            str(log_path),
            format=file_format,
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            backtrace=True,
            diagnose=True
        )


def get_logger(name: str = __name__):
    """
    Retorna um logger configurado para o módulo especificado.

    Args:
        name: Nome do módulo (use __name__)

    Returns:
        Logger configurado
    """
    return logger.bind(name=name)


# Configuração padrão ao importar
setup_logger()
