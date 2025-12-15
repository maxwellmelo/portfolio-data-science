"""
API REST para consulta de dados integrados do Piauí.

Endpoints para acesso aos dados de:
- Saúde (mortalidade, nascimentos)
- Educação (escolas, IDEB)
- Economia (PIB, empresas)
- Assistência Social (CadÚnico)
"""

from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import pandas as pd
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings, FONTES_DADOS, MUNICIPIOS_PIAUI
from src.extractors import SyntheticDataGenerator
from src.api.data_loader import DataLoader, get_data_loader


# ========== Modelos Pydantic ==========

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str


class MunicipioInfo(BaseModel):
    codigo_ibge: int
    nome: str
    uf: str = "PI"


class FonteDados(BaseModel):
    nome: str
    descricao: str
    datasets: List[str]
    frequencia_atualizacao: str
    url: str


class IndicadorSaude(BaseModel):
    municipio_id: int
    municipio_nome: str
    ano: int
    total_obitos: int
    total_nascimentos: int
    taxa_mortalidade: Optional[float] = None
    taxa_natalidade: Optional[float] = None


class IndicadorEducacao(BaseModel):
    municipio_id: int
    municipio_nome: str
    ano: int
    total_escolas: int
    total_alunos: int
    ideb_anos_iniciais: Optional[float] = None
    ideb_anos_finais: Optional[float] = None


class IndicadorEconomia(BaseModel):
    municipio_id: int
    municipio_nome: str
    ano: int
    pib_total_mil_reais: float
    pib_per_capita: float
    populacao_estimada: int


class PaginatedResponse(BaseModel):
    data: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int


# ========== Aplicação FastAPI ==========

def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""

    app = FastAPI(
        title=settings.api.title,
        version=settings.api.version,
        description="""
        API para consulta de dados integrados multissetoriais do estado do Piauí.

        ## Fontes de Dados
        - **Saúde**: DATASUS (SIM, SINASC, SIH)
        - **Educação**: INEP (Censo Escolar, IDEB)
        - **Economia**: IBGE (PIB, Empresas)
        - **Assistência Social**: MDS (Cadastro Único)

        ## Funcionalidades
        - Consulta por município
        - Filtros por período
        - Agregações e indicadores
        - Paginação de resultados
        """,
        docs_url=settings.api.docs_url,
        redoc_url=settings.api.redoc_url
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()

# Cache de dados (em produção, usar Redis)
_data_cache = {}
_data_loader: DataLoader = None


def get_data_generator():
    """Retorna instância do gerador de dados."""
    return SyntheticDataGenerator()


def get_loader() -> DataLoader:
    """Retorna instância do DataLoader."""
    global _data_loader
    if _data_loader is None:
        _data_loader = get_data_loader()
    return _data_loader


def load_cached_data(generator: SyntheticDataGenerator) -> dict:
    """Carrega dados em cache, priorizando dados reais."""
    loader = get_loader()
    return loader.load_all(generator)


# ========== Endpoints ==========

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz com informações da API."""
    return {
        "api": settings.api.title,
        "version": settings.api.version,
        "docs": settings.api.docs_url,
        "status": "online"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Verifica status da API."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.api.version
    )


@app.get("/fontes", response_model=List[FonteDados], tags=["Metadados"])
async def listar_fontes():
    """Lista todas as fontes de dados disponíveis."""
    return [
        FonteDados(**fonte)
        for fonte in FONTES_DADOS.values()
    ]


@app.get("/fontes/status", tags=["Metadados"])
async def status_fontes(generator: SyntheticDataGenerator = Depends(get_data_generator)):
    """
    Mostra status das fontes de dados carregadas.

    Indica quais datasets contêm dados reais (IBGE) vs sintéticos.
    """
    # Garantir que os dados estão carregados
    load_cached_data(generator)
    loader = get_loader()

    return {
        "resumo": {
            "total_datasets": len(loader._sources),
            "datasets_reais": sum(1 for s in loader._sources.values() if s.is_real),
            "datasets_sinteticos": sum(1 for s in loader._sources.values() if not s.is_real)
        },
        "datasets": loader.get_data_sources()
    }


@app.get("/municipios", response_model=List[MunicipioInfo], tags=["Metadados"])
async def listar_municipios():
    """Lista municípios do Piauí disponíveis."""
    return [
        MunicipioInfo(codigo_ibge=codigo, nome=nome)
        for codigo, nome in MUNICIPIOS_PIAUI.items()
    ]


@app.get("/saude/mortalidade", tags=["Saúde"])
async def consultar_mortalidade(
    municipio_id: Optional[int] = Query(None, description="Código IBGE do município"),
    ano: Optional[int] = Query(None, description="Ano de referência"),
    causa: Optional[str] = Query(None, description="CID da causa básica"),
    page: int = Query(1, ge=1, description="Página"),
    page_size: int = Query(100, ge=1, le=1000, description="Registros por página"),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Consulta dados de mortalidade (SIM/DATASUS).

    Retorna registros de óbitos com:
    - Causa básica (CID)
    - Dados demográficos
    - Local de ocorrência
    """
    data = load_cached_data(generator)
    df = data["saude_mortalidade"].copy()

    # Filtros
    if municipio_id:
        df = df[df["municipio_id"] == municipio_id]
    if ano:
        df = df[df["ano"] == ano]
    if causa:
        df = df[df["cid_principal"].str.contains(causa, case=False)]

    # Paginação
    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    df_page = df.iloc[start:end]

    return PaginatedResponse(
        data=df_page.to_dict("records"),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@app.get("/saude/nascimentos", tags=["Saúde"])
async def consultar_nascimentos(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """Consulta dados de nascidos vivos (SINASC)."""
    data = load_cached_data(generator)
    df = data["saude_nascimentos"].copy()

    if municipio_id:
        df = df[df["municipio_id"] == municipio_id]
    if ano:
        df = df[df["ano"] == ano]

    total = len(df)
    start = (page - 1) * page_size
    df_page = df.iloc[start:start + page_size]

    return PaginatedResponse(
        data=df_page.to_dict("records"),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@app.get("/educacao/escolas", tags=["Educação"])
async def consultar_escolas(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    dependencia: Optional[str] = Query(None, description="Estadual, Municipal, Privada, Federal"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """Consulta dados de escolas (Censo Escolar)."""
    data = load_cached_data(generator)
    df = data["educacao_escolas"].copy()

    if municipio_id:
        df = df[df["municipio_id"] == municipio_id]
    if ano:
        df = df[df["ano"] == ano]
    if dependencia:
        df = df[df["dependencia_administrativa"] == dependencia]

    total = len(df)
    start = (page - 1) * page_size
    df_page = df.iloc[start:start + page_size]

    return PaginatedResponse(
        data=df_page.to_dict("records"),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@app.get("/educacao/ideb", tags=["Educação"])
async def consultar_ideb(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    etapa: Optional[str] = Query(None, description="Anos Iniciais, Anos Finais, Ensino Médio"),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """Consulta dados do IDEB."""
    data = load_cached_data(generator)
    df = data["educacao_ideb"].copy()

    if municipio_id:
        df = df[df["municipio_id"] == municipio_id]
    if ano:
        df = df[df["ano"] == ano]
    if etapa:
        df = df[df["etapa_ensino"] == etapa]

    return df.to_dict("records")


@app.get("/economia/pib", tags=["Economia"])
async def consultar_pib(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Consulta dados de PIB municipal.

    **DADOS REAIS DO IBGE** (quando disponíveis):
    - Fonte: IBGE - Sistema de Contas Regionais
    - Anos: 2020, 2021
    - 224 municípios do Piauí
    """
    data = load_cached_data(generator)
    loader = get_loader()

    df = data["economia_pib"].copy()

    if municipio_id:
        df = df[df["municipio_id"] == municipio_id]
    if ano:
        df = df[df["ano"] == ano]

    # Verificar se são dados reais
    is_real = loader.is_real_data("economia_pib")

    return {
        "dados_reais": is_real,
        "fonte": "IBGE - Sistema de Contas Regionais" if is_real else "Dados Sintéticos",
        "total_registros": len(df),
        "data": df.to_dict("records")
    }


@app.get("/assistencia/cadunico", tags=["Assistência Social"])
async def consultar_cadunico(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    faixa_renda: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """Consulta dados do Cadastro Único."""
    data = load_cached_data(generator)
    df = data["assistencia_cadunico"].copy()

    if municipio_id:
        df = df[df["municipio_id"] == municipio_id]
    if ano:
        df = df[df["ano"] == ano]
    if faixa_renda:
        df = df[df["faixa_renda"] == faixa_renda]

    total = len(df)
    start = (page - 1) * page_size
    df_page = df.iloc[start:start + page_size]

    return PaginatedResponse(
        data=df_page.to_dict("records"),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@app.get("/indicadores/{municipio_id}", tags=["Indicadores"])
async def indicadores_municipio(
    municipio_id: int,
    ano: int = Query(2021, description="Ano de referência (2021 para dados reais de PIB)"),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Retorna indicadores consolidados de um município.

    Agrega dados de todas as fontes para visão integrada.

    **Nota**: Para dados econômicos reais do IBGE, use ano=2020 ou ano=2021.
    """
    if municipio_id not in MUNICIPIOS_PIAUI:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    data = load_cached_data(generator)
    loader = get_loader()

    # Saúde
    mort = data["saude_mortalidade"]
    mort_mun = mort[(mort["municipio_id"] == municipio_id) & (mort["ano"] == ano)]

    nasc = data["saude_nascimentos"]
    nasc_mun = nasc[(nasc["municipio_id"] == municipio_id) & (nasc["ano"] == ano)]

    # Educação
    escolas = data["educacao_escolas"]
    escolas_mun = escolas[(escolas["municipio_id"] == municipio_id) & (escolas["ano"] == ano)]

    ideb = data["educacao_ideb"]
    ideb_mun = ideb[(ideb["municipio_id"] == municipio_id) & (ideb["ano"] <= ano)]

    # Economia (pode ser dado real)
    pib = data["economia_pib"]
    pib_mun = pib[(pib["municipio_id"] == municipio_id) & (pib["ano"] == ano)]

    # Se não encontrou no ano solicitado, tentar ano mais próximo disponível
    if len(pib_mun) == 0:
        pib_mun_all = pib[pib["municipio_id"] == municipio_id]
        if len(pib_mun_all) > 0:
            ano_mais_proximo = pib_mun_all["ano"].max()
            pib_mun = pib_mun_all[pib_mun_all["ano"] == ano_mais_proximo]

    # Assistência
    cad = data["assistencia_cadunico"]
    cad_mun = cad[(cad["municipio_id"] == municipio_id) & (cad["ano"] == ano)]

    # Verificar fontes
    economia_real = loader.is_real_data("economia_pib")

    return {
        "municipio": {
            "id": municipio_id,
            "nome": MUNICIPIOS_PIAUI[municipio_id],
            "uf": "PI"
        },
        "ano_referencia": ano,
        "fontes": {
            "economia": "IBGE - Dados Reais" if economia_real else "Dados Sintéticos",
            "saude": "Dados Sintéticos",
            "educacao": "Dados Sintéticos",
            "assistencia": "Dados Sintéticos"
        },
        "saude": {
            "total_obitos": len(mort_mun),
            "total_nascimentos": len(nasc_mun),
            "principais_causas": mort_mun["causa_basica"].value_counts().head(5).to_dict() if len(mort_mun) > 0 else {},
            "dados_reais": False
        },
        "educacao": {
            "total_escolas": len(escolas_mun),
            "total_alunos": int(escolas_mun["total_alunos"].sum()) if len(escolas_mun) > 0 else 0,
            "ideb_mais_recente": float(ideb_mun[ideb_mun["ano"] == ideb_mun["ano"].max()]["ideb"].mean()) if len(ideb_mun) > 0 else None,
            "dados_reais": False
        },
        "economia": {
            "ano_dados": int(pib_mun["ano"].iloc[0]) if len(pib_mun) > 0 else None,
            "pib_total_mil_reais": float(pib_mun["pib_total_mil_reais"].sum()) if len(pib_mun) > 0 else 0,
            "pib_per_capita": float(pib_mun["pib_per_capita"].mean()) if len(pib_mun) > 0 and "pib_per_capita" in pib_mun.columns else 0,
            "populacao_estimada": int(pib_mun["populacao_estimada"].sum()) if len(pib_mun) > 0 and "populacao_estimada" in pib_mun.columns else 0,
            "dados_reais": economia_real
        },
        "assistencia": {
            "familias_cadastradas": len(cad_mun),
            "familias_extrema_pobreza": len(cad_mun[cad_mun["faixa_renda"] == "Extrema pobreza"]) if len(cad_mun) > 0 else 0,
            "familias_bolsa_familia": len(cad_mun[cad_mun["recebe_bolsa_familia"] == True]) if len(cad_mun) > 0 else 0,
            "dados_reais": False
        }
    }


# ========== Execução ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api.host, port=settings.api.port)
