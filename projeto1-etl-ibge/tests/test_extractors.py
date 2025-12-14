"""
Testes para os módulos de extração de dados.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors.ibge_client import IBGEClient, IBGEApiError, RateLimiter
from src.extractors.localidades import LocalidadesExtractor


class TestRateLimiter:
    """Testes para o RateLimiter."""

    def test_rate_limiter_initialization(self):
        """Testa inicialização do rate limiter."""
        limiter = RateLimiter(min_interval=0.5)
        assert limiter.min_interval == 0.5
        assert limiter.last_request_time == 0.0

    def test_rate_limiter_wait(self):
        """Testa que o rate limiter respeita o intervalo."""
        limiter = RateLimiter(min_interval=0.1)

        # Primeira chamada não deve esperar
        import time
        start = time.time()
        limiter.wait()
        elapsed = time.time() - start
        assert elapsed < 0.1  # Não deve esperar na primeira chamada

        # Segunda chamada deve esperar
        start = time.time()
        limiter.wait()
        elapsed = time.time() - start
        assert elapsed >= 0.09  # Deve esperar aproximadamente 0.1s


class TestIBGEClient:
    """Testes para o cliente IBGE."""

    def test_client_initialization(self):
        """Testa inicialização do cliente."""
        client = IBGEClient(timeout=30, retry_attempts=3)
        assert client.timeout == 30
        assert client.retry_attempts == 3
        client.close()

    def test_client_context_manager(self):
        """Testa uso como context manager."""
        with IBGEClient() as client:
            assert client is not None

    @patch("httpx.Client.get")
    def test_get_regioes_success(self, mock_get):
        """Testa extração de regiões com sucesso."""
        # Mock da resposta
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "sigla": "N", "nome": "Norte"},
            {"id": 2, "sigla": "NE", "nome": "Nordeste"}
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with IBGEClient() as client:
            regioes = client.get_regioes()

        assert len(regioes) == 2
        assert regioes[0]["sigla"] == "N"

    @patch("httpx.Client.get")
    def test_get_estados_success(self, mock_get):
        """Testa extração de estados com sucesso."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": 22,
                "sigla": "PI",
                "nome": "Piauí",
                "regiao": {"id": 2, "sigla": "NE", "nome": "Nordeste"}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with IBGEClient() as client:
            estados = client.get_estados()

        assert len(estados) == 1
        assert estados[0]["sigla"] == "PI"


class TestLocalidadesExtractor:
    """Testes para o extrator de localidades."""

    @patch.object(IBGEClient, "get_regioes")
    def test_extract_regioes_returns_dataframe(self, mock_get_regioes):
        """Testa que extract_regioes retorna DataFrame."""
        mock_get_regioes.return_value = [
            {"id": 1, "sigla": "N", "nome": "Norte"},
            {"id": 2, "sigla": "NE", "nome": "Nordeste"},
            {"id": 3, "sigla": "SE", "nome": "Sudeste"},
            {"id": 4, "sigla": "S", "nome": "Sul"},
            {"id": 5, "sigla": "CO", "nome": "Centro-Oeste"}
        ]

        with LocalidadesExtractor() as extractor:
            df = extractor.extract_regioes()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert "id" in df.columns
        assert "sigla" in df.columns
        assert "nome" in df.columns

    @patch.object(IBGEClient, "get_estados")
    def test_extract_estados_returns_dataframe(self, mock_get_estados):
        """Testa que extract_estados retorna DataFrame."""
        mock_get_estados.return_value = [
            {
                "id": 22,
                "sigla": "PI",
                "nome": "Piauí",
                "regiao": {"id": 2, "sigla": "NE", "nome": "Nordeste"}
            },
            {
                "id": 35,
                "sigla": "SP",
                "nome": "São Paulo",
                "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"}
            }
        ]

        with LocalidadesExtractor() as extractor:
            df = extractor.extract_estados()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "regiao_id" in df.columns

    @patch.object(IBGEClient, "get_municipios")
    def test_extract_municipios_by_uf(self, mock_get_municipios):
        """Testa extração de municípios por UF."""
        mock_get_municipios.return_value = [
            {
                "id": 2211001,
                "nome": "Teresina",
                "microrregiao": {
                    "id": 22015,
                    "nome": "Teresina",
                    "mesorregiao": {
                        "id": 2204,
                        "nome": "Centro-Norte Piauiense",
                        "UF": {
                            "id": 22,
                            "sigla": "PI",
                            "nome": "Piauí",
                            "regiao": {"id": 2, "sigla": "NE", "nome": "Nordeste"}
                        }
                    }
                }
            }
        ]

        with LocalidadesExtractor() as extractor:
            df = extractor.extract_municipios(uf="PI")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]["nome"] == "Teresina"
        assert df.iloc[0]["uf_sigla"] == "PI"


class TestDataQuality:
    """Testes de qualidade dos dados."""

    def test_regiao_ids_are_valid(self):
        """Testa que IDs de regiões são válidos (1-5)."""
        valid_ids = {1, 2, 3, 4, 5}

        # Simular dados
        data = [
            {"id": 1, "sigla": "N", "nome": "Norte"},
            {"id": 2, "sigla": "NE", "nome": "Nordeste"},
            {"id": 3, "sigla": "SE", "nome": "Sudeste"},
            {"id": 4, "sigla": "S", "nome": "Sul"},
            {"id": 5, "sigla": "CO", "nome": "Centro-Oeste"}
        ]

        for item in data:
            assert item["id"] in valid_ids

    def test_estado_sigla_format(self):
        """Testa formato das siglas de estado."""
        siglas = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
                  "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
                  "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

        for sigla in siglas:
            assert len(sigla) == 2
            assert sigla.isupper()

    def test_municipio_id_format(self):
        """Testa formato do código IBGE de municípios (7 dígitos)."""
        municipio_ids = [2211001, 3550308, 1100205]

        for mid in municipio_ids:
            assert 1000000 <= mid <= 9999999


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
