"""Módulo de extração de dados."""

from .ibge_client import IBGEClient
from .localidades import LocalidadesExtractor
from .populacao import PopulacaoExtractor
from .pib import PIBExtractor

__all__ = [
    "IBGEClient",
    "LocalidadesExtractor",
    "PopulacaoExtractor",
    "PIBExtractor"
]
