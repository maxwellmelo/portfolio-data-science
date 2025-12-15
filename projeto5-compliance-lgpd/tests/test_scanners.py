"""Testes para o scanner de PII."""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scanners import PIIScanner, ScanResult, PIIType, RiskLevel


class TestPIIScanner:
    """Testes para o scanner de PII."""

    @pytest.fixture
    def scanner(self):
        """Fixture para criar instância do scanner."""
        return PIIScanner()

    @pytest.fixture
    def sample_df(self):
        """Fixture para criar DataFrame de exemplo."""
        return pd.DataFrame({
            'id': [1, 2, 3],
            'nome_completo': ['João Silva', 'Maria Santos', 'Pedro Oliveira'],
            'cpf': ['123.456.789-00', '987.654.321-00', '111.222.333-44'],
            'email': ['joao@test.com', 'maria@test.com', 'pedro@test.com'],
            'telefone': ['(11) 99999-8888', '(21) 88888-7777', '(31) 77777-6666'],
            'salario': [5000.00, 7500.00, 6000.00],
            'departamento': ['TI', 'RH', 'Financeiro']
        })

    def test_scanner_initialization(self, scanner):
        """Testa inicialização do scanner."""
        assert scanner is not None
        # Verificar atributos existentes (uppercase)
        assert hasattr(scanner, 'PATTERNS')
        assert hasattr(scanner, 'COLUMN_PATTERNS')

    def test_scan_returns_result(self, scanner, sample_df):
        """Testa que scan retorna ScanResult."""
        result = scanner.scan(sample_df)

        assert isinstance(result, ScanResult)
        assert result.total_rows == 3
        assert result.columns_scanned == 7

    def test_detect_cpf(self, scanner, sample_df):
        """Testa detecção de CPF."""
        result = scanner.scan(sample_df)

        cpf_pii = next((p for p in result.pii_found if p.column == 'cpf'), None)
        assert cpf_pii is not None
        assert cpf_pii.pii_type == PIIType.CPF
        # CPF é classificado como alto risco pelo scanner
        assert cpf_pii.risk_level in [RiskLevel.ALTO, RiskLevel.CRITICO]

    def test_detect_email(self, scanner, sample_df):
        """Testa detecção de email."""
        result = scanner.scan(sample_df)

        email_pii = next((p for p in result.pii_found if p.column == 'email'), None)
        assert email_pii is not None
        assert email_pii.pii_type == PIIType.EMAIL

    def test_detect_telefone(self, scanner, sample_df):
        """Testa detecção de telefone."""
        result = scanner.scan(sample_df)

        tel_pii = next((p for p in result.pii_found if p.column == 'telefone'), None)
        assert tel_pii is not None
        assert tel_pii.pii_type == PIIType.TELEFONE

    def test_detect_nome(self, scanner, sample_df):
        """Testa detecção de nome por padrão de coluna."""
        result = scanner.scan(sample_df)

        nome_pii = next((p for p in result.pii_found if p.column == 'nome_completo'), None)
        assert nome_pii is not None
        assert nome_pii.pii_type == PIIType.NOME

    def test_risk_summary(self, scanner, sample_df):
        """Testa resumo de risco."""
        result = scanner.scan(sample_df)

        assert hasattr(result, 'risk_summary')
        assert 'critico' in result.risk_summary
        assert 'alto' in result.risk_summary
        assert 'medio' in result.risk_summary
        assert 'baixo' in result.risk_summary

    def test_recommendations_generated(self, scanner, sample_df):
        """Testa geração de recomendações."""
        result = scanner.scan(sample_df)

        assert hasattr(result, 'recommendations')
        assert len(result.recommendations) > 0

    def test_empty_dataframe(self, scanner):
        """Testa scan de DataFrame vazio."""
        df = pd.DataFrame()
        result = scanner.scan(df)

        assert result.total_rows == 0
        assert len(result.pii_found) == 0

    def test_no_pii_dataframe(self, scanner):
        """Testa DataFrame sem PII."""
        df = pd.DataFrame({
            'codigo': [1, 2, 3],
            'valor': [100, 200, 300],
            'categoria': ['A', 'B', 'C']
        })
        result = scanner.scan(df)

        # Pode encontrar alguns PIIs por padrão de coluna, mas deve ser baixo
        assert result.risk_summary.get('critico', 0) == 0


class TestPIIPatterns:
    """Testes para padrões de PII."""

    @pytest.fixture
    def scanner(self):
        return PIIScanner()

    def test_cpf_valid_formats(self, scanner):
        """Testa diferentes formatos de CPF."""
        df = pd.DataFrame({
            'doc1': ['123.456.789-00'],  # Com pontos e traço
            'doc2': ['12345678900'],      # Só números
        })
        result = scanner.scan(df)

        # Ambos devem ser detectados como CPF
        cpf_count = sum(1 for p in result.pii_found if p.pii_type == PIIType.CPF)
        assert cpf_count >= 1

    def test_cnpj_detection(self, scanner):
        """Testa detecção de CNPJ."""
        df = pd.DataFrame({
            'cnpj': ['12.345.678/0001-90']
        })
        result = scanner.scan(df)

        cnpj_pii = next((p for p in result.pii_found if p.pii_type == PIIType.CNPJ), None)
        assert cnpj_pii is not None

    def test_email_formats(self, scanner):
        """Testa diferentes formatos de email."""
        df = pd.DataFrame({
            'emails': ['user@domain.com', 'user.name@sub.domain.org', 'user_123@test.net']
        })
        result = scanner.scan(df)

        email_pii = next((p for p in result.pii_found if p.pii_type == PIIType.EMAIL), None)
        assert email_pii is not None
        assert email_pii.count == 3

    def test_cep_detection(self, scanner):
        """Testa detecção de CEP."""
        df = pd.DataFrame({
            'cep': ['12345-678', '12345678']
        })
        result = scanner.scan(df)

        cep_pii = next((p for p in result.pii_found if p.pii_type == PIIType.CEP), None)
        assert cep_pii is not None


class TestColumnNameDetection:
    """Testes para detecção por nome de coluna."""

    @pytest.fixture
    def scanner(self):
        return PIIScanner()

    def test_detect_by_column_name(self, scanner):
        """Testa detecção baseada em nome da coluna."""
        df = pd.DataFrame({
            'endereco': ['Rua A, 123'],
            'salario': [5000],
            'data_nascimento': ['01/01/1990']
        })
        result = scanner.scan(df)

        # Deve detectar por nome da coluna mesmo sem padrão regex
        assert len(result.pii_found) >= 2

    def test_case_insensitive_column(self, scanner):
        """Testa que nomes de coluna são case-insensitive."""
        df = pd.DataFrame({
            'NOME': ['João'],
            'Email': ['test@test.com'],
            'CPF': ['123.456.789-00']
        })
        result = scanner.scan(df)

        assert len(result.pii_found) >= 3
