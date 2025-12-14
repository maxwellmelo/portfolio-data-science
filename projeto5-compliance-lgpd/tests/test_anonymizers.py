"""Testes para o anonimizador de dados."""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.anonymizers import DataAnonymizer


class TestDataAnonymizer:
    """Testes para o anonimizador."""

    @pytest.fixture
    def anonymizer(self):
        """Fixture para criar instância do anonimizador."""
        return DataAnonymizer()

    @pytest.fixture
    def sample_df(self):
        """Fixture para criar DataFrame de exemplo."""
        return pd.DataFrame({
            'id': [1, 2, 3],
            'nome': ['João Silva', 'Maria Santos', 'Pedro Oliveira'],
            'cpf': ['123.456.789-00', '987.654.321-00', '111.222.333-44'],
            'email': ['joao@test.com', 'maria@test.com', 'pedro@test.com'],
            'salario': [5000.00, 7500.00, 6000.00]
        })

    def test_anonymizer_initialization(self, anonymizer):
        """Testa inicialização do anonimizador."""
        assert anonymizer is not None

    def test_mask_value(self, anonymizer):
        """Testa mascaramento de valor."""
        original = "123.456.789-00"
        masked = anonymizer.mask_value(original, visible_chars=3)

        assert masked != original
        assert len(masked) == len(original)
        assert '*' in masked

    def test_mask_preserves_format(self, anonymizer):
        """Testa que mascaramento preserva formato."""
        cpf = "123.456.789-00"
        masked = anonymizer.mask_value(cpf, visible_chars=3)

        # Pontos e traços devem ser preservados
        assert '.' in masked
        assert '-' in masked

    def test_hash_value(self, anonymizer):
        """Testa hash de valor."""
        original = "João Silva"
        hashed = anonymizer.hash_value(original)

        assert hashed != original
        assert len(hashed) > 0

    def test_hash_consistency(self, anonymizer):
        """Testa que hash é consistente."""
        original = "teste123"
        hash1 = anonymizer.hash_value(original)
        hash2 = anonymizer.hash_value(original)

        assert hash1 == hash2

    def test_hash_truncate(self, anonymizer):
        """Testa truncamento do hash."""
        original = "valor"
        hashed = anonymizer.hash_value(original, truncate=12)

        assert len(hashed) == 12

    def test_pseudonymize(self, anonymizer):
        """Testa pseudonimização."""
        original = "João Silva"
        pseudo = anonymizer.pseudonymize(original, prefix="Pessoa")

        assert pseudo.startswith("Pessoa_")
        assert original not in pseudo

    def test_pseudonymize_consistency(self, anonymizer):
        """Testa que pseudônimos são consistentes."""
        original = "João Silva"
        pseudo1 = anonymizer.pseudonymize(original)
        pseudo2 = anonymizer.pseudonymize(original)

        assert pseudo1 == pseudo2

    def test_generalize_numeric(self, anonymizer):
        """Testa generalização de valor numérico."""
        value = 5250
        generalized = anonymizer.generalize_numeric(value, bin_size=1000)

        assert generalized == "5000-6000"

    def test_suppress_value(self, anonymizer):
        """Testa supressão de valor."""
        original = "dado sensível"
        suppressed = anonymizer.suppress_value(original)

        assert suppressed == "[SUPRIMIDO]"
        assert original not in suppressed

    def test_add_noise(self, anonymizer):
        """Testa adição de ruído."""
        original = 1000.0
        noisy = anonymizer.add_noise(original, percentage=10)

        # Valor deve estar dentro de ±10%
        assert 900 <= noisy <= 1100
        assert noisy != original  # Muito improvável ser igual

    def test_tokenize(self, anonymizer):
        """Testa tokenização."""
        original = "dado para tokenizar"
        token = anonymizer.tokenize(original)

        assert token.startswith("TKN_")
        assert original not in token


class TestDataFrameAnonymization:
    """Testes de anonimização de DataFrame."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer()

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame({
            'nome': ['João', 'Maria'],
            'cpf': ['123.456.789-00', '987.654.321-00'],
            'salario': [5000.0, 7000.0]
        })

    def test_anonymize_single_column(self, anonymizer, sample_df):
        """Testa anonimização de coluna única."""
        config = {
            'cpf': {'method': 'hash'}
        }

        df_anon = anonymizer.anonymize_dataframe(sample_df, config)

        assert df_anon['cpf'].iloc[0] != sample_df['cpf'].iloc[0]
        assert df_anon['nome'].iloc[0] == sample_df['nome'].iloc[0]  # Não modificado

    def test_anonymize_multiple_columns(self, anonymizer, sample_df):
        """Testa anonimização de múltiplas colunas."""
        config = {
            'nome': {'method': 'pseudonymize'},
            'cpf': {'method': 'hash'},
            'salario': {'method': 'noise', 'percentage': 10}
        }

        df_anon = anonymizer.anonymize_dataframe(sample_df, config)

        assert df_anon['nome'].iloc[0] != sample_df['nome'].iloc[0]
        assert df_anon['cpf'].iloc[0] != sample_df['cpf'].iloc[0]
        # Salário pode ser igual por acaso, mas muito improvável

    def test_original_unchanged(self, anonymizer, sample_df):
        """Testa que DataFrame original não é modificado."""
        original_cpf = sample_df['cpf'].iloc[0]

        config = {'cpf': {'method': 'hash'}}
        anonymizer.anonymize_dataframe(sample_df.copy(), config)

        assert sample_df['cpf'].iloc[0] == original_cpf

    def test_all_methods(self, anonymizer):
        """Testa todos os métodos de anonimização."""
        df = pd.DataFrame({
            'col1': ['valor1'],
            'col2': ['valor2'],
            'col3': ['valor3'],
            'col4': [1000],
            'col5': ['valor5'],
            'col6': ['valor6']
        })

        config = {
            'col1': {'method': 'mask'},
            'col2': {'method': 'hash'},
            'col3': {'method': 'pseudonymize'},
            'col4': {'method': 'noise'},
            'col5': {'method': 'suppress'},
            'col6': {'method': 'tokenize'}
        }

        df_anon = anonymizer.anonymize_dataframe(df, config)

        # Verificar que todas as colunas foram anonimizadas
        assert df_anon['col1'].iloc[0] != df['col1'].iloc[0]
        assert df_anon['col2'].iloc[0] != df['col2'].iloc[0]
        assert df_anon['col3'].iloc[0] != df['col3'].iloc[0]
        assert df_anon['col5'].iloc[0] == '[SUPRIMIDO]'
        assert df_anon['col6'].iloc[0].startswith('TKN_')


class TestEdgeCases:
    """Testes de casos extremos."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer()

    def test_null_values(self, anonymizer):
        """Testa tratamento de valores nulos."""
        df = pd.DataFrame({
            'col': ['valor', None, 'outro']
        })

        config = {'col': {'method': 'hash'}}
        df_anon = anonymizer.anonymize_dataframe(df, config)

        assert pd.isna(df_anon['col'].iloc[1]) or df_anon['col'].iloc[1] in ['', None, 'None']

    def test_empty_string(self, anonymizer):
        """Testa tratamento de strings vazias."""
        masked = anonymizer.mask_value('')
        assert masked == '' or masked == '*' * 0

    def test_special_characters(self, anonymizer):
        """Testa tratamento de caracteres especiais."""
        original = "João@#$%ção"
        hashed = anonymizer.hash_value(original)

        assert hashed is not None
        assert len(hashed) > 0

    def test_numeric_as_string(self, anonymizer):
        """Testa mascaramento de número como string."""
        masked = anonymizer.mask_value("12345", visible_chars=2)
        assert masked[-2:] == "45" or '*' in masked
