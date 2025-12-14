"""Testes para a API REST."""

import pytest
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from src.api import app


@pytest.fixture
def client():
    """Fixture para criar cliente de teste."""
    return TestClient(app)


class TestAPIEndpoints:
    """Testes dos endpoints da API."""

    def test_root(self, client):
        """Testa endpoint raiz."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "nome" in data
        assert "versao" in data

    def test_health(self, client):
        """Testa endpoint de saúde."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"

    def test_fontes(self, client):
        """Testa endpoint de fontes de dados."""
        response = client.get("/fontes")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_municipios(self, client):
        """Testa endpoint de municípios."""
        response = client.get("/municipios")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verificar estrutura
        municipio = data[0]
        assert "codigo" in municipio
        assert "nome" in municipio

    def test_saude_mortalidade(self, client):
        """Testa endpoint de mortalidade."""
        response = client.get("/saude/mortalidade")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_saude_mortalidade_filtro_ano(self, client):
        """Testa filtro por ano em mortalidade."""
        response = client.get("/saude/mortalidade?ano=2023")
        assert response.status_code == 200

        data = response.json()
        for item in data:
            assert item.get("ano") == 2023

    def test_saude_nascimentos(self, client):
        """Testa endpoint de nascimentos."""
        response = client.get("/saude/nascimentos")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_educacao_escolas(self, client):
        """Testa endpoint de escolas."""
        response = client.get("/educacao/escolas")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_educacao_ideb(self, client):
        """Testa endpoint do IDEB."""
        response = client.get("/educacao/ideb")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_economia_pib(self, client):
        """Testa endpoint de PIB."""
        response = client.get("/economia/pib")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_assistencia_cadunico(self, client):
        """Testa endpoint do CadÚnico."""
        response = client.get("/assistencia/cadunico")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_indicadores_municipio(self, client):
        """Testa endpoint de indicadores consolidados."""
        response = client.get("/indicadores/2211001?ano=2023")
        assert response.status_code == 200

        data = response.json()
        assert "municipio" in data
        assert "ano" in data
        assert "saude" in data or "economia" in data or "educacao" in data

    def test_indicadores_municipio_invalido(self, client):
        """Testa indicadores para município inválido."""
        response = client.get("/indicadores/9999999?ano=2023")
        # Pode retornar 200 com dados vazios ou 404
        assert response.status_code in [200, 404]


class TestAPIFilters:
    """Testes dos filtros da API."""

    def test_pib_filtro_municipio(self, client):
        """Testa filtro por município no PIB."""
        response = client.get("/economia/pib?municipio_id=2211001")
        assert response.status_code == 200

        data = response.json()
        for item in data:
            assert item.get("municipio_id") == 2211001

    def test_escolas_filtro_rede(self, client):
        """Testa filtro por rede nas escolas."""
        response = client.get("/educacao/escolas?rede=Municipal")
        assert response.status_code == 200

        data = response.json()
        for item in data:
            assert item.get("rede") == "Municipal"

    def test_pagination(self, client):
        """Testa paginação."""
        response = client.get("/municipios?limit=5")
        assert response.status_code == 200

        data = response.json()
        assert len(data) <= 5


class TestAPIErrorHandling:
    """Testes de tratamento de erros."""

    def test_endpoint_not_found(self, client):
        """Testa endpoint inexistente."""
        response = client.get("/endpoint_inexistente")
        assert response.status_code == 404

    def test_invalid_parameter(self, client):
        """Testa parâmetro inválido."""
        response = client.get("/saude/mortalidade?ano=invalid")
        # Deve retornar erro de validação
        assert response.status_code in [400, 422]
