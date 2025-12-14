"""Testes para os extratores de dados."""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors import SyntheticDataGenerator


class TestSyntheticDataGenerator:
    """Testes para o gerador de dados sintéticos."""

    @pytest.fixture
    def generator(self):
        """Fixture para criar instância do gerador."""
        return SyntheticDataGenerator()

    def test_generator_initialization(self, generator):
        """Testa inicialização do gerador."""
        assert generator is not None
        assert hasattr(generator, 'municipios')
        assert len(generator.municipios) > 0

    def test_generate_all(self, generator):
        """Testa geração de todos os datasets."""
        datasets = generator.generate_all()

        assert isinstance(datasets, dict)
        assert len(datasets) > 0

        expected_datasets = ['mortalidade', 'nascimentos', 'escolas', 'ideb', 'pib_municipal', 'cadunico']
        for name in expected_datasets:
            assert name in datasets, f"Dataset '{name}' não encontrado"
            assert isinstance(datasets[name], pd.DataFrame)
            assert len(datasets[name]) > 0

    def test_generate_mortalidade(self, generator):
        """Testa geração de dados de mortalidade."""
        df = generator.generate_mortalidade()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        required_cols = ['municipio_id', 'municipio_nome', 'ano', 'obitos_totais', 'taxa_mortalidade_infantil']
        for col in required_cols:
            assert col in df.columns, f"Coluna '{col}' não encontrada"

        # Verificar tipos de dados
        assert df['ano'].dtype in ['int64', 'int32']
        assert df['obitos_totais'].dtype in ['int64', 'int32']

    def test_generate_nascimentos(self, generator):
        """Testa geração de dados de nascimentos."""
        df = generator.generate_nascimentos()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        required_cols = ['municipio_id', 'municipio_nome', 'ano', 'nascidos_vivos', 'partos_normais', 'partos_cesareos']
        for col in required_cols:
            assert col in df.columns

    def test_generate_escolas(self, generator):
        """Testa geração de dados de escolas."""
        df = generator.generate_escolas()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        required_cols = ['municipio_id', 'municipio_nome', 'codigo_escola', 'nome_escola', 'tipo_escola', 'rede']
        for col in required_cols:
            assert col in df.columns

        # Verificar valores válidos
        assert all(df['rede'].isin(['Municipal', 'Estadual', 'Federal', 'Privada']))

    def test_generate_ideb(self, generator):
        """Testa geração de dados do IDEB."""
        df = generator.generate_ideb()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        required_cols = ['municipio_id', 'municipio_nome', 'ano', 'nivel_ensino', 'ideb']
        for col in required_cols:
            assert col in df.columns

        # IDEB deve estar entre 0 e 10
        assert df['ideb'].min() >= 0
        assert df['ideb'].max() <= 10

    def test_generate_pib(self, generator):
        """Testa geração de dados de PIB."""
        df = generator.generate_pib_municipal()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        required_cols = ['municipio_id', 'municipio_nome', 'ano', 'pib_total_mil_reais', 'pib_per_capita', 'populacao']
        for col in required_cols:
            assert col in df.columns

        # PIB deve ser positivo
        assert df['pib_total_mil_reais'].min() > 0

    def test_generate_cadunico(self, generator):
        """Testa geração de dados do CadÚnico."""
        df = generator.generate_cadunico()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        required_cols = ['municipio_id', 'municipio_nome', 'ano', 'familias_cadastradas', 'familias_extrema_pobreza']
        for col in required_cols:
            assert col in df.columns

    def test_data_consistency(self, generator):
        """Testa consistência entre datasets."""
        datasets = generator.generate_all()

        # Todos os datasets devem ter os mesmos municípios
        municipios_base = set(datasets['mortalidade']['municipio_id'].unique())

        for name, df in datasets.items():
            if 'municipio_id' in df.columns:
                municipios_atual = set(df['municipio_id'].unique())
                assert municipios_base == municipios_atual, f"Municípios diferentes em '{name}'"


class TestDataQuality:
    """Testes de qualidade dos dados gerados."""

    @pytest.fixture
    def datasets(self):
        """Fixture para gerar todos os datasets."""
        generator = SyntheticDataGenerator()
        return generator.generate_all()

    def test_no_null_ids(self, datasets):
        """Verifica que não há IDs nulos."""
        for name, df in datasets.items():
            if 'municipio_id' in df.columns:
                assert df['municipio_id'].notna().all(), f"IDs nulos em '{name}'"

    def test_no_negative_values(self, datasets):
        """Verifica que não há valores negativos em colunas de contagem."""
        count_cols = ['obitos_totais', 'nascidos_vivos', 'total_alunos', 'familias_cadastradas', 'populacao']

        for name, df in datasets.items():
            for col in count_cols:
                if col in df.columns:
                    assert (df[col] >= 0).all(), f"Valores negativos em '{name}.{col}'"

    def test_valid_years(self, datasets):
        """Verifica que os anos estão em faixas válidas."""
        for name, df in datasets.items():
            if 'ano' in df.columns:
                assert df['ano'].min() >= 2010, f"Anos muito antigos em '{name}'"
                assert df['ano'].max() <= 2024, f"Anos futuros em '{name}'"
