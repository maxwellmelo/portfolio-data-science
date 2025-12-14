"""
Classe base para extratores de dados.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
from loguru import logger


class BaseExtractor(ABC):
    """
    Classe abstrata base para extratores de dados.

    Define interface comum para todos os extratores:
    - DATASUS
    - INEP
    - IBGE
    - MDS
    """

    def __init__(self, source_name: str):
        """
        Inicializa o extrator.

        Args:
            source_name: Nome da fonte de dados
        """
        self.source_name = source_name
        self.metadata = {
            "source": source_name,
            "extracted_at": None,
            "record_count": 0,
            "status": "pending"
        }

    @abstractmethod
    def extract(self, **kwargs) -> pd.DataFrame:
        """
        Extrai dados da fonte.

        Returns:
            DataFrame com dados extraídos
        """
        pass

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool:
        """
        Valida dados extraídos.

        Args:
            df: DataFrame a validar

        Returns:
            True se válido
        """
        pass

    def _update_metadata(self, df: pd.DataFrame, status: str = "success") -> None:
        """Atualiza metadados da extração."""
        self.metadata["extracted_at"] = datetime.now().isoformat()
        self.metadata["record_count"] = len(df)
        self.metadata["status"] = status

    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados da última extração."""
        return self.metadata.copy()


class DataSUSExtractor(BaseExtractor):
    """Extrator para dados do DATASUS."""

    def __init__(self):
        super().__init__("DATASUS")

    def extract(self, dataset: str = "SIM", **kwargs) -> pd.DataFrame:
        """Extrai dados do DATASUS."""
        logger.info(f"Extração DATASUS não implementada (usar dados sintéticos)")
        return pd.DataFrame()

    def validate(self, df: pd.DataFrame) -> bool:
        return len(df) > 0


class INEPExtractor(BaseExtractor):
    """Extrator para dados do INEP."""

    def __init__(self):
        super().__init__("INEP")

    def extract(self, dataset: str = "censo_escolar", **kwargs) -> pd.DataFrame:
        """Extrai dados do INEP."""
        logger.info(f"Extração INEP não implementada (usar dados sintéticos)")
        return pd.DataFrame()

    def validate(self, df: pd.DataFrame) -> bool:
        return len(df) > 0


class IBGEExtractor(BaseExtractor):
    """Extrator para dados do IBGE."""

    def __init__(self):
        super().__init__("IBGE")

    def extract(self, dataset: str = "pib", **kwargs) -> pd.DataFrame:
        """Extrai dados do IBGE."""
        logger.info(f"Extração IBGE não implementada (usar dados sintéticos)")
        return pd.DataFrame()

    def validate(self, df: pd.DataFrame) -> bool:
        return len(df) > 0
