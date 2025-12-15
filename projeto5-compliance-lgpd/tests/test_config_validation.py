"""Testes para validação de configuração JSON."""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import validate_config, load_config_file, ColumnConfig


class TestColumnConfigValidation:
    """Testes para validação de ColumnConfig."""

    def test_valid_config(self):
        """Testa configuração válida."""
        config = ColumnConfig(method="hash")
        assert config.method == "hash"

    def test_valid_config_with_options(self):
        """Testa configuração válida com opções."""
        config = ColumnConfig(
            method="hash",
            truncate=12,
            algorithm="sha256"
        )
        assert config.method == "hash"
        assert config.truncate == 12

    def test_invalid_method(self):
        """Testa método inválido."""
        with pytest.raises(ValueError) as exc_info:
            ColumnConfig(method="invalid_method")

        assert "nao suportado" in str(exc_info.value).lower()

    def test_all_valid_methods(self):
        """Testa todos os métodos válidos."""
        valid_methods = ["mask", "hash", "pseudonymize", "generalize", "suppress", "tokenize", "noise"]

        for method in valid_methods:
            config = ColumnConfig(method=method)
            assert config.method == method

    def test_invalid_truncate(self):
        """Testa valor de truncate inválido."""
        with pytest.raises(ValueError):
            ColumnConfig(method="hash", truncate=0)

        with pytest.raises(ValueError):
            ColumnConfig(method="hash", truncate=-1)

    def test_valid_truncate(self):
        """Testa valores válidos de truncate."""
        config = ColumnConfig(method="hash", truncate=1)
        assert config.truncate == 1

        config = ColumnConfig(method="hash", truncate=64)
        assert config.truncate == 64

    def test_invalid_noise_level(self):
        """Testa noise_level inválido."""
        with pytest.raises(ValueError):
            ColumnConfig(method="noise", noise_level=-0.1)

        with pytest.raises(ValueError):
            ColumnConfig(method="noise", noise_level=1.5)

    def test_valid_noise_level(self):
        """Testa valores válidos de noise_level."""
        config = ColumnConfig(method="noise", noise_level=0.0)
        assert config.noise_level == 0.0

        config = ColumnConfig(method="noise", noise_level=1.0)
        assert config.noise_level == 1.0

        config = ColumnConfig(method="noise", noise_level=0.5)
        assert config.noise_level == 0.5


class TestValidateConfig:
    """Testes para função validate_config."""

    def test_valid_config(self):
        """Testa configuração válida."""
        config = {
            "cpf": {"method": "hash", "truncate": 12},
            "nome": {"method": "pseudonymize"}
        }

        validated = validate_config(config)
        assert "cpf" in validated
        assert "nome" in validated

    def test_invalid_method_in_config(self):
        """Testa método inválido na configuração."""
        config = {
            "col1": {"method": "invalid"}
        }

        with pytest.raises(ValueError) as exc_info:
            validate_config(config)

        assert "col1" in str(exc_info.value)

    def test_multiple_errors(self):
        """Testa múltiplos erros na configuração."""
        config = {
            "col1": {"method": "invalid1"},
            "col2": {"method": "invalid2"}
        }

        with pytest.raises(ValueError) as exc_info:
            validate_config(config)

        error_msg = str(exc_info.value)
        assert "col1" in error_msg
        assert "col2" in error_msg

    def test_partial_valid_config(self):
        """Testa configuração parcialmente válida."""
        config = {
            "col1": {"method": "hash"},  # válido
            "col2": {"method": "invalid"}  # inválido
        }

        with pytest.raises(ValueError) as exc_info:
            validate_config(config)

        assert "col2" in str(exc_info.value)


class TestLoadConfigFile:
    """Testes para função load_config_file."""

    def test_load_valid_json(self):
        """Testa carregamento de JSON válido."""
        config = {
            "cpf": {"method": "hash"},
            "nome": {"method": "mask"}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            loaded = load_config_file(temp_path)
            assert "cpf" in loaded
            assert "nome" in loaded
        finally:
            Path(temp_path).unlink()

    def test_file_not_found(self):
        """Testa arquivo não encontrado."""
        with pytest.raises(FileNotFoundError):
            load_config_file("arquivo_inexistente.json")

    def test_invalid_json(self):
        """Testa JSON inválido."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                load_config_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_empty_config(self):
        """Testa configuração vazia."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                load_config_file(temp_path)

            assert "vazia" in str(exc_info.value).lower()
        finally:
            Path(temp_path).unlink()

    def test_config_not_dict(self):
        """Testa configuração que não é dicionário."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(["lista", "invalida"], f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                load_config_file(temp_path)

            assert "dicionario" in str(exc_info.value).lower()
        finally:
            Path(temp_path).unlink()

    def test_config_with_invalid_method(self):
        """Testa configuração com método inválido."""
        config = {
            "col": {"method": "metodo_invalido"}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError):
                load_config_file(temp_path)
        finally:
            Path(temp_path).unlink()


class TestConfigExamples:
    """Testes com exemplos de configuração do README."""

    def test_readme_example_config(self):
        """Testa exemplo de configuração do README."""
        config = {
            "cpf": {"method": "hash", "truncate": 12},
            "nome_completo": {"method": "pseudonymize"},
            "email": {"method": "mask", "visible_start": 3},
            "telefone": {"method": "suppress"},
            "salario": {"method": "noise", "noise_level": 0.1}
        }

        validated = validate_config(config)
        assert len(validated) == 5

    def test_all_methods_config(self):
        """Testa configuração com todos os métodos."""
        config = {
            "col1": {"method": "mask", "pattern": "***-***"},
            "col2": {"method": "hash", "algorithm": "sha512"},
            "col3": {"method": "pseudonymize", "pii_type": "email"},
            "col4": {"method": "generalize", "bins": 5},
            "col5": {"method": "suppress", "replacement": "[REMOVED]"},
            "col6": {"method": "tokenize", "prefix": "USER_"},
            "col7": {"method": "noise", "noise_level": 0.05}
        }

        validated = validate_config(config)
        assert len(validated) == 7
