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

# Municipios do Piaui - Lista completa (224 municipios)
# Fonte: API IBGE - https://servicodados.ibge.gov.br/api/v1/localidades/estados/22/municipios
MUNICIPIOS_PIAUI = {
    2200053: "Acauã",
    2200103: "Agricolândia",
    2200202: "Água Branca",
    2200251: "Alagoinha do Piauí",
    2200277: "Alegrete do Piauí",
    2200301: "Alto Longá",
    2200400: "Altos",
    2200459: "Alvorada do Gurguéia",
    2200509: "Amarante",
    2200608: "Angical do Piauí",
    2200707: "Anísio de Abreu",
    2200806: "Antônio Almeida",
    2200905: "Aroazes",
    2200954: "Aroeiras do Itaim",
    2201002: "Arraial",
    2201051: "Assunção do Piauí",
    2201101: "Avelino Lopes",
    2201150: "Baixa Grande do Ribeiro",
    2201176: "Barra D'Alcântara",
    2201200: "Barras",
    2201309: "Barreiras do Piauí",
    2201408: "Barro Duro",
    2201507: "Batalha",
    2201556: "Bela Vista do Piauí",
    2201572: "Belém do Piauí",
    2201606: "Beneditinos",
    2201705: "Bertolínia",
    2201739: "Betânia do Piauí",
    2201770: "Boa Hora",
    2201804: "Bocaina",
    2201903: "Bom Jesus",
    2201919: "Bom Princípio do Piauí",
    2201929: "Bonfim do Piauí",
    2201945: "Boqueirão do Piauí",
    2201960: "Brasileira",
    2201988: "Brejo do Piauí",
    2202000: "Buriti dos Lopes",
    2202026: "Buriti dos Montes",
    2202059: "Cabeceiras do Piauí",
    2202075: "Cajazeiras do Piauí",
    2202083: "Cajueiro da Praia",
    2202091: "Caldeirão Grande do Piauí",
    2202109: "Campinas do Piauí",
    2202117: "Campo Alegre do Fidalgo",
    2202133: "Campo Grande do Piauí",
    2202174: "Campo Largo do Piauí",
    2202208: "Campo Maior",
    2202251: "Canavieira",
    2202307: "Canto do Buriti",
    2202406: "Capitão de Campos",
    2202455: "Capitão Gervásio Oliveira",
    2202505: "Caracol",
    2202539: "Caraúbas do Piauí",
    2202554: "Caridade do Piauí",
    2202604: "Castelo do Piauí",
    2202653: "Caxingó",
    2202703: "Cocal",
    2202711: "Cocal de Telha",
    2202729: "Cocal dos Alves",
    2202737: "Coivaras",
    2202752: "Colônia do Gurguéia",
    2202778: "Colônia do Piauí",
    2202802: "Conceição do Canindé",
    2202851: "Coronel José Dias",
    2202901: "Corrente",
    2203008: "Cristalândia do Piauí",
    2203107: "Cristino Castro",
    2203206: "Curimatá",
    2203230: "Currais",
    2203255: "Curralinhos",
    2203271: "Curral Novo do Piauí",
    2203305: "Demerval Lobão",
    2203354: "Dirceu Arcoverde",
    2203404: "Dom Expedito Lopes",
    2203420: "Domingos Mourão",
    2203453: "Dom Inocêncio",
    2203503: "Elesbão Veloso",
    2203602: "Eliseu Martins",
    2203701: "Esperantina",
    2203750: "Fartura do Piauí",
    2203800: "Flores do Piauí",
    2203859: "Floresta do Piauí",
    2203909: "Floriano",
    2204006: "Francinópolis",
    2204105: "Francisco Ayres",
    2204154: "Francisco Macedo",
    2204204: "Francisco Santos",
    2204303: "Fronteiras",
    2204352: "Geminiano",
    2204402: "Gilbués",
    2204501: "Guadalupe",
    2204550: "Guaribas",
    2204600: "Hugo Napoleão",
    2204659: "Ilha Grande",
    2204709: "Inhuma",
    2204808: "Ipiranga do Piauí",
    2204907: "Isaías Coelho",
    2205003: "Itainópolis",
    2205102: "Itaueira",
    2205151: "Jacobina do Piauí",
    2205201: "Jaicós",
    2205250: "Jardim do Mulato",
    2205276: "Jatobá do Piauí",
    2205300: "Jerumenha",
    2205359: "João Costa",
    2205409: "Joaquim Pires",
    2205458: "Joca Marques",
    2205508: "José de Freitas",
    2205516: "Juazeiro do Piauí",
    2205524: "Júlio Borges",
    2205532: "Jurema",
    2205540: "Lagoinha do Piauí",
    2205557: "Lagoa Alegre",
    2205565: "Lagoa do Barro do Piauí",
    2205573: "Lagoa de São Francisco",
    2205581: "Lagoa do Piauí",
    2205599: "Lagoa do Sítio",
    2205607: "Landri Sales",
    2205706: "Luís Correia",
    2205805: "Luzilândia",
    2205854: "Madeiro",
    2205904: "Manoel Emídio",
    2205953: "Marcolândia",
    2206001: "Marcos Parente",
    2206050: "Massapê do Piauí",
    2206100: "Matias Olímpio",
    2206209: "Miguel Alves",
    2206308: "Miguel Leão",
    2206357: "Milton Brandão",
    2206407: "Monsenhor Gil",
    2206506: "Monsenhor Hipólito",
    2206605: "Monte Alegre do Piauí",
    2206654: "Morro Cabeça no Tempo",
    2206670: "Morro do Chapéu do Piauí",
    2206696: "Murici dos Portelas",
    2206704: "Nazaré do Piauí",
    2206720: "Nazária",
    2206753: "Nossa Senhora de Nazaré",
    2206803: "Nossa Senhora dos Remédios",
    2206902: "Novo Oriente do Piauí",
    2206951: "Novo Santo Antônio",
    2207009: "Oeiras",
    2207108: "Olho D'Água do Piauí",
    2207207: "Padre Marcos",
    2207306: "Paes Landim",
    2207355: "Pajeú do Piauí",
    2207405: "Palmeira do Piauí",
    2207504: "Palmeirais",
    2207553: "Paquetá",
    2207603: "Parnaguá",
    2207702: "Parnaíba",
    2207751: "Passagem Franca do Piauí",
    2207777: "Patos do Piauí",
    2207793: "Pau D'Arco do Piauí",
    2207801: "Paulistana",
    2207850: "Pavussu",
    2207900: "Pedro II",
    2207934: "Pedro Laurentino",
    2207959: "Nova Santa Rita",
    2208007: "Picos",
    2208106: "Pimenteiras",
    2208205: "Pio IX",
    2208304: "Piracuruca",
    2208403: "Piripiri",
    2208502: "Porto",
    2208551: "Porto Alegre do Piauí",
    2208601: "Prata do Piauí",
    2208650: "Queimada Nova",
    2208700: "Redenção do Gurguéia",
    2208809: "Regeneração",
    2208858: "Riacho Frio",
    2208874: "Ribeira do Piauí",
    2208908: "Ribeiro Gonçalves",
    2209005: "Rio Grande do Piauí",
    2209104: "Santa Cruz do Piauí",
    2209153: "Santa Cruz dos Milagres",
    2209203: "Santa Filomena",
    2209302: "Santa Luz",
    2209351: "Santana do Piauí",
    2209377: "Santa Rosa do Piauí",
    2209401: "Santo Antônio de Lisboa",
    2209450: "Santo Antônio dos Milagres",
    2209500: "Santo Inácio do Piauí",
    2209559: "São Braz do Piauí",
    2209609: "São Félix do Piauí",
    2209658: "São Francisco de Assis do Piauí",
    2209708: "São Francisco do Piauí",
    2209757: "São Gonçalo do Gurguéia",
    2209807: "São Gonçalo do Piauí",
    2209856: "São João da Canabrava",
    2209872: "São João da Fronteira",
    2209906: "São João da Serra",
    2209955: "São João da Varjota",
    2209971: "São João do Arraial",
    2210003: "São João do Piauí",
    2210052: "São José do Divino",
    2210102: "São José do Peixe",
    2210201: "São José do Piauí",
    2210300: "São Julião",
    2210359: "São Lourenço do Piauí",
    2210375: "São Luis do Piauí",
    2210383: "São Miguel da Baixa Grande",
    2210391: "São Miguel do Fidalgo",
    2210409: "São Miguel do Tapuio",
    2210508: "São Pedro do Piauí",
    2210607: "São Raimundo Nonato",
    2210623: "Sebastião Barros",
    2210631: "Sebastião Leal",
    2210656: "Sigefredo Pacheco",
    2210706: "Simões",
    2210805: "Simplício Mendes",
    2210904: "Socorro do Piauí",
    2210938: "Sussuapara",
    2210953: "Tamboril do Piauí",
    2210979: "Tanque do Piauí",
    2211001: "Teresina",
    2211100: "União",
    2211209: "Uruçuí",
    2211308: "Valença do Piauí",
    2211357: "Várzea Branca",
    2211407: "Várzea Grande",
    2211506: "Vera Mendes",
    2211605: "Vila Nova do Piauí",
    2211704: "Wall Ferraz",
}
