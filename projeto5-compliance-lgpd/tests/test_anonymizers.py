"""Testes para o anonimizador de dados."""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.anonymizers import DataAnonymizer, AnonymizationMethod


class TestDataAnonymizer:
    """Testes para o anonimizador."""

    @pytest.fixture
    def anonymizer(self):
        """Fixture para criar instância do anonimizador."""
        # Usar salt customizado para testes (evitar warnings)
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

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
        assert anonymizer.salt is not None

    def test_anonymizer_with_custom_salt(self):
        """Testa inicialização com salt customizado."""
        custom_salt = "my_secure_salt_12345"
        anonymizer = DataAnonymizer(salt=custom_salt)
        assert anonymizer.salt == custom_salt

    def test_anonymizer_strict_mode_with_insecure_salt(self):
        """Testa modo strict com salt inseguro."""
        with pytest.raises(ValueError):
            DataAnonymizer(salt="short", strict_mode=True)


class TestMaskMethod:
    """Testes para método de mascaramento."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

    def test_mask_column_basic(self, anonymizer):
        """Testa mascaramento básico de coluna."""
        df = pd.DataFrame({'col': ['12345', 'abcde']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.MASK
        )

        assert df_anon['col'].iloc[0] == '*****'
        assert df_anon['col'].iloc[1] == '*****'

    def test_mask_with_visible_start(self, anonymizer):
        """Testa mascaramento com caracteres visíveis no início."""
        df = pd.DataFrame({'col': ['123456789']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.MASK,
            visible_start=3
        )

        assert df_anon['col'].iloc[0].startswith('123')
        assert '***' in df_anon['col'].iloc[0]

    def test_mask_with_visible_end(self, anonymizer):
        """Testa mascaramento com caracteres visíveis no final."""
        df = pd.DataFrame({'col': ['123456789']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.MASK,
            visible_end=2
        )

        assert df_anon['col'].iloc[0].endswith('89')

    def test_mask_with_pattern(self, anonymizer):
        """Testa mascaramento com padrão específico."""
        df = pd.DataFrame({'cpf': ['123.456.789-00']})

        df_anon = anonymizer.anonymize_column(
            df, 'cpf',
            AnonymizationMethod.MASK,
            pattern='***.***.***-**'
        )

        assert df_anon['cpf'].iloc[0] == '***.***.***-**'

    def test_mask_null_values(self, anonymizer):
        """Testa que valores nulos são preservados."""
        df = pd.DataFrame({'col': ['valor', None, 'outro']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.MASK
        )

        assert pd.isna(df_anon['col'].iloc[1])


class TestHashMethod:
    """Testes para método de hash."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

    def test_hash_column(self, anonymizer):
        """Testa hash de coluna."""
        df = pd.DataFrame({'col': ['valor']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.HASH
        )

        assert df_anon['col'].iloc[0] != 'valor'
        assert len(df_anon['col'].iloc[0]) == 64  # SHA-256

    def test_hash_consistency(self, anonymizer):
        """Testa que hash é consistente para mesmo valor."""
        df = pd.DataFrame({'col': ['teste', 'teste', 'outro']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.HASH
        )

        assert df_anon['col'].iloc[0] == df_anon['col'].iloc[1]
        assert df_anon['col'].iloc[0] != df_anon['col'].iloc[2]

    def test_hash_truncate(self, anonymizer):
        """Testa truncamento do hash."""
        df = pd.DataFrame({'col': ['valor']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.HASH,
            truncate=12
        )

        assert len(df_anon['col'].iloc[0]) == 12

    def test_hash_different_salts(self):
        """Testa que salts diferentes produzem hashes diferentes."""
        df = pd.DataFrame({'col': ['valor']})

        anon1 = DataAnonymizer(salt="salt_one_1234567890")
        anon2 = DataAnonymizer(salt="salt_two_1234567890")

        df1 = anon1.anonymize_column(df.copy(), 'col', AnonymizationMethod.HASH)
        df2 = anon2.anonymize_column(df.copy(), 'col', AnonymizationMethod.HASH)

        assert df1['col'].iloc[0] != df2['col'].iloc[0]

    def test_hash_null_values(self, anonymizer):
        """Testa que valores nulos são preservados."""
        df = pd.DataFrame({'col': ['valor', None]})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.HASH
        )

        assert pd.isna(df_anon['col'].iloc[1])


class TestPseudonymizeMethod:
    """Testes para método de pseudonimização."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

    def test_pseudonymize_column(self, anonymizer):
        """Testa pseudonimização de coluna."""
        df = pd.DataFrame({'nome': ['João Silva', 'Maria Santos']})

        df_anon = anonymizer.anonymize_column(
            df, 'nome',
            AnonymizationMethod.PSEUDONYMIZE,
            pii_type='name'
        )

        assert df_anon['nome'].iloc[0] != 'João Silva'
        assert df_anon['nome'].iloc[1] != 'Maria Santos'

    def test_pseudonymize_consistency(self, anonymizer):
        """Testa que valores iguais recebem mesmo pseudônimo."""
        df = pd.DataFrame({'nome': ['João', 'João', 'Maria']})

        df_anon = anonymizer.anonymize_column(
            df, 'nome',
            AnonymizationMethod.PSEUDONYMIZE
        )

        assert df_anon['nome'].iloc[0] == df_anon['nome'].iloc[1]
        assert df_anon['nome'].iloc[0] != df_anon['nome'].iloc[2]


class TestGeneralizeMethod:
    """Testes para método de generalização."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

    def test_generalize_numeric(self, anonymizer):
        """Testa generalização de valores numéricos."""
        df = pd.DataFrame({'idade': [25, 35, 45, 55, 65]})

        df_anon = anonymizer.anonymize_column(
            df, 'idade',
            AnonymizationMethod.GENERALIZE,
            generalization_type='range',
            bins=3
        )

        # Valores devem estar categorizados
        assert df_anon['idade'].dtype.name == 'category'


class TestSuppressMethod:
    """Testes para método de supressão."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

    def test_suppress_column(self, anonymizer):
        """Testa supressão de coluna."""
        df = pd.DataFrame({'col': ['valor1', 'valor2', 'valor3']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.SUPPRESS
        )

        # Todos os valores devem ser None
        assert all(pd.isna(df_anon['col']))

    def test_suppress_with_replacement(self, anonymizer):
        """Testa supressão com valor de substituição."""
        df = pd.DataFrame({'col': ['valor1', 'valor2']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.SUPPRESS,
            replacement='[REMOVIDO]'
        )

        assert all(df_anon['col'] == '[REMOVIDO]')


class TestTokenizeMethod:
    """Testes para método de tokenização."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

    def test_tokenize_column(self, anonymizer):
        """Testa tokenização de coluna."""
        df = pd.DataFrame({'col': ['valor1', 'valor2']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.TOKENIZE
        )

        assert all(str(v).startswith('TOK_') for v in df_anon['col'])

    def test_tokenize_with_prefix(self, anonymizer):
        """Testa tokenização com prefixo customizado."""
        df = pd.DataFrame({'col': ['valor']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.TOKENIZE,
            prefix='ID_'
        )

        assert df_anon['col'].iloc[0].startswith('ID_')

    def test_token_mapping(self, anonymizer):
        """Testa que mapeamento de tokens é mantido."""
        df = pd.DataFrame({'col': ['valor']})

        anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.TOKENIZE
        )

        mapping = anonymizer.get_token_mapping()
        assert 'valor' in mapping


class TestNoiseMethod:
    """Testes para método de adição de ruído."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

    def test_noise_column(self, anonymizer):
        """Testa adição de ruído em coluna numérica."""
        df = pd.DataFrame({'valor': [1000.0, 2000.0, 3000.0]})

        df_anon = anonymizer.anonymize_column(
            df, 'valor',
            AnonymizationMethod.NOISE,
            noise_level=0.1
        )

        # Valores devem ser diferentes (com alta probabilidade)
        assert not all(df_anon['valor'] == df['valor'])

    def test_noise_preserves_approximate_value(self, anonymizer):
        """Testa que ruído não altera drasticamente os valores."""
        original_value = 1000.0
        df = pd.DataFrame({'valor': [original_value] * 100})

        df_anon = anonymizer.anonymize_column(
            df, 'valor',
            AnonymizationMethod.NOISE,
            noise_level=0.1
        )

        # Média deve estar próxima do valor original
        mean_value = df_anon['valor'].mean()
        assert abs(mean_value - original_value) < original_value * 0.2


class TestDataFrameAnonymization:
    """Testes de anonimização de DataFrame completo."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

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
        assert df_anon['nome'].iloc[0] == sample_df['nome'].iloc[0]

    def test_anonymize_multiple_columns(self, anonymizer, sample_df):
        """Testa anonimização de múltiplas colunas."""
        config = {
            'nome': {'method': 'pseudonymize', 'pii_type': 'name'},
            'cpf': {'method': 'hash', 'truncate': 12},
            'salario': {'method': 'noise', 'noise_level': 0.1}
        }

        df_anon = anonymizer.anonymize_dataframe(sample_df, config)

        assert df_anon['nome'].iloc[0] != sample_df['nome'].iloc[0]
        assert df_anon['cpf'].iloc[0] != sample_df['cpf'].iloc[0]
        assert len(df_anon['cpf'].iloc[0]) == 12

    def test_original_unchanged(self, anonymizer, sample_df):
        """Testa que DataFrame original não é modificado."""
        original_cpf = sample_df['cpf'].iloc[0]

        config = {'cpf': {'method': 'hash'}}
        anonymizer.anonymize_dataframe(sample_df, config)

        assert sample_df['cpf'].iloc[0] == original_cpf

    def test_missing_column_warning(self, anonymizer, sample_df):
        """Testa aviso para coluna inexistente."""
        config = {
            'coluna_inexistente': {'method': 'hash'}
        }

        # Não deve lançar exceção, apenas log warning
        df_anon = anonymizer.anonymize_dataframe(sample_df, config)
        assert 'coluna_inexistente' not in df_anon.columns

    def test_all_methods(self, anonymizer):
        """Testa todos os métodos de anonimização."""
        df = pd.DataFrame({
            'col1': ['valor1'],
            'col2': ['valor2'],
            'col3': ['valor3'],
            'col4': [1000.0],
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

        assert df_anon['col1'].iloc[0] != df['col1'].iloc[0]
        assert df_anon['col2'].iloc[0] != df['col2'].iloc[0]
        assert df_anon['col3'].iloc[0] != df['col3'].iloc[0]
        assert pd.isna(df_anon['col5'].iloc[0])
        assert df_anon['col6'].iloc[0].startswith('TOK_')


class TestSpecificMethods:
    """Testes para métodos específicos de mascaramento."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

    def test_mask_cpf(self, anonymizer):
        """Testa mascaramento específico de CPF."""
        result = anonymizer.mask_cpf("123.456.789-00")
        assert result == "123.***.***-00"

    def test_mask_cpf_invalid(self, anonymizer):
        """Testa mascaramento de CPF inválido."""
        result = anonymizer.mask_cpf("invalid")
        assert result == "***.***.***-**"

    def test_mask_email(self, anonymizer):
        """Testa mascaramento de email."""
        result = anonymizer.mask_email("joao@example.com")
        assert '@example.com' in result
        assert result.startswith('j')
        assert '*' in result

    def test_mask_email_invalid(self, anonymizer):
        """Testa mascaramento de email inválido."""
        result = anonymizer.mask_email("invalid")
        assert result == "***@***.***"

    def test_mask_telefone(self, anonymizer):
        """Testa mascaramento de telefone."""
        result = anonymizer.mask_telefone("(11) 99999-8888")
        assert "(11)" in result
        assert "*****" in result

    def test_mask_telefone_invalid(self, anonymizer):
        """Testa mascaramento de telefone inválido."""
        result = anonymizer.mask_telefone("123")
        assert result == "(**) *****-****"


class TestEdgeCases:
    """Testes de casos extremos."""

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer(salt="test_salt_for_unit_tests_12345")

    def test_empty_dataframe(self, anonymizer):
        """Testa anonimização de DataFrame vazio."""
        df = pd.DataFrame({'col': []})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.HASH
        )

        assert len(df_anon) == 0

    def test_special_characters(self, anonymizer):
        """Testa tratamento de caracteres especiais."""
        df = pd.DataFrame({'col': ['João@#$%ção']})

        df_anon = anonymizer.anonymize_column(
            df, 'col',
            AnonymizationMethod.HASH
        )

        assert df_anon['col'].iloc[0] is not None
        assert len(df_anon['col'].iloc[0]) > 0

    def test_column_not_found(self, anonymizer):
        """Testa erro quando coluna não existe."""
        df = pd.DataFrame({'col': ['valor']})

        with pytest.raises(ValueError):
            anonymizer.anonymize_column(
                df, 'coluna_inexistente',
                AnonymizationMethod.HASH
            )

    def test_invalid_method(self, anonymizer):
        """Testa erro para método inválido."""
        df = pd.DataFrame({'col': ['valor']})

        with pytest.raises(ValueError):
            anonymizer.anonymize_column(df, 'col', 'invalid_method')


class TestSaltSecurity:
    """Testes de segurança do salt."""

    def test_default_salt_is_insecure(self):
        """Testa que salt padrão é detectado como inseguro."""
        from config.settings import settings

        # Salt padrão deve ser inseguro
        assert not settings.anonymization.is_salt_secure()
        assert settings.anonymization.get_salt_warning() != ""

    def test_anonymizer_with_default_salt(self):
        """Testa que anonimizador funciona mesmo com salt padrão (apenas warning)."""
        # Deve funcionar sem erro, apenas gerar warning
        anonymizer = DataAnonymizer()
        assert anonymizer is not None
        assert anonymizer.salt is not None

    def test_secure_salt_no_warning(self, caplog):
        """Testa que salt seguro não gera warning."""
        import logging
        caplog.set_level(logging.WARNING)
        caplog.clear()

        # Usar salt seguro (>=16 chars)
        anonymizer = DataAnonymizer(salt="this_is_a_very_secure_salt_12345")

        # Não deve ter warnings sobre salt inseguro
        salt_warnings = [r for r in caplog.records
                        if "inseguro" in r.message.lower() or "critico" in r.message.lower()]
        assert len(salt_warnings) == 0

    def test_strict_mode_blocks_insecure_salt(self):
        """Testa que strict_mode bloqueia salt inseguro."""
        with pytest.raises(ValueError) as exc_info:
            DataAnonymizer(strict_mode=True)

        assert "insegura" in str(exc_info.value).lower() or "salt" in str(exc_info.value).lower()
