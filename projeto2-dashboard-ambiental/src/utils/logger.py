"""
Sistema de logging centralizado usando loguru
Fornece logging estruturado, rotação de arquivos e formatação customizada
"""

import sys
from pathlib import Path
from loguru import logger

# Diretório de logs
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Remover handler padrão do loguru
logger.remove()

# Configurar formato customizado
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Handler para console (stdout) - apenas INFO e acima
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level="INFO",
    colorize=True,
    backtrace=True,
    diagnose=True
)

# Handler para arquivo geral - todos os níveis
logger.add(
    LOGS_DIR / "dashboard_{time:YYYY-MM-DD}.log",
    format=LOG_FORMAT,
    level="DEBUG",
    rotation="500 MB",  # Rotação quando arquivo atinge 500MB
    retention="30 days",  # Manter logs por 30 dias
    compression="zip",  # Comprimir logs antigos
    backtrace=True,
    diagnose=True
)

# Handler para erros - apenas WARNING e acima
logger.add(
    LOGS_DIR / "errors_{time:YYYY-MM-DD}.log",
    format=LOG_FORMAT,
    level="WARNING",
    rotation="100 MB",
    retention="60 days",
    compression="zip",
    backtrace=True,
    diagnose=True
)


def get_logger(name: str = None):
    """
    Retorna instância do logger configurado

    Args:
        name: Nome do módulo/componente para identificação nos logs

    Returns:
        Logger configurado

    Example:
        >>> from utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Aplicação iniciada")
    """
    if name:
        return logger.bind(name=name)
    return logger


# Exportar logger padrão
__all__ = ['logger', 'get_logger']
