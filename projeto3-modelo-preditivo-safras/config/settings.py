"""
Configurações do projeto de Modelo Preditivo de Safras Agrícolas.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import List, Optional
from functools import lru_cache


# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent


class DataSettings(BaseSettings):
    """Configurações de dados."""

    raw_dir: str = Field(default="data/raw")
    processed_dir: str = Field(default="data/processed")
    models_dir: str = Field(default="data/models")

    # API SIDRA/IBGE
    sidra_base_url: str = Field(
        default="https://servicodados.ibge.gov.br/api/v3/agregados"
    )

    # Agregados da PAM (Produção Agrícola Municipal)
    agregado_pam_lavouras_temporarias: int = 1612  # Área plantada, colhida, produção
    agregado_pam_lavouras_permanentes: int = 1613
    agregado_pam_rendimento: int = 5457  # Rendimento médio

    # Culturas principais para análise
    culturas_foco: List[str] = [
        "Soja (em grão)",
        "Milho (em grão)",
        "Arroz (em casca)",
        "Feijão (em grão)",
        "Algodão herbáceo (em caroço)",
        "Cana-de-açúcar",
        "Café (em grão) Total",
        "Mandioca"
    ]

    # Estados do Piauí e vizinhos para foco regional
    estados_foco: List[str] = ["PI", "MA", "BA", "TO", "CE"]

    class Config:
        env_file = ".env"
        extra = "ignore"


class ModelSettings(BaseSettings):
    """Configurações de modelagem."""

    # Train/Test Split
    test_size: float = Field(default=0.2)
    random_state: int = Field(default=42)

    # Cross Validation
    cv_folds: int = Field(default=5)

    # Target
    target_column: str = Field(default="rendimento_kg_ha")

    # Features numéricas esperadas
    numeric_features: List[str] = [
        "area_plantada_ha",
        "area_colhida_ha",
        "producao_ton",
        "ano",
        "latitude",
        "longitude"
    ]

    # Features categóricas
    categorical_features: List[str] = [
        "cultura",
        "estado",
        "regiao",
        "municipio_porte"
    ]

    # Modelos a treinar
    models_to_train: List[str] = [
        "linear_regression",
        "ridge",
        "lasso",
        "random_forest",
        "gradient_boosting",
        "xgboost",
        "lightgbm"
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"


class Settings(BaseSettings):
    """Configurações centralizadas."""

    project_name: str = "Modelo Preditivo - Safras Agrícolas"
    version: str = "1.0.0"

    data: DataSettings = DataSettings()
    model: ModelSettings = ModelSettings()

    # Logging
    log_level: str = Field(default="INFO")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()


settings = get_settings()


# Códigos das culturas no SIDRA
CODIGOS_CULTURAS = {
    "Soja (em grão)": 39,
    "Milho (em grão)": 33,
    "Arroz (em casca)": 31,
    "Feijão (em grão)": 32,
    "Algodão herbáceo (em caroço)": 10,
    "Cana-de-açúcar": 15,
    "Café (em grão) Total": 14,
    "Mandioca": 34,
    "Trigo (em grão)": 40,
    "Sorgo (em grão)": 38
}

# Códigos dos estados
CODIGOS_ESTADOS = {
    "RO": 11, "AC": 12, "AM": 13, "RR": 14, "PA": 15, "AP": 16, "TO": 17,
    "MA": 21, "PI": 22, "CE": 23, "RN": 24, "PB": 25, "PE": 26, "AL": 27,
    "SE": 28, "BA": 29, "MG": 31, "ES": 32, "RJ": 33, "SP": 35,
    "PR": 41, "SC": 42, "RS": 43, "MS": 50, "MT": 51, "GO": 52, "DF": 53
}

# Regiões
REGIOES = {
    "Norte": ["RO", "AC", "AM", "RR", "PA", "AP", "TO"],
    "Nordeste": ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"],
    "Sudeste": ["MG", "ES", "RJ", "SP"],
    "Sul": ["PR", "SC", "RS"],
    "Centro-Oeste": ["MS", "MT", "GO", "DF"]
}
