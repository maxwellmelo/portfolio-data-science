"""
Limpeza e transformação de dados.
Responsável por normalizar e preparar dados para o carregamento.
"""

import pandas as pd
import numpy as np
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataCleaner:
    """
    Classe para limpeza e transformação de dados.

    Métodos para:
    - Normalizar strings
    - Tratar valores nulos
    - Converter tipos de dados
    - Remover duplicatas
    """

    @staticmethod
    def normalize_string(df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """
        Normaliza colunas de string (strip, title case).

        Args:
            df: DataFrame com dados
            columns: Lista de colunas a normalizar

        Returns:
            DataFrame com strings normalizadas
        """
        df = df.copy()

        for col in columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                # Não aplicar title() em siglas
                if "sigla" not in col.lower():
                    df[col] = df[col].str.title()

        logger.debug(f"Strings normalizadas nas colunas: {columns}")
        return df

    @staticmethod
    def convert_numeric(
        df: pd.DataFrame,
        columns: list,
        fill_na: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Converte colunas para tipo numérico.

        Args:
            df: DataFrame com dados
            columns: Lista de colunas a converter
            fill_na: Valor para preencher nulos (None = manter NaN)

        Returns:
            DataFrame com colunas convertidas
        """
        df = df.copy()

        for col in columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

                if fill_na is not None:
                    df[col] = df[col].fillna(fill_na)

        logger.debug(f"Colunas convertidas para numérico: {columns}")
        return df

    @staticmethod
    def remove_duplicates(
        df: pd.DataFrame,
        subset: Optional[list] = None,
        keep: str = "first"
    ) -> pd.DataFrame:
        """
        Remove registros duplicados.

        Args:
            df: DataFrame com dados
            subset: Colunas para verificar duplicatas (None = todas)
            keep: 'first', 'last' ou False

        Returns:
            DataFrame sem duplicatas
        """
        initial_count = len(df)
        df = df.drop_duplicates(subset=subset, keep=keep)
        removed = initial_count - len(df)

        if removed > 0:
            logger.info(f"Removidas {removed} linhas duplicadas")

        return df

    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame,
        strategy: dict
    ) -> pd.DataFrame:
        """
        Trata valores ausentes de acordo com estratégia por coluna.

        Args:
            df: DataFrame com dados
            strategy: Dicionário {coluna: 'drop'|'fill_zero'|'fill_mean'|valor}

        Returns:
            DataFrame com valores tratados
        """
        df = df.copy()

        for col, action in strategy.items():
            if col not in df.columns:
                continue

            if action == "drop":
                df = df.dropna(subset=[col])
            elif action == "fill_zero":
                df[col] = df[col].fillna(0)
            elif action == "fill_mean":
                df[col] = df[col].fillna(df[col].mean())
            elif action == "fill_median":
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(action)

        logger.debug(f"Valores ausentes tratados: {list(strategy.keys())}")
        return df

    @staticmethod
    def add_metadata(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona colunas de metadados ao DataFrame.

        Args:
            df: DataFrame original

        Returns:
            DataFrame com colunas de metadados
        """
        df = df.copy()

        df["extracted_at"] = pd.Timestamp.now()
        df["source"] = "IBGE"

        return df

    @classmethod
    def clean_localidades(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline de limpeza para dados de localidades.

        Args:
            df: DataFrame com dados de localidades

        Returns:
            DataFrame limpo
        """
        logger.info("Iniciando limpeza de dados de localidades")

        # Normalizar strings
        string_cols = [c for c in df.columns if "nome" in c.lower()]
        df = cls.normalize_string(df, string_cols)

        # Converter IDs para inteiro
        id_cols = [c for c in df.columns if "id" in c.lower()]
        df = cls.convert_numeric(df, id_cols)

        # Remover duplicatas
        df = cls.remove_duplicates(df)

        # Adicionar metadados
        df = cls.add_metadata(df)

        logger.info(f"Limpeza concluída | registros={len(df)}")
        return df

    @classmethod
    def clean_populacao(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline de limpeza para dados de população.

        Args:
            df: DataFrame com dados populacionais

        Returns:
            DataFrame limpo
        """
        logger.info("Iniciando limpeza de dados de população")

        # Converter valores numéricos
        df = cls.convert_numeric(df, ["valor", "ano"])

        # Remover valores negativos ou zero
        initial = len(df)
        df = df[df["valor"] > 0]
        removed = initial - len(df)
        if removed > 0:
            logger.warning(f"Removidos {removed} registros com valor <= 0")

        # Remover duplicatas (mesmo local e ano)
        df = cls.remove_duplicates(df, subset=["localidade_id", "ano"])

        # Adicionar metadados
        df = cls.add_metadata(df)

        logger.info(f"Limpeza concluída | registros={len(df)}")
        return df

    @classmethod
    def clean_pib(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline de limpeza para dados de PIB.

        Args:
            df: DataFrame com dados de PIB

        Returns:
            DataFrame limpo
        """
        logger.info("Iniciando limpeza de dados de PIB")

        # Converter valores numéricos
        df = cls.convert_numeric(df, ["valor", "ano"])

        # Remover duplicatas (mesmo local, ano e variável)
        df = cls.remove_duplicates(
            df,
            subset=["localidade_id", "ano", "variavel_id"]
        )

        # Adicionar metadados
        df = cls.add_metadata(df)

        logger.info(f"Limpeza concluída | registros={len(df)}")
        return df
