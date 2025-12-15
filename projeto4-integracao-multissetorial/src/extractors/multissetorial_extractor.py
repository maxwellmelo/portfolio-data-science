"""
Extrator de Dados Multissetoriais do Piaui.

Gera dados sinteticos realistas baseados em estatisticas oficiais do Piaui para:
- Saude (DATASUS): Mortalidade infantil, cobertura vacinal, infraestrutura
- Educacao (INEP): IDEB, escolas, matriculas, aprovacao
- Assistencia Social (MDS): CadUnico, beneficios

Os valores sao calibrados com base em dados reais do IBGE, DATASUS e INEP.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger
from datetime import datetime
import random

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import MUNICIPIOS_PIAUI


class MultissetorialExtractor:
    """
    Extrator de dados multissetoriais do Piaui.

    Gera dados sinteticos calibrados com estatisticas reais:
    - Mortalidade infantil PI (media ~15 por mil nascidos vivos)
    - IDEB PI (media ~4.5 anos iniciais, ~4.0 anos finais)
    - Cobertura vacinal (media ~75%)
    """

    # Estatisticas reais do Piaui para calibracao
    ESTATISTICAS_REAIS = {
        'mortalidade_infantil_media': 15.2,  # por mil nascidos vivos (2022)
        'mortalidade_infantil_std': 5.0,
        'cobertura_vacinal_media': 75.0,     # percentual (2023)
        'cobertura_vacinal_std': 12.0,
        'ideb_anos_iniciais_media': 4.8,     # 2021
        'ideb_anos_iniciais_std': 0.8,
        'ideb_anos_finais_media': 4.2,       # 2021
        'ideb_anos_finais_std': 0.7,
        'taxa_aprovacao_media': 0.88,        # percentual
        'taxa_aprovacao_std': 0.08,
    }

    # Mesorregioes do Piaui para variacoes regionais
    MESORREGIOES = {
        'Norte Piauiense': [2200053, 2200103, 2200251, 2200277, 2200459, 2200509, 2200608,
                           2200707, 2200806, 2200905, 2201002, 2201051, 2201101, 2201150],
        'Centro-Norte Piauiense': [2200202, 2200301, 2200400, 2201200, 2201309, 2201408,
                                   2201507, 2201606, 2201705, 2201804, 2201903, 2202000,
                                   2202109, 2202208, 2202307, 2211001],  # Inclui Teresina
        'Sudoeste Piauiense': [2201919, 2201929, 2201945, 2201960, 2201988, 2202026,
                              2202059, 2202075, 2202083, 2202091, 2202117, 2202133],
        'Sudeste Piauiense': [2201556, 2201572, 2201739, 2201770, 2202174, 2202251,
                             2202406, 2202455, 2202505, 2202539, 2202554, 2208007],  # Inclui Picos
    }

    def __init__(self, seed: int = 42):
        """
        Inicializa o extrator.

        Args:
            seed: Semente para reproducibilidade
        """
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        self.municipios = MUNICIPIOS_PIAUI

        # Gera fatores de ajuste por municipio (baseado em tamanho/desenvolvimento)
        self._generate_municipal_factors()

        logger.info(f"MultissetorialExtractor inicializado | {len(self.municipios)} municipios")

    def _generate_municipal_factors(self):
        """Gera fatores de ajuste por municipio para realismo."""
        self.municipal_factors = {}

        # Municipios maiores/mais desenvolvidos
        grandes = [2211001, 2207702, 2208007, 2203909, 2208403]  # Teresina, Parnaiba, Picos, Floriano, Piripiri
        medios = [2200400, 2202208, 2207009, 2200509, 2201200]   # Altos, Campo Maior, Oeiras, Amarante, Barras

        for mun_id in self.municipios.keys():
            if mun_id in grandes:
                # Municipios grandes: melhores indicadores
                self.municipal_factors[mun_id] = {
                    'saude': 1.15,    # 15% melhor em saude
                    'educacao': 1.12, # 12% melhor em educacao
                    'economia': 1.20  # 20% melhor em economia
                }
            elif mun_id in medios:
                self.municipal_factors[mun_id] = {
                    'saude': 1.05,
                    'educacao': 1.05,
                    'economia': 1.08
                }
            else:
                # Municipios pequenos: variacoes maiores
                self.municipal_factors[mun_id] = {
                    'saude': np.random.uniform(0.85, 1.10),
                    'educacao': np.random.uniform(0.88, 1.08),
                    'economia': np.random.uniform(0.80, 1.05)
                }

    def _get_mesorregiao(self, municipio_id: int) -> str:
        """Retorna mesorregiao do municipio."""
        for meso, municipios in self.MESORREGIOES.items():
            if municipio_id in municipios:
                return meso
        return 'Centro-Norte Piauiense'  # Default

    def extract_saude(self, anos: List[int] = None) -> pd.DataFrame:
        """
        Extrai indicadores de saude (simulados baseados em DATASUS).

        Indicadores:
        - Mortalidade infantil (por mil nascidos vivos)
        - Cobertura vacinal (%)
        - Leitos SUS por 1000 hab
        - Estabelecimentos de saude

        Args:
            anos: Lista de anos

        Returns:
            DataFrame com indicadores de saude por municipio/ano
        """
        if anos is None:
            anos = [2019, 2020, 2021, 2022, 2023]

        logger.info(f"Gerando indicadores de saude para {len(self.municipios)} municipios...")

        records = []

        for mun_id, mun_nome in self.municipios.items():
            factor = self.municipal_factors[mun_id]['saude']
            mesorregiao = self._get_mesorregiao(mun_id)

            for ano in anos:
                # Tendencia de melhoria ao longo dos anos
                trend_factor = 1 - (ano - 2019) * 0.02

                # Mortalidade infantil (menor eh melhor, entao invertemos o factor)
                mort_inf = max(5.0, np.random.normal(
                    self.ESTATISTICAS_REAIS['mortalidade_infantil_media'] / factor * trend_factor,
                    self.ESTATISTICAS_REAIS['mortalidade_infantil_std']
                ))

                # Cobertura vacinal
                cob_vac = min(98.0, max(50.0, np.random.normal(
                    self.ESTATISTICAS_REAIS['cobertura_vacinal_media'] * factor,
                    self.ESTATISTICAS_REAIS['cobertura_vacinal_std']
                )))

                # COVID impactou cobertura em 2020-2021
                if ano in [2020, 2021]:
                    cob_vac *= 0.92

                # Leitos SUS por 1000 habitantes (media Brasil ~2.0)
                leitos = max(0.5, np.random.normal(1.8 * factor, 0.5))

                # Estabelecimentos de saude (proporcional ao tamanho)
                if mun_id == 2211001:  # Teresina
                    estab = np.random.randint(800, 1200)
                elif mun_id in [2207702, 2208007, 2203909]:  # Grandes
                    estab = np.random.randint(80, 150)
                else:
                    estab = np.random.randint(5, 40)

                records.append({
                    'municipio_id': mun_id,
                    'municipio_nome': mun_nome,
                    'mesorregiao': mesorregiao,
                    'ano': ano,
                    'mortalidade_infantil': round(mort_inf, 2),
                    'cobertura_vacinal': round(cob_vac, 2),
                    'leitos_sus_por_1000hab': round(leitos, 2),
                    'estabelecimentos_saude': estab,
                    'fonte': 'DATASUS (simulado)'
                })

        df = pd.DataFrame(records)
        logger.info(f"Saude extraida: {len(df)} registros")
        return df

    def extract_educacao(self, anos: List[int] = None) -> pd.DataFrame:
        """
        Extrai indicadores de educacao (simulados baseados em INEP).

        Indicadores:
        - IDEB anos iniciais (1-5 ano)
        - IDEB anos finais (6-9 ano)
        - Taxa de aprovacao
        - Total de escolas
        - Total de matriculas

        Args:
            anos: Lista de anos (IDEB eh bienal: 2017, 2019, 2021, 2023)

        Returns:
            DataFrame com indicadores de educacao por municipio/ano
        """
        if anos is None:
            anos = [2017, 2019, 2021, 2023]  # IDEB eh bienal

        logger.info(f"Gerando indicadores de educacao para {len(self.municipios)} municipios...")

        records = []

        for mun_id, mun_nome in self.municipios.items():
            factor = self.municipal_factors[mun_id]['educacao']
            mesorregiao = self._get_mesorregiao(mun_id)

            for ano in anos:
                # Tendencia de melhoria no IDEB
                trend_bonus = (ano - 2017) * 0.08

                # IDEB anos iniciais (escala 0-10, PI media ~4.8)
                ideb_ai = min(8.0, max(2.5, np.random.normal(
                    self.ESTATISTICAS_REAIS['ideb_anos_iniciais_media'] * factor + trend_bonus,
                    self.ESTATISTICAS_REAIS['ideb_anos_iniciais_std']
                )))

                # IDEB anos finais (escala 0-10, PI media ~4.2)
                ideb_af = min(7.5, max(2.0, np.random.normal(
                    self.ESTATISTICAS_REAIS['ideb_anos_finais_media'] * factor + trend_bonus * 0.8,
                    self.ESTATISTICAS_REAIS['ideb_anos_finais_std']
                )))

                # Taxa de aprovacao
                taxa_aprov = min(0.99, max(0.65, np.random.normal(
                    self.ESTATISTICAS_REAIS['taxa_aprovacao_media'] * factor,
                    self.ESTATISTICAS_REAIS['taxa_aprovacao_std']
                )))

                # Total de escolas (proporcional ao tamanho)
                if mun_id == 2211001:  # Teresina
                    escolas = np.random.randint(400, 600)
                    matriculas = np.random.randint(200000, 280000)
                elif mun_id in [2207702, 2208007, 2203909, 2208403]:  # Grandes
                    escolas = np.random.randint(50, 100)
                    matriculas = np.random.randint(15000, 40000)
                else:
                    escolas = np.random.randint(5, 30)
                    matriculas = np.random.randint(800, 8000)

                records.append({
                    'municipio_id': mun_id,
                    'municipio_nome': mun_nome,
                    'mesorregiao': mesorregiao,
                    'ano': ano,
                    'ideb_anos_iniciais': round(ideb_ai, 2),
                    'ideb_anos_finais': round(ideb_af, 2),
                    'taxa_aprovacao': round(taxa_aprov, 4),
                    'total_escolas': escolas,
                    'total_matriculas': matriculas,
                    'fonte': 'INEP (simulado)'
                })

        df = pd.DataFrame(records)
        logger.info(f"Educacao extraida: {len(df)} registros")
        return df

    def extract_assistencia_social(self, anos: List[int] = None) -> pd.DataFrame:
        """
        Extrai indicadores de assistencia social (simulados baseados em MDS).

        Indicadores:
        - Familias no CadUnico
        - Beneficiarios Bolsa Familia/Auxilio Brasil
        - Taxa de pobreza estimada

        Args:
            anos: Lista de anos

        Returns:
            DataFrame com indicadores de assistencia social
        """
        if anos is None:
            anos = [2019, 2020, 2021, 2022, 2023]

        logger.info(f"Gerando indicadores de assistencia social para {len(self.municipios)} municipios...")

        records = []

        # Piaui tem ~27% de pobreza (um dos mais altos do Brasil)
        taxa_pobreza_base = 0.27

        for mun_id, mun_nome in self.municipios.items():
            factor = self.municipal_factors[mun_id]['economia']
            mesorregiao = self._get_mesorregiao(mun_id)

            for ano in anos:
                # Populacao estimada (simplificado)
                if mun_id == 2211001:  # Teresina
                    pop = np.random.randint(850000, 880000)
                elif mun_id in [2207702, 2208007, 2203909]:
                    pop = np.random.randint(100000, 160000)
                else:
                    pop = np.random.randint(3000, 30000)

                # Taxa de pobreza (inverso do factor economico)
                taxa_pobreza = min(0.60, max(0.10, np.random.normal(
                    taxa_pobreza_base / factor,
                    0.08
                )))

                # Aumento de beneficiarios em 2020 (pandemia)
                if ano >= 2020:
                    taxa_pobreza *= 1.08

                # Familias no CadUnico (proporcional a pobreza)
                familias_cadunico = int(pop * 0.28 * taxa_pobreza / 0.27)

                # Beneficiarios do programa social
                beneficiarios = int(familias_cadunico * np.random.uniform(0.75, 0.90))

                records.append({
                    'municipio_id': mun_id,
                    'municipio_nome': mun_nome,
                    'mesorregiao': mesorregiao,
                    'ano': ano,
                    'familias_cadunico': familias_cadunico,
                    'beneficiarios_programa_social': beneficiarios,
                    'taxa_pobreza_estimada': round(taxa_pobreza, 4),
                    'populacao_estimada': pop,
                    'fonte': 'MDS (simulado)'
                })

        df = pd.DataFrame(records)
        logger.info(f"Assistencia Social extraida: {len(df)} registros")
        return df

    def extract_all(self, save_dir: str = "data/multissetorial") -> Dict[str, pd.DataFrame]:
        """
        Extrai todos os dados multissetoriais.

        Args:
            save_dir: Diretorio para salvar os CSVs

        Returns:
            Dicionario com DataFrames
        """
        logger.info("Iniciando extracao de dados multissetoriais...")

        datasets = {}

        # Saude
        logger.info("=" * 50)
        logger.info("Extraindo SAUDE...")
        df_saude = self.extract_saude()
        datasets["indicadores_saude"] = df_saude

        # Educacao
        logger.info("=" * 50)
        logger.info("Extraindo EDUCACAO...")
        df_educacao = self.extract_educacao()
        datasets["indicadores_educacao"] = df_educacao

        # Assistencia Social
        logger.info("=" * 50)
        logger.info("Extraindo ASSISTENCIA SOCIAL...")
        df_assist = self.extract_assistencia_social()
        datasets["indicadores_assistencia"] = df_assist

        # Criar dataset integrado (ano 2021 - mais completo)
        logger.info("=" * 50)
        logger.info("Criando dataset INTEGRADO...")
        df_integrado = self._create_integrated_dataset(datasets)
        datasets["dados_integrados"] = df_integrado

        # Salvar arquivos
        if save_dir:
            save_path = Path(save_dir)
            save_path.mkdir(parents=True, exist_ok=True)

            for name, df in datasets.items():
                filepath = save_path / f"{name}.csv"
                df.to_csv(filepath, index=False, encoding="utf-8-sig")
                logger.info(f"Salvo: {filepath} ({len(df)} registros)")

        total = sum(len(df) for df in datasets.values())
        logger.info(f"Extracao concluida! Total: {total} registros")

        return datasets

    def _create_integrated_dataset(self, datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Cria dataset integrado com todos os indicadores.

        Seleciona ano 2021 (mais completo) e junta todos os indicadores.
        """
        # Filtrar ano 2021 (disponivel em todos os datasets)
        df_saude = datasets["indicadores_saude"][
            datasets["indicadores_saude"]["ano"] == 2021
        ].copy()

        df_educacao = datasets["indicadores_educacao"][
            datasets["indicadores_educacao"]["ano"] == 2021
        ].copy()

        df_assist = datasets["indicadores_assistencia"][
            datasets["indicadores_assistencia"]["ano"] == 2021
        ].copy()

        # Merge progressivo
        df = df_saude[['municipio_id', 'municipio_nome', 'mesorregiao', 'ano',
                       'mortalidade_infantil', 'cobertura_vacinal',
                       'leitos_sus_por_1000hab', 'estabelecimentos_saude']].copy()

        df = df.merge(
            df_educacao[['municipio_id', 'ideb_anos_iniciais', 'ideb_anos_finais',
                        'taxa_aprovacao', 'total_escolas', 'total_matriculas']],
            on='municipio_id',
            how='left'
        )

        df = df.merge(
            df_assist[['municipio_id', 'familias_cadunico', 'beneficiarios_programa_social',
                      'taxa_pobreza_estimada', 'populacao_estimada']],
            on='municipio_id',
            how='left'
        )

        # Adicionar classificacao de vulnerabilidade
        df['indice_vulnerabilidade'] = self._calculate_vulnerability_index(df)
        df['classificacao_vulnerabilidade'] = pd.cut(
            df['indice_vulnerabilidade'],
            bins=[0, 0.3, 0.5, 0.7, 1.0],
            labels=['Baixa', 'Media', 'Alta', 'Muito Alta']
        )

        logger.info(f"Dataset integrado criado: {len(df)} municipios")
        return df

    def _calculate_vulnerability_index(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula indice de vulnerabilidade multidimensional.

        Combina indicadores de saude, educacao e assistencia social.
        Escala 0-1 (maior = mais vulneravel)
        """
        # Normalizar indicadores (0-1)
        def normalize(series, inverse=False):
            min_val = series.min()
            max_val = series.max()
            if max_val == min_val:
                return pd.Series([0.5] * len(series))
            normalized = (series - min_val) / (max_val - min_val)
            return 1 - normalized if inverse else normalized

        # Mortalidade infantil (maior = pior)
        mort_norm = normalize(df['mortalidade_infantil'])

        # Cobertura vacinal (maior = melhor, inverter)
        vac_norm = normalize(df['cobertura_vacinal'], inverse=True)

        # IDEB (maior = melhor, inverter)
        ideb_norm = normalize(df['ideb_anos_iniciais'], inverse=True)

        # Taxa de pobreza (maior = pior)
        pob_norm = normalize(df['taxa_pobreza_estimada'])

        # Indice ponderado
        indice = (
            mort_norm * 0.25 +    # 25% saude
            vac_norm * 0.15 +     # 15% saude
            ideb_norm * 0.30 +    # 30% educacao
            pob_norm * 0.30       # 30% economia
        )

        return indice


# Script de execucao
if __name__ == "__main__":
    extractor = MultissetorialExtractor()

    print("\n" + "=" * 60)
    print("EXTRATOR DE DADOS MULTISSETORIAIS - PIAUI")
    print("=" * 60)

    datasets = extractor.extract_all(save_dir="data/multissetorial")

    print("\n" + "=" * 60)
    print("RESUMO DOS DADOS EXTRAIDOS")
    print("=" * 60)

    for name, df in datasets.items():
        print(f"\n{name.upper()}:")
        print(f"  Registros: {len(df)}")
        print(f"  Colunas: {list(df.columns)}")
        if "municipio_id" in df.columns:
            print(f"  Municipios unicos: {df['municipio_id'].nunique()}")
        if "ano" in df.columns:
            print(f"  Anos: {sorted(df['ano'].unique())}")
