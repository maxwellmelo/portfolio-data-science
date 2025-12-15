"""
Carregador de dados para a API.

Gerencia dados reais (IBGE) e sintéticos.
Dados reais têm prioridade quando disponíveis.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from loguru import logger
from dataclasses import dataclass


@dataclass
class DataSource:
    """Informações sobre a fonte de dados."""
    name: str
    is_real: bool
    source: str
    records: int
    years: list


class DataLoader:
    """
    Carregador de dados que combina fontes reais e sintéticas.

    Prioriza dados reais do IBGE quando disponíveis,
    usa dados sintéticos como fallback.
    """

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(__file__).parent.parent.parent
        self.real_data_path = self.base_path / "data" / "real"
        self.synthetic_data_path = self.base_path / "data" / "processed"

        self._cache: Dict[str, pd.DataFrame] = {}
        self._sources: Dict[str, DataSource] = {}

        logger.info(f"DataLoader inicializado | base_path={self.base_path}")

    def _load_csv(self, filepath: Path) -> Optional[pd.DataFrame]:
        """Carrega arquivo CSV se existir."""
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                logger.info(f"Carregado: {filepath.name} ({len(df)} registros)")
                return df
            except Exception as e:
                logger.error(f"Erro ao carregar {filepath}: {e}")
        return None

    def load_real_data(self) -> Dict[str, pd.DataFrame]:
        """Carrega dados reais do IBGE."""
        real_data = {}

        # PIB e População (economia_completo.csv tem PIB + População já mergeados)
        economia_path = self.real_data_path / "economia_completo.csv"
        if not economia_path.exists():
            economia_path = self.real_data_path / "economia_real.csv"

        if economia_path.exists():
            df = self._load_csv(economia_path)
            if df is not None:
                # Calcular PIB per capita se não existir
                if 'pib_per_capita' not in df.columns and 'populacao_estimada' in df.columns:
                    df['pib_per_capita'] = (df['pib_total_mil_reais'] * 1000) / df['populacao_estimada']

                real_data['economia_pib'] = df
                self._sources['economia_pib'] = DataSource(
                    name="PIB Municipal",
                    is_real=True,
                    source="IBGE - SIDRA",
                    records=len(df),
                    years=sorted(df['ano'].unique().tolist())
                )

        # População (separado)
        populacao_path = self.real_data_path / "populacao.csv"
        if populacao_path.exists():
            df = self._load_csv(populacao_path)
            if df is not None:
                real_data['populacao'] = df
                self._sources['populacao'] = DataSource(
                    name="População Estimada",
                    is_real=True,
                    source="IBGE - SIDRA",
                    records=len(df),
                    years=sorted(df['ano'].unique().tolist())
                )

        return real_data

    def load_synthetic_data(self, generator) -> Dict[str, pd.DataFrame]:
        """Carrega dados sintéticos do gerador."""
        logger.info("Gerando dados sintéticos...")
        return generator.generate_all()

    def load_all(self, generator=None) -> Dict[str, pd.DataFrame]:
        """
        Carrega todos os dados, priorizando reais sobre sintéticos.

        Returns:
            Dicionário com todos os datasets
        """
        if self._cache:
            return self._cache

        # 1. Carregar dados reais primeiro
        real_data = self.load_real_data()
        logger.info(f"Dados reais carregados: {list(real_data.keys())}")

        # 2. Carregar dados sintéticos
        synthetic_data = {}
        if generator:
            synthetic_data = self.load_synthetic_data(generator)

            # Registrar fontes sintéticas
            for name, df in synthetic_data.items():
                if name not in self._sources:
                    self._sources[name] = DataSource(
                        name=name,
                        is_real=False,
                        source="Dados Sintéticos (Faker)",
                        records=len(df),
                        years=sorted(df['ano'].unique().tolist()) if 'ano' in df.columns else []
                    )

        # 3. Combinar (reais sobrescrevem sintéticos)
        self._cache = {**synthetic_data, **real_data}

        # Log resumo
        logger.info("=" * 50)
        logger.info("DADOS CARREGADOS:")
        for name, source in self._sources.items():
            status = "REAL" if source.is_real else "SINTETICO"
            logger.info(f"  [{status}] {name}: {source.records} registros")
        logger.info("=" * 50)

        return self._cache

    def get_data_sources(self) -> Dict[str, dict]:
        """Retorna informações sobre as fontes de dados."""
        return {
            name: {
                "nome": source.name,
                "dados_reais": source.is_real,
                "fonte": source.source,
                "registros": source.records,
                "anos_disponiveis": source.years
            }
            for name, source in self._sources.items()
        }

    def get_pib_data(self, municipio_id: int = None, ano: int = None) -> pd.DataFrame:
        """
        Retorna dados de PIB, priorizando dados reais.
        """
        if 'economia_pib' not in self._cache:
            return pd.DataFrame()

        df = self._cache['economia_pib'].copy()

        if municipio_id:
            df = df[df['municipio_id'] == municipio_id]
        if ano:
            df = df[df['ano'] == ano]

        return df

    def get_populacao_data(self, municipio_id: int = None, ano: int = None) -> pd.DataFrame:
        """Retorna dados de população."""
        if 'populacao' not in self._cache:
            # Tentar obter de economia_pib
            if 'economia_pib' in self._cache and 'populacao_estimada' in self._cache['economia_pib'].columns:
                df = self._cache['economia_pib'][['municipio_id', 'municipio_nome', 'ano', 'populacao_estimada']].copy()
            else:
                return pd.DataFrame()
        else:
            df = self._cache['populacao'].copy()

        if municipio_id:
            df = df[df['municipio_id'] == municipio_id]
        if ano:
            df = df[df['ano'] == ano]

        return df

    def is_real_data(self, dataset_name: str) -> bool:
        """Verifica se o dataset contém dados reais."""
        return self._sources.get(dataset_name, DataSource("", False, "", 0, [])).is_real


# Instância global
_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    """Retorna instância singleton do DataLoader."""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader
