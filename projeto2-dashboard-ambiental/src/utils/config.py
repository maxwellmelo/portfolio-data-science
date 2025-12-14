"""
Configurações centralizadas do Dashboard Ambiental
"""

import os
from pathlib import Path
from typing import Dict, List

# Diretórios do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Criar diretórios se não existirem
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, ASSETS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# URLs das APIs e Serviços do INPE/TerraBrasilis
TERRABRASILIS_BASE_URL = "http://terrabrasilis.dpi.inpe.br"
TERRABRASILIS_GEOSERVER = f"{TERRABRASILIS_BASE_URL}/geoserver/ows"

# Serviços WFS para diferentes biomas e programas
WFS_SERVICES = {
    "prodes_cerrado": {
        "url": f"{TERRABRASILIS_BASE_URL}/geoserver/prodes-cerrado/ows",
        "workspace": "prodes-cerrado",
        "layers": [
            "prodes-cerrado:yearly_deforestation",
            "prodes-cerrado:accumulated_deforestation"
        ]
    },
    "prodes_amazonia": {
        "url": f"{TERRABRASILIS_BASE_URL}/geoserver/prodes-amazonia/ows",
        "workspace": "prodes-amazonia",
        "layers": [
            "prodes-amazonia:yearly_deforestation",
            "prodes-amazonia:accumulated_deforestation"
        ]
    }
}

# Configurações de Estados e Biomas
ESTADOS_BRASIL = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
}

# Estados do Cerrado (com destaque para Piauí)
ESTADOS_CERRADO = ["GO", "TO", "MT", "MS", "DF", "MG", "BA", "MA", "PI", "RO", "PR", "SP"]

# Estados da Amazônia Legal
ESTADOS_AMAZONIA = ["AC", "AP", "AM", "PA", "RO", "RR", "TO", "MT", "MA"]

BIOMAS = {
    "Amazônia": {"color": "#006400", "states": ESTADOS_AMAZONIA},
    "Cerrado": {"color": "#FFD700", "states": ESTADOS_CERRADO},
    "Mata Atlântica": {"color": "#228B22", "states": ["BA", "ES", "GO", "MS", "MG", "PR", "RJ", "SC", "SP"]},
    "Caatinga": {"color": "#DEB887", "states": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"]},
    "Pantanal": {"color": "#4682B4", "states": ["MT", "MS"]},
    "Pampa": {"color": "#90EE90", "states": ["RS"]}
}

# Dados de 2025 (preliminares) - conforme pesquisa do INPE
DADOS_2025_PRELIM = {
    "cerrado": {
        "taxa_total_km2": 7235,
        "reducao_percentual": 11.49,
        "estados_maiores_desmatadores": {
            "MA": 2006,
            "TO": 1489,
            "PI": 1350
        }
    },
    "amazonia": {
        "reducao_registrada": True,
        "dados_detalhados": "Aguardando consolidação primeiro semestre 2026"
    }
}

# Configurações de visualização
CHART_CONFIG = {
    "template": "plotly_white",
    "color_palette": ["#1f7a1f", "#ff6b6b", "#4ecdc4", "#ffe66d", "#a8e6cf"],
    "map_style": "OpenStreetMap",
    "height_default": 500,
    "width_default": 800
}

# Range de anos disponíveis
ANOS_DISPONIVEIS = list(range(2000, 2026))

# Configurações de cache
CACHE_CONFIG = {
    "ttl": 3600 * 24,  # 24 horas
    "max_entries": 1000
}

# Mensagens e textos do dashboard
TEXTOS = {
    "titulo": "🌳 Dashboard Ambiental - Desmatamento no Brasil",
    "subtitulo": "Análise de dados do PRODES/INPE com foco no Cerrado e Piauí",
    "descricao": """
    Este dashboard apresenta dados oficiais de desmatamento do INPE (Instituto Nacional de Pesquisas Espaciais)
    através do programa PRODES, com ênfase no bioma Cerrado e no estado do Piauí.
    """,
    "fonte_dados": "Fonte: INPE/TerraBrasilis - PRODES",
    "aviso_dados_preliminares": "⚠️ Dados de 2025 são preliminares. Consolidação prevista para primeiro semestre de 2026."
}

def get_config(key: str, default=None):
    """Retorna valor de configuração"""
    return os.getenv(key, default)

def get_file_path(filename: str, data_type: str = "raw") -> Path:
    """Retorna caminho completo para arquivo de dados"""
    if data_type == "raw":
        return RAW_DATA_DIR / filename
    elif data_type == "processed":
        return PROCESSED_DATA_DIR / filename
    else:
        return DATA_DIR / filename
