"""
Configurações do projeto ETL IBGE.
Utiliza Pydantic Settings para gerenciamento de variáveis de ambiente.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Configurações do banco de dados PostgreSQL."""

    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=5432, alias="DB_PORT")
    database: str = Field(default="ibge_data", alias="DB_NAME")
    user: str = Field(default="postgres", alias="DB_USER")
    password: str = Field(default="postgres", alias="DB_PASSWORD")
    schema: str = Field(default="public", alias="DB_SCHEMA")

    @property
    def connection_string(self) -> str:
        """Retorna a string de conexão do PostgreSQL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def async_connection_string(self) -> str:
        """Retorna a string de conexão assíncrona."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    class Config:
        env_file = ".env"
        extra = "ignore"


class IBGEApiSettings(BaseSettings):
    """Configurações da API do IBGE."""

    base_url: str = Field(
        default="https://servicodados.ibge.gov.br/api/v1",
        alias="IBGE_BASE_URL"
    )
    sidra_url: str = Field(
        default="https://servicodados.ibge.gov.br/api/v3/agregados",
        alias="IBGE_SIDRA_URL"
    )
    timeout: int = Field(default=60, alias="IBGE_TIMEOUT")
    retry_attempts: int = Field(default=3, alias="IBGE_RETRY_ATTEMPTS")
    rate_limit_delay: float = Field(default=0.5, alias="IBGE_RATE_LIMIT_DELAY")

    class Config:
        env_file = ".env"
        extra = "ignore"


class ETLSettings(BaseSettings):
    """Configurações do pipeline ETL."""

    batch_size: int = Field(default=1000, alias="ETL_BATCH_SIZE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    data_dir: str = Field(default="data", alias="DATA_DIR")

    class Config:
        env_file = ".env"
        extra = "ignore"


class Settings(BaseSettings):
    """Configurações centralizadas do projeto."""

    project_name: str = "ETL Pipeline IBGE"
    version: str = "1.0.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Sub-configurações
    database: DatabaseSettings = DatabaseSettings()
    ibge_api: IBGEApiSettings = IBGEApiSettings()
    etl: ETLSettings = ETLSettings()

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância cacheada das configurações.
    Use esta função para acessar as configurações em todo o projeto.
    """
    return Settings()


# Instância global para acesso direto
settings = get_settings()
