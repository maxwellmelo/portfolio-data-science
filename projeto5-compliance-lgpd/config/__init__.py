"""Módulo de configurações."""
from .settings import (
    settings, get_settings,
    DADOS_SENSIVEIS_LGPD, BASES_LEGAIS_LGPD, DIREITOS_TITULARES,
    SensitivityLevel, DataCategory
)

__all__ = [
    "settings", "get_settings",
    "DADOS_SENSIVEIS_LGPD", "BASES_LEGAIS_LGPD", "DIREITOS_TITULARES",
    "SensitivityLevel", "DataCategory"
]
