"""
Carregador de dados para a API - Sistema Integrado Multissetorial.

Gerencia dados reais (IBGE) e sinteticos (Saude, Educacao, Assistencia).
Dados reais tem prioridade quando disponiveis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List
from loguru import logger
from dataclasses import dataclass


@dataclass
class DataSource:
    """Informacoes sobre a fonte de dados."""
    name: str
    is_real: bool
    source: str
    records: int
    years: list
    setor: str = ""


class DataLoader:
    """
    Carregador de dados multissetoriais do Piaui.

    Integra dados de:
    - Economia (IBGE - dados reais)
    - Saude (DATASUS - simulados)
    - Educacao (INEP - simulados)
    - Assistencia Social (MDS - simulados)
    """

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(__file__).parent.parent.parent
        self.real_data_path = self.base_path / "data" / "real"
        self.multissetorial_path = self.base_path / "data" / "multissetorial"
        self.synthetic_data_path = self.base_path / "data" / "processed"

        self._cache: Dict[str, pd.DataFrame] = {}
        self._sources: Dict[str, DataSource] = {}
        self._integrated_cache: Optional[pd.DataFrame] = None

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

        # PIB e Populacao (economia_completo.csv tem PIB + Populacao mergeados)
        economia_path = self.real_data_path / "economia_completo.csv"
        if not economia_path.exists():
            economia_path = self.real_data_path / "economia_real.csv"

        if economia_path.exists():
            df = self._load_csv(economia_path)
            if df is not None:
                # Calcular PIB per capita se nao existir
                if 'pib_per_capita' not in df.columns and 'populacao_estimada' in df.columns:
                    df['pib_per_capita'] = (df['pib_total_mil_reais'] * 1000) / df['populacao_estimada']

                real_data['economia_pib'] = df
                self._sources['economia_pib'] = DataSource(
                    name="PIB Municipal",
                    is_real=True,
                    source="IBGE - SIDRA",
                    records=len(df),
                    years=sorted(df['ano'].unique().tolist()),
                    setor="economia"
                )

        # Populacao (separado)
        populacao_path = self.real_data_path / "populacao.csv"
        if populacao_path.exists():
            df = self._load_csv(populacao_path)
            if df is not None:
                real_data['populacao'] = df
                self._sources['populacao'] = DataSource(
                    name="Populacao Estimada",
                    is_real=True,
                    source="IBGE - SIDRA",
                    records=len(df),
                    years=sorted(df['ano'].unique().tolist()),
                    setor="demografia"
                )

        return real_data

    def load_multissetorial_data(self) -> Dict[str, pd.DataFrame]:
        """Carrega dados multissetoriais (Saude, Educacao, Assistencia)."""
        multi_data = {}

        # Se nao existirem os arquivos, gerar usando o extrator
        if not self.multissetorial_path.exists():
            logger.info("Gerando dados multissetoriais...")
            self._generate_multissetorial_data()

        # Saude
        saude_path = self.multissetorial_path / "indicadores_saude.csv"
        if saude_path.exists():
            df = self._load_csv(saude_path)
            if df is not None:
                multi_data['saude'] = df
                self._sources['saude'] = DataSource(
                    name="Indicadores de Saude",
                    is_real=False,
                    source="DATASUS (simulado)",
                    records=len(df),
                    years=sorted(df['ano'].unique().tolist()),
                    setor="saude"
                )

        # Educacao
        educacao_path = self.multissetorial_path / "indicadores_educacao.csv"
        if educacao_path.exists():
            df = self._load_csv(educacao_path)
            if df is not None:
                multi_data['educacao'] = df
                self._sources['educacao'] = DataSource(
                    name="Indicadores de Educacao",
                    is_real=False,
                    source="INEP (simulado)",
                    records=len(df),
                    years=sorted(df['ano'].unique().tolist()),
                    setor="educacao"
                )

        # Assistencia Social
        assistencia_path = self.multissetorial_path / "indicadores_assistencia.csv"
        if assistencia_path.exists():
            df = self._load_csv(assistencia_path)
            if df is not None:
                multi_data['assistencia'] = df
                self._sources['assistencia'] = DataSource(
                    name="Indicadores de Assistencia Social",
                    is_real=False,
                    source="MDS (simulado)",
                    records=len(df),
                    years=sorted(df['ano'].unique().tolist()),
                    setor="assistencia_social"
                )

        # Dataset integrado
        integrado_path = self.multissetorial_path / "dados_integrados.csv"
        if integrado_path.exists():
            df = self._load_csv(integrado_path)
            if df is not None:
                multi_data['integrado'] = df
                self._integrated_cache = df
                self._sources['integrado'] = DataSource(
                    name="Dados Integrados Multissetoriais",
                    is_real=False,
                    source="IBGE + DATASUS + INEP + MDS",
                    records=len(df),
                    years=[2021],
                    setor="multissetorial"
                )

        return multi_data

    def _generate_multissetorial_data(self):
        """Gera dados multissetoriais usando o extrator."""
        try:
            import sys
            sys.path.insert(0, str(self.base_path / "src"))
            from extractors.multissetorial_extractor import MultissetorialExtractor

            extractor = MultissetorialExtractor()
            extractor.extract_all(save_dir=str(self.multissetorial_path))
        except Exception as e:
            logger.error(f"Erro ao gerar dados multissetoriais: {e}")

    def load_synthetic_data(self, generator) -> Dict[str, pd.DataFrame]:
        """Carrega dados sinteticos do gerador."""
        logger.info("Gerando dados sinteticos...")
        return generator.generate_all()

    def load_all(self, generator=None) -> Dict[str, pd.DataFrame]:
        """
        Carrega todos os dados, priorizando reais sobre sinteticos.

        Returns:
            Dicionario com todos os datasets
        """
        if self._cache:
            return self._cache

        # 1. Carregar dados reais primeiro (IBGE)
        real_data = self.load_real_data()
        logger.info(f"Dados reais carregados: {list(real_data.keys())}")

        # 2. Carregar dados multissetoriais (Saude, Educacao, Assistencia)
        multi_data = self.load_multissetorial_data()
        logger.info(f"Dados multissetoriais carregados: {list(multi_data.keys())}")

        # 3. Carregar dados sinteticos adicionais (se fornecido gerador)
        synthetic_data = {}
        if generator:
            synthetic_data = self.load_synthetic_data(generator)
            for name, df in synthetic_data.items():
                if name not in self._sources:
                    self._sources[name] = DataSource(
                        name=name,
                        is_real=False,
                        source="Dados Sinteticos (Faker)",
                        records=len(df),
                        years=sorted(df['ano'].unique().tolist()) if 'ano' in df.columns else [],
                        setor="outros"
                    )

        # 4. Combinar (reais sobrescrevem sinteticos)
        self._cache = {**synthetic_data, **multi_data, **real_data}

        # Log resumo
        logger.info("=" * 50)
        logger.info("DADOS CARREGADOS:")
        for name, source in self._sources.items():
            status = "REAL" if source.is_real else "SIMULADO"
            logger.info(f"  [{status}] {name}: {source.records} registros ({source.setor})")
        logger.info("=" * 50)

        return self._cache

    def get_data_sources(self) -> Dict[str, dict]:
        """Retorna informacoes sobre as fontes de dados."""
        return {
            name: {
                "nome": source.name,
                "dados_reais": source.is_real,
                "fonte": source.source,
                "registros": source.records,
                "anos_disponiveis": source.years,
                "setor": source.setor
            }
            for name, source in self._sources.items()
        }

    def get_pib_data(self, municipio_id: int = None, ano: int = None) -> pd.DataFrame:
        """Retorna dados de PIB, priorizando dados reais."""
        if 'economia_pib' not in self._cache:
            return pd.DataFrame()

        df = self._cache['economia_pib'].copy()

        if municipio_id:
            df = df[df['municipio_id'] == municipio_id]
        if ano:
            df = df[df['ano'] == ano]

        return df

    def get_populacao_data(self, municipio_id: int = None, ano: int = None) -> pd.DataFrame:
        """Retorna dados de populacao."""
        if 'populacao' not in self._cache:
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

    def get_saude_data(self, municipio_id: int = None, ano: int = None) -> pd.DataFrame:
        """Retorna dados de saude."""
        if 'saude' not in self._cache:
            return pd.DataFrame()

        df = self._cache['saude'].copy()

        if municipio_id:
            df = df[df['municipio_id'] == municipio_id]
        if ano:
            df = df[df['ano'] == ano]

        return df

    def get_educacao_data(self, municipio_id: int = None, ano: int = None) -> pd.DataFrame:
        """Retorna dados de educacao."""
        if 'educacao' not in self._cache:
            return pd.DataFrame()

        df = self._cache['educacao'].copy()

        if municipio_id:
            df = df[df['municipio_id'] == municipio_id]
        if ano:
            df = df[df['ano'] == ano]

        return df

    def get_assistencia_data(self, municipio_id: int = None, ano: int = None) -> pd.DataFrame:
        """Retorna dados de assistencia social."""
        if 'assistencia' not in self._cache:
            return pd.DataFrame()

        df = self._cache['assistencia'].copy()

        if municipio_id:
            df = df[df['municipio_id'] == municipio_id]
        if ano:
            df = df[df['ano'] == ano]

        return df

    def get_integrated_data(self) -> pd.DataFrame:
        """Retorna dataset integrado com todos os indicadores."""
        if 'integrado' not in self._cache:
            return pd.DataFrame()
        return self._cache['integrado'].copy()

    def get_municipio_completo(self, municipio_id: int) -> dict:
        """
        Retorna todos os indicadores de um municipio especifico.

        Args:
            municipio_id: Codigo IBGE do municipio

        Returns:
            Dicionario com indicadores de todos os setores
        """
        result = {
            "municipio_id": municipio_id,
            "setores": {}
        }

        # Economia
        df_eco = self.get_pib_data(municipio_id=municipio_id)
        if not df_eco.empty:
            result["setores"]["economia"] = df_eco.to_dict('records')

        # Saude
        df_saude = self.get_saude_data(municipio_id=municipio_id)
        if not df_saude.empty:
            result["setores"]["saude"] = df_saude.to_dict('records')

        # Educacao
        df_edu = self.get_educacao_data(municipio_id=municipio_id)
        if not df_edu.empty:
            result["setores"]["educacao"] = df_edu.to_dict('records')

        # Assistencia
        df_assist = self.get_assistencia_data(municipio_id=municipio_id)
        if not df_assist.empty:
            result["setores"]["assistencia_social"] = df_assist.to_dict('records')

        # Integrado (snapshot 2021)
        df_int = self.get_integrated_data()
        if not df_int.empty:
            mun_data = df_int[df_int['municipio_id'] == municipio_id]
            if not mun_data.empty:
                result["perfil_integrado"] = mun_data.iloc[0].to_dict()

        return result

    def get_correlacao_indicadores(self, indicadores: List[str] = None) -> pd.DataFrame:
        """
        Calcula correlacao entre indicadores de diferentes setores.

        Args:
            indicadores: Lista de indicadores para correlacionar

        Returns:
            DataFrame com matriz de correlacao
        """
        df = self.get_integrated_data()
        if df.empty:
            return pd.DataFrame()

        if indicadores is None:
            # Indicadores padrao para correlacao
            indicadores = [
                'mortalidade_infantil', 'cobertura_vacinal',
                'ideb_anos_iniciais', 'ideb_anos_finais',
                'taxa_pobreza_estimada'
            ]

        # Adicionar PIB se disponivel
        if 'economia_pib' in self._cache:
            df_pib = self._cache['economia_pib']
            df_pib_2021 = df_pib[df_pib['ano'] == 2021][['municipio_id', 'pib_per_capita']].copy()
            if 'pib_per_capita' in df_pib_2021.columns:
                df = df.merge(df_pib_2021, on='municipio_id', how='left')
                if 'pib_per_capita' not in indicadores:
                    indicadores.append('pib_per_capita')

        # Filtrar colunas disponiveis
        cols_disponiveis = [c for c in indicadores if c in df.columns]

        if len(cols_disponiveis) < 2:
            return pd.DataFrame()

        return df[cols_disponiveis].corr()

    def get_municipios_prioritarios(
        self,
        criterio: str = "vulnerabilidade",
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        Identifica municipios prioritarios para investimento.

        Args:
            criterio: 'vulnerabilidade', 'saude', 'educacao', 'economia'
            top_n: Numero de municipios a retornar

        Returns:
            DataFrame com municipios prioritarios
        """
        df = self.get_integrated_data()
        if df.empty:
            return pd.DataFrame()

        if criterio == "vulnerabilidade":
            # Ordenar por indice de vulnerabilidade (maior primeiro)
            df_sorted = df.sort_values('indice_vulnerabilidade', ascending=False)
        elif criterio == "saude":
            # Alta mortalidade infantil + baixa cobertura vacinal
            df['prioridade_saude'] = (
                df['mortalidade_infantil'] / df['mortalidade_infantil'].max() +
                (1 - df['cobertura_vacinal'] / 100)
            ) / 2
            df_sorted = df.sort_values('prioridade_saude', ascending=False)
        elif criterio == "educacao":
            # Baixo IDEB
            df['prioridade_educacao'] = 1 - (df['ideb_anos_iniciais'] / 10)
            df_sorted = df.sort_values('prioridade_educacao', ascending=False)
        elif criterio == "economia":
            # Alta taxa de pobreza
            df_sorted = df.sort_values('taxa_pobreza_estimada', ascending=False)
        else:
            df_sorted = df.sort_values('indice_vulnerabilidade', ascending=False)

        return df_sorted.head(top_n)

    def get_comparativo_mesorregioes(self) -> pd.DataFrame:
        """
        Calcula medias dos indicadores por mesorregiao.

        Returns:
            DataFrame com comparativo entre mesorregioes
        """
        df = self.get_integrated_data()
        if df.empty:
            return pd.DataFrame()

        indicadores_numericos = [
            'mortalidade_infantil', 'cobertura_vacinal',
            'ideb_anos_iniciais', 'ideb_anos_finais',
            'taxa_pobreza_estimada', 'populacao_estimada'
        ]

        cols_disponiveis = [c for c in indicadores_numericos if c in df.columns]

        return df.groupby('mesorregiao')[cols_disponiveis].mean().round(2)

    def is_real_data(self, dataset_name: str) -> bool:
        """Verifica se o dataset contem dados reais."""
        return self._sources.get(dataset_name, DataSource("", False, "", 0, [])).is_real


# Instancia global
_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    """Retorna instancia singleton do DataLoader."""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader
