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
        # Deve ter todos os 224 municípios do Piauí
        assert len(generator.municipios) == 224

    def test_generate_all(self, generator):
        """Testa geração de todos os datasets."""
        datasets = generator.generate_all()

        assert isinstance(datasets, dict)
        assert len(datasets) > 0

        # Nomes corretos dos datasets
        expected_datasets = [
            'saude_mortalidade',
            'saude_nascimentos',
            'educacao_escolas',
            'educacao_ideb',
            'economia_pib',
            'assistencia_cadunico'
        ]
        for name in expected_datasets:
            assert name in datasets, f"Dataset '{name}' não encontrado"
            assert isinstance(datasets[name], pd.DataFrame)
            assert len(datasets[name]) > 0

    def test_generate_saude_mortalidade(self, generator):
        """Testa geração de dados de mortalidade."""
        df = generator.generate_saude_mortalidade(n_records=100)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100

        # Colunas reais do gerador (dados em nível de registro)
        required_cols = [
            'id_obito', 'data_obito', 'municipio_id', 'municipio_nome',
            'uf', 'idade', 'sexo', 'raca_cor', 'escolaridade',
            'cid_principal', 'causa_basica', 'local_obito', 'ano'
        ]
        for col in required_cols:
            assert col in df.columns, f"Coluna '{col}' não encontrada"

        # Verificar tipos de dados
        assert df['ano'].dtype in ['int64', 'int32']
        assert df['idade'].dtype in ['int64', 'int32']

        # Verificar valores válidos
        assert all(df['sexo'].isin(['M', 'F']))
        assert all(df['idade'] >= 0)
        assert all(df['idade'] <= 110)

    def test_generate_saude_nascimentos(self, generator):
        """Testa geração de dados de nascimentos."""
        df = generator.generate_saude_nascimentos(n_records=100)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100

        # Colunas reais do gerador
        required_cols = [
            'id_nascimento', 'data_nascimento', 'municipio_id', 'municipio_nome',
            'uf', 'sexo', 'peso_nascer', 'semanas_gestacao', 'tipo_parto',
            'idade_mae', 'escolaridade_mae', 'estado_civil_mae',
            'consultas_prenatal', 'apgar_1min', 'apgar_5min', 'ano'
        ]
        for col in required_cols:
            assert col in df.columns, f"Coluna '{col}' não encontrada"

        # Verificar valores válidos
        assert all(df['tipo_parto'].isin(['Vaginal', 'Cesáreo']))
        assert all(df['peso_nascer'] >= 500)
        assert all(df['peso_nascer'] <= 5500)
        assert all(df['semanas_gestacao'] >= 22)
        assert all(df['semanas_gestacao'] <= 42)

    def test_generate_educacao_escolas(self, generator):
        """Testa geração de dados de escolas."""
        df = generator.generate_educacao_escolas(n_records=100)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100

        # Colunas reais do gerador
        required_cols = [
            'id_escola', 'nome_escola', 'municipio_id', 'municipio_nome',
            'uf', 'dependencia_administrativa', 'localizacao', 'total_alunos',
            'total_docentes', 'total_funcionarios', 'educacao_infantil',
            'ensino_fundamental', 'ensino_medio', 'eja', 'ano'
        ]
        for col in required_cols:
            assert col in df.columns, f"Coluna '{col}' não encontrada"

        # Verificar valores válidos
        assert all(df['dependencia_administrativa'].isin(['Estadual', 'Municipal', 'Privada', 'Federal']))
        assert all(df['localizacao'].isin(['Urbana', 'Rural']))
        assert all(df['total_alunos'] >= 20)

    def test_generate_educacao_ideb(self, generator):
        """Testa geração de dados do IDEB."""
        df = generator.generate_educacao_ideb()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        # Colunas reais do gerador
        required_cols = [
            'municipio_id', 'municipio_nome', 'uf', 'ano', 'etapa_ensino',
            'rede', 'ideb', 'meta_projetada', 'taxa_aprovacao',
            'nota_matematica', 'nota_portugues'
        ]
        for col in required_cols:
            assert col in df.columns, f"Coluna '{col}' não encontrada"

        # IDEB deve estar entre 2 e 8 (conforme gerador)
        assert df['ideb'].min() >= 2.0
        assert df['ideb'].max() <= 8.0

        # Verificar valores válidos
        assert all(df['etapa_ensino'].isin(['Anos Iniciais', 'Anos Finais', 'Ensino Médio']))
        assert all(df['rede'].isin(['Estadual', 'Municipal']))

    def test_generate_economia_pib(self, generator):
        """Testa geração de dados de PIB."""
        df = generator.generate_economia_pib()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        # Colunas reais do gerador
        required_cols = [
            'municipio_id', 'municipio_nome', 'uf', 'ano',
            'pib_total_mil_reais', 'pib_agropecuaria_mil_reais',
            'pib_industria_mil_reais', 'pib_servicos_mil_reais',
            'pib_adm_publica_mil_reais', 'populacao_estimada', 'pib_per_capita'
        ]
        for col in required_cols:
            assert col in df.columns, f"Coluna '{col}' não encontrada"

        # PIB deve ser positivo
        assert df['pib_total_mil_reais'].min() > 0
        assert df['populacao_estimada'].min() > 0
        assert df['pib_per_capita'].min() > 0

    def test_generate_assistencia_cadunico(self, generator):
        """Testa geração de dados do CadÚnico."""
        df = generator.generate_assistencia_cadunico(n_records=100)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100

        # Colunas reais do gerador
        required_cols = [
            'id_familia', 'data_cadastro', 'data_atualizacao',
            'municipio_id', 'municipio_nome', 'uf', 'qtd_membros_familia',
            'renda_per_capita', 'faixa_renda', 'situacao_domicilio',
            'tipo_domicilio', 'agua_canalizada', 'energia_eletrica',
            'esgoto_sanitario', 'coleta_lixo', 'recebe_bolsa_familia',
            'recebe_bpc', 'ano'
        ]
        for col in required_cols:
            assert col in df.columns, f"Coluna '{col}' não encontrada"

        # Verificar valores válidos
        assert all(df['faixa_renda'].isin([
            'Extrema pobreza', 'Pobreza', 'Baixa renda', 'Acima de meio SM'
        ]))
        assert all(df['qtd_membros_familia'] >= 1)
        assert all(df['renda_per_capita'] >= 0)

    def test_data_consistency_municipios(self, generator):
        """Testa consistência de municípios entre datasets."""
        datasets = generator.generate_all()

        # Verificar que todos os datasets têm municipio_id válidos
        for name, df in datasets.items():
            if 'municipio_id' in df.columns:
                invalid_municipios = df[~df['municipio_id'].isin(generator.municipios.keys())]
                assert len(invalid_municipios) == 0, f"Municípios inválidos em '{name}'"

    def test_data_structure_consistency(self):
        """Testa que estrutura dos dados é consistente entre gerações."""
        gen1 = SyntheticDataGenerator(seed=123)
        gen2 = SyntheticDataGenerator(seed=456)

        df1 = gen1.generate_economia_pib()
        df2 = gen2.generate_economia_pib()

        # Estrutura deve ser idêntica (mesmo com seeds diferentes)
        assert list(df1.columns) == list(df2.columns)
        assert len(df1) == len(df2)
        assert df1['municipio_id'].nunique() == df2['municipio_id'].nunique()


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

    def test_no_negative_counts(self, datasets):
        """Verifica que não há valores negativos em colunas de contagem."""
        count_cols = [
            'total_alunos', 'total_docentes', 'total_funcionarios',
            'qtd_membros_familia', 'populacao_estimada', 'peso_nascer'
        ]

        for name, df in datasets.items():
            for col in count_cols:
                if col in df.columns:
                    assert (df[col] >= 0).all(), f"Valores negativos em '{name}.{col}'"

    def test_valid_years(self, datasets):
        """Verifica que os anos estão em faixas válidas."""
        for name, df in datasets.items():
            if 'ano' in df.columns:
                assert df['ano'].min() >= 2017, f"Anos muito antigos em '{name}'"
                assert df['ano'].max() <= 2024, f"Anos futuros em '{name}'"

    def test_valid_uf(self, datasets):
        """Verifica que todos os registros são do Piauí."""
        for name, df in datasets.items():
            if 'uf' in df.columns:
                assert all(df['uf'] == 'PI'), f"UF diferente de PI em '{name}'"

    def test_pib_composition(self, datasets):
        """Verifica que a composição do PIB é consistente."""
        df = datasets['economia_pib']

        # A soma dos componentes deve ser aproximadamente igual ao total
        componentes = (
            df['pib_agropecuaria_mil_reais'] +
            df['pib_industria_mil_reais'] +
            df['pib_servicos_mil_reais'] +
            df['pib_adm_publica_mil_reais']
        )

        # Tolerância de 1% para diferenças de arredondamento
        diferenca_percentual = abs(componentes - df['pib_total_mil_reais']) / df['pib_total_mil_reais']
        assert (diferenca_percentual < 0.01).all(), "Composição do PIB inconsistente"

    def test_ideb_range(self, datasets):
        """Verifica que o IDEB está no range válido."""
        df = datasets['educacao_ideb']
        assert df['ideb'].min() >= 0, "IDEB menor que 0"
        assert df['ideb'].max() <= 10, "IDEB maior que 10"

    def test_taxa_aprovacao_range(self, datasets):
        """Verifica que a taxa de aprovação está entre 0 e 1."""
        df = datasets['educacao_ideb']
        assert df['taxa_aprovacao'].min() >= 0, "Taxa de aprovação menor que 0"
        assert df['taxa_aprovacao'].max() <= 1, "Taxa de aprovação maior que 1"
