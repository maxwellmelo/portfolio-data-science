"""
Configurações do Sistema de Integração Multissetorial.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Dict, Optional
from functools import lru_cache
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent


class DatabaseSettings(BaseSettings):
    """Configurações do banco de dados."""

    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=5432, alias="DB_PORT")
    database: str = Field(default="piaui_integrado", alias="DB_NAME")
    user: str = Field(default="postgres", alias="DB_USER")
    password: str = Field(default="postgres", alias="DB_PASSWORD")
    schema_staging: str = Field(default="staging")
    schema_dwh: str = Field(default="dwh")

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    class Config:
        env_file = ".env"
        extra = "ignore"


class APISettings(BaseSettings):
    """Configurações da API REST."""

    host: str = Field(default="0.0.0.0", alias="API_HOST")
    port: int = Field(default=8000, alias="API_PORT")
    debug: bool = Field(default=False, alias="API_DEBUG")
    title: str = "API de Dados Integrados do Piauí"
    version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # segundos

    # CORS
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"


class SourceSettings(BaseSettings):
    """Configurações das fontes de dados."""

    # DATASUS
    datasus_base_url: str = "https://datasus.saude.gov.br"
    datasus_ftp: str = "ftp.datasus.gov.br"

    # INEP
    inep_base_url: str = "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos"

    # IBGE
    ibge_api_url: str = "https://servicodados.ibge.gov.br/api/v3"

    # Códigos do Piauí
    codigo_uf_piaui: int = 22
    codigo_ibge_teresina: int = 2211001

    class Config:
        env_file = ".env"
        extra = "ignore"


class OrchestrationSettings(BaseSettings):
    """Configurações de orquestração."""

    # Prefect
    prefect_api_url: str = Field(default="http://localhost:4200/api", alias="PREFECT_API_URL")

    # Schedule (cron)
    schedule_daily: str = "0 6 * * *"  # 6h diariamente
    schedule_weekly: str = "0 6 * * 0"  # Domingo 6h

    # Retry
    max_retries: int = 3
    retry_delay_seconds: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"


class Settings(BaseSettings):
    """Configurações centralizadas."""

    project_name: str = "Sistema de Integração Multissetorial - Piauí"
    version: str = "1.0.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")

    database: DatabaseSettings = DatabaseSettings()
    api: APISettings = APISettings()
    sources: SourceSettings = SourceSettings()
    orchestration: OrchestrationSettings = OrchestrationSettings()

    # Diretórios
    data_dir: str = "data"
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


# Metadados das fontes de dados
FONTES_DADOS = {
    "saude": {
        "nome": "DATASUS",
        "descricao": "Sistema de Informações de Saúde",
        "datasets": [
            "SIM - Sistema de Informações sobre Mortalidade",
            "SINASC - Sistema de Informações sobre Nascidos Vivos",
            "SIH - Sistema de Informações Hospitalares",
            "SIA - Sistema de Informações Ambulatoriais"
        ],
        "frequencia_atualizacao": "mensal",
        "url": "https://datasus.saude.gov.br/"
    },
    "educacao": {
        "nome": "INEP",
        "descricao": "Instituto Nacional de Estudos e Pesquisas Educacionais",
        "datasets": [
            "Censo Escolar",
            "IDEB - Índice de Desenvolvimento da Educação Básica",
            "ENEM - Exame Nacional do Ensino Médio",
            "Censo da Educação Superior"
        ],
        "frequencia_atualizacao": "anual",
        "url": "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos"
    },
    "economia": {
        "nome": "IBGE",
        "descricao": "Instituto Brasileiro de Geografia e Estatística",
        "datasets": [
            "PIB Municipal",
            "Cadastro Central de Empresas",
            "PAM - Produção Agrícola Municipal",
            "Pesquisa Nacional por Amostra de Domicílios"
        ],
        "frequencia_atualizacao": "anual",
        "url": "https://www.ibge.gov.br/"
    },
    "assistencia_social": {
        "nome": "MDS",
        "descricao": "Ministério do Desenvolvimento Social",
        "datasets": [
            "Cadastro Único",
            "Bolsa Família / Auxílio Brasil",
            "BPC - Benefício de Prestação Continuada"
        ],
        "frequencia_atualizacao": "mensal",
        "url": "https://aplicacoes.mds.gov.br/sagi/"
    }
}

# Municípios do Piauí (principais)
MUNICIPIOS_PIAUI = {
    2211001: "Teresina",
    2207702: "Parnaíba",
    2211100: "Picos",
    2205003: "Floriano",
    2200509: "Barras",
    2201408: "Campo Maior",
    2210102: "Piripiri",
    2200400: "Altos",
    2203909: "Esperantina",
    2206902: "Oeiras"
}
