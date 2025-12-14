"""
Carregamento de dados para arquivos CSV.
Alternativa ao banco de dados para persistência local.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import pandas as pd

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVLoader:
    """
    Carregador de dados para arquivos CSV.

    Útil para:
    - Persistência local sem banco de dados
    - Backup de dados extraídos
    - Compartilhamento de dados processados
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Inicializa o loader.

        Args:
            output_dir: Diretório de saída (usa data/processed por padrão)
        """
        self.output_dir = Path(output_dir or f"{settings.etl.data_dir}/processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"CSVLoader inicializado | output_dir={self.output_dir}")

    def _generate_filename(self, name: str, timestamp: bool = True) -> str:
        """
        Gera nome de arquivo com timestamp opcional.

        Args:
            name: Nome base do arquivo
            timestamp: Se deve incluir timestamp

        Returns:
            Nome do arquivo
        """
        if timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{name}_{ts}.csv"
        return f"{name}.csv"

    def save(
        self,
        df: pd.DataFrame,
        name: str,
        timestamp: bool = False,
        index: bool = False,
        **kwargs
    ) -> Path:
        """
        Salva DataFrame como CSV.

        Args:
            df: DataFrame a salvar
            name: Nome base do arquivo
            timestamp: Se deve incluir timestamp no nome
            index: Se deve incluir índice
            **kwargs: Argumentos adicionais para to_csv()

        Returns:
            Caminho do arquivo salvo
        """
        filename = self._generate_filename(name, timestamp)
        filepath = self.output_dir / filename

        df.to_csv(filepath, index=index, **kwargs)

        logger.info(f"Arquivo salvo: {filepath} | registros={len(df)}")
        return filepath

    def save_regioes(self, df: pd.DataFrame) -> Path:
        """Salva dados de regiões."""
        return self.save(df, "regioes", encoding="utf-8-sig")

    def save_estados(self, df: pd.DataFrame) -> Path:
        """Salva dados de estados."""
        return self.save(df, "estados", encoding="utf-8-sig")

    def save_municipios(self, df: pd.DataFrame) -> Path:
        """Salva dados de municípios."""
        return self.save(df, "municipios", encoding="utf-8-sig")

    def save_populacao(self, df: pd.DataFrame) -> Path:
        """Salva dados de população."""
        return self.save(df, "populacao", timestamp=True, encoding="utf-8-sig")

    def save_pib(self, df: pd.DataFrame) -> Path:
        """Salva dados de PIB."""
        return self.save(df, "pib", timestamp=True, encoding="utf-8-sig")

    def load(self, filename: str, **kwargs) -> pd.DataFrame:
        """
        Carrega DataFrame de arquivo CSV.

        Args:
            filename: Nome do arquivo
            **kwargs: Argumentos adicionais para read_csv()

        Returns:
            DataFrame carregado
        """
        filepath = self.output_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

        df = pd.read_csv(filepath, **kwargs)
        logger.info(f"Arquivo carregado: {filepath} | registros={len(df)}")

        return df

    def list_files(self, pattern: str = "*.csv") -> list:
        """
        Lista arquivos no diretório de saída.

        Args:
            pattern: Padrão glob para filtrar arquivos

        Returns:
            Lista de caminhos de arquivos
        """
        return list(self.output_dir.glob(pattern))
