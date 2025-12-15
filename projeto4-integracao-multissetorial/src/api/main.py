"""
API REST - Sistema Integrado de Dados do Piaui (Prototipo BDG).

API multissetorial para consulta de dados integrados:
- Economia (PIB, Populacao) - IBGE Real
- Saude (Mortalidade, Vacinacao) - DATASUS
- Educacao (IDEB, Escolas) - INEP
- Assistencia Social (CadUnico) - MDS

Funcionalidades:
- Consultas por setor e municipio
- Analises cruzadas entre setores
- Identificacao de municipios prioritarios
- Comparativos entre mesorregioes
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


class PaginatedResponse(BaseModel):
    data: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int


class CorrelacaoResponse(BaseModel):
    indicadores: List[str]
    matriz: dict
    insights: List[str]


class MunicipioPrioritario(BaseModel):
    municipio_id: int
    municipio_nome: str
    mesorregiao: str
    indice_vulnerabilidade: float
    classificacao: str


# ========== Aplicacao FastAPI ==========

def create_app() -> FastAPI:
    """Cria e configura a aplicacao FastAPI."""

    app = FastAPI(
        title="Sistema Integrado de Dados do Piaui - Prototipo BDG",
        version="2.0.0",
        description="""
        ## Sistema Integrado de Dados Multissetoriais do Piaui

        API REST para consulta de dados governamentais integrados dos 224 municipios do Piaui.
        Prototipo de Banco de Dados Geografico (BDG) para apoio a gestao de politicas publicas.

        ### Setores Integrados
        - **Economia**: PIB municipal, PIB per capita, populacao (IBGE - **DADOS REAIS**)
        - **Saude**: Mortalidade infantil, cobertura vacinal, infraestrutura (DATASUS)
        - **Educacao**: IDEB, escolas, matriculas, aprovacao (INEP)
        - **Assistencia Social**: CadUnico, beneficios, taxa de pobreza (MDS)

        ### Funcionalidades de Analise
        - Consulta multissetorial por municipio
        - Analises de correlacao entre indicadores
        - Identificacao de municipios prioritarios
        - Comparativo entre mesorregioes
        - Indice de vulnerabilidade social

        ### Contexto
        Desenvolvido como prova de conceito para o **Projeto Pilares II** (Banco Mundial)
        do Governo do Estado do Piaui.
        """,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()

# Cache de dados
_data_loader: DataLoader = None


def get_data_generator():
    """Retorna instancia do gerador de dados."""
    return SyntheticDataGenerator()


def get_loader() -> DataLoader:
    """Retorna instancia do DataLoader."""
    global _data_loader
    if _data_loader is None:
        _data_loader = get_data_loader()
    return _data_loader


def load_cached_data(generator: SyntheticDataGenerator) -> dict:
    """Carrega dados em cache, priorizando dados reais."""
    loader = get_loader()
    return loader.load_all(generator)


# ========== ENDPOINTS RAIZ ==========

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz com informacoes da API."""
    return {
        "api": "Sistema Integrado de Dados do Piaui - Prototipo BDG",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "online",
        "setores": ["economia", "saude", "educacao", "assistencia_social"],
        "municipios": 224,
        "projeto": "Pilares II - Banco Mundial"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Verifica status da API."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version="2.0.0"
    )


# ========== ENDPOINTS METADADOS ==========

@app.get("/fontes", response_model=List[FonteDados], tags=["Metadados"])
async def listar_fontes():
    """Lista todas as fontes de dados disponiveis."""
    return [FonteDados(**fonte) for fonte in FONTES_DADOS.values()]


@app.get("/fontes/status", tags=["Metadados"])
async def status_fontes(generator: SyntheticDataGenerator = Depends(get_data_generator)):
    """
    Status das fontes de dados carregadas.

    Indica quais datasets contem dados reais (IBGE) vs simulados.
    """
    load_cached_data(generator)
    loader = get_loader()

    return {
        "resumo": {
            "total_datasets": len(loader._sources),
            "datasets_reais": sum(1 for s in loader._sources.values() if s.is_real),
            "datasets_simulados": sum(1 for s in loader._sources.values() if not s.is_real)
        },
        "setores_integrados": {
            "economia": {"fonte": "IBGE SIDRA", "dados_reais": True},
            "saude": {"fonte": "DATASUS (simulado)", "dados_reais": False},
            "educacao": {"fonte": "INEP (simulado)", "dados_reais": False},
            "assistencia_social": {"fonte": "MDS (simulado)", "dados_reais": False}
        },
        "datasets": loader.get_data_sources()
    }


@app.get("/municipios", response_model=List[MunicipioInfo], tags=["Metadados"])
async def listar_municipios():
    """Lista os 224 municipios do Piaui."""
    return [
        MunicipioInfo(codigo_ibge=codigo, nome=nome)
        for codigo, nome in MUNICIPIOS_PIAUI.items()
    ]


# ========== ENDPOINTS SETORIAIS ==========

@app.get("/economia/pib", tags=["Economia"])
async def consultar_pib(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Consulta dados de PIB municipal.

    **DADOS REAIS DO IBGE**:
    - Fonte: IBGE - Sistema de Contas Regionais
    - Anos: 2020, 2021
    - 224 municipios do Piaui
    """
    load_cached_data(generator)
    loader = get_loader()

    df = loader.get_pib_data(municipio_id=municipio_id, ano=ano)
    is_real = loader.is_real_data("economia_pib")

    return {
        "dados_reais": is_real,
        "fonte": "IBGE - Sistema de Contas Regionais" if is_real else "Dados Simulados",
        "total_registros": len(df),
        "data": df.to_dict("records")
    }


@app.get("/saude/indicadores", tags=["Saude"])
async def consultar_saude(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Consulta indicadores de saude (DATASUS simulado).

    Indicadores disponiveis:
    - Mortalidade infantil (por mil nascidos vivos)
    - Cobertura vacinal (%)
    - Leitos SUS por 1000 habitantes
    - Estabelecimentos de saude
    """
    load_cached_data(generator)
    loader = get_loader()

    df = loader.get_saude_data(municipio_id=municipio_id, ano=ano)

    return {
        "dados_reais": False,
        "fonte": "DATASUS (simulado com base em estatisticas reais do PI)",
        "total_registros": len(df),
        "data": df.to_dict("records")
    }


@app.get("/educacao/indicadores", tags=["Educacao"])
async def consultar_educacao(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Consulta indicadores de educacao (INEP simulado).

    Indicadores disponiveis:
    - IDEB anos iniciais (1-5 ano)
    - IDEB anos finais (6-9 ano)
    - Taxa de aprovacao
    - Total de escolas
    - Total de matriculas
    """
    load_cached_data(generator)
    loader = get_loader()

    df = loader.get_educacao_data(municipio_id=municipio_id, ano=ano)

    return {
        "dados_reais": False,
        "fonte": "INEP (simulado com base em estatisticas reais do PI)",
        "total_registros": len(df),
        "data": df.to_dict("records")
    }


@app.get("/assistencia/indicadores", tags=["Assistencia Social"])
async def consultar_assistencia(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Consulta indicadores de assistencia social (MDS simulado).

    Indicadores disponiveis:
    - Familias no CadUnico
    - Beneficiarios de programas sociais
    - Taxa de pobreza estimada
    """
    load_cached_data(generator)
    loader = get_loader()

    df = loader.get_assistencia_data(municipio_id=municipio_id, ano=ano)

    return {
        "dados_reais": False,
        "fonte": "MDS (simulado com base em estatisticas reais do PI)",
        "total_registros": len(df),
        "data": df.to_dict("records")
    }


# ========== ENDPOINTS MULTISSETORIAIS ==========

@app.get("/municipios/{codigo_ibge}/completo", tags=["Analise Multissetorial"])
async def get_municipio_completo(
    codigo_ibge: int,
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Retorna TODOS os indicadores de um municipio.

    Integra dados de economia, saude, educacao e assistencia social
    em uma unica consulta.

    **Exemplo de uso**: Perfil completo de Teresina (2211001)
    """
    if codigo_ibge not in MUNICIPIOS_PIAUI:
        raise HTTPException(status_code=404, detail="Municipio nao encontrado")

    load_cached_data(generator)
    loader = get_loader()

    result = loader.get_municipio_completo(codigo_ibge)
    result["municipio_nome"] = MUNICIPIOS_PIAUI[codigo_ibge]

    return result


@app.get("/analise/correlacao", tags=["Analise Multissetorial"])
async def analise_correlacao(
    indicadores: Optional[str] = Query(
        None,
        description="Indicadores separados por virgula. Ex: pib_per_capita,ideb_anos_iniciais,mortalidade_infantil"
    ),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Analise de correlacao entre indicadores de diferentes setores.

    Calcula correlacao de Pearson entre indicadores, permitindo identificar
    relacoes entre desenvolvimento economico, saude e educacao.

    **Exemplo de insight**: Correlacao negativa entre PIB per capita e mortalidade infantil
    indica que municipios mais ricos tendem a ter menores taxas de mortalidade.
    """
    load_cached_data(generator)
    loader = get_loader()

    # Converter string para lista
    ind_list = None
    if indicadores:
        ind_list = [i.strip() for i in indicadores.split(",")]

    df_corr = loader.get_correlacao_indicadores(ind_list)

    if df_corr.empty:
        raise HTTPException(status_code=404, detail="Dados insuficientes para correlacao")

    # Gerar insights automaticos
    insights = []
    for col1 in df_corr.columns:
        for col2 in df_corr.columns:
            if col1 < col2:
                corr_val = df_corr.loc[col1, col2]
                if abs(corr_val) > 0.5:
                    direcao = "positiva" if corr_val > 0 else "negativa"
                    forca = "forte" if abs(corr_val) > 0.7 else "moderada"
                    insights.append(
                        f"Correlacao {forca} {direcao} ({corr_val:.2f}) entre {col1} e {col2}"
                    )

    return {
        "indicadores": list(df_corr.columns),
        "matriz_correlacao": df_corr.to_dict(),
        "insights": insights if insights else ["Nenhuma correlacao significativa encontrada (|r| > 0.5)"]
    }


@app.get("/analise/prioridade", tags=["Analise Multissetorial"])
async def municipios_prioritarios(
    criterio: str = Query(
        "vulnerabilidade",
        description="Criterio: vulnerabilidade, saude, educacao, economia"
    ),
    top_n: int = Query(20, ge=1, le=224, description="Numero de municipios"),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Identifica municipios prioritarios para investimento.

    Baseado em indicadores multissetoriais, rankeia municipios que
    mais necessitam de intervencao em politicas publicas.

    **Criterios disponiveis**:
    - `vulnerabilidade`: Indice combinado de saude + educacao + economia
    - `saude`: Alta mortalidade infantil + baixa cobertura vacinal
    - `educacao`: Baixo IDEB
    - `economia`: Alta taxa de pobreza

    **Caso de uso**: Planejamento de programas sociais prioritarios
    """
    load_cached_data(generator)
    loader = get_loader()

    df = loader.get_municipios_prioritarios(criterio=criterio, top_n=top_n)

    if df.empty:
        raise HTTPException(status_code=404, detail="Dados insuficientes")

    # Selecionar colunas relevantes
    colunas = ['municipio_id', 'municipio_nome', 'mesorregiao']

    if 'indice_vulnerabilidade' in df.columns:
        colunas.append('indice_vulnerabilidade')
    if 'classificacao_vulnerabilidade' in df.columns:
        colunas.append('classificacao_vulnerabilidade')
    if 'mortalidade_infantil' in df.columns:
        colunas.append('mortalidade_infantil')
    if 'ideb_anos_iniciais' in df.columns:
        colunas.append('ideb_anos_iniciais')
    if 'taxa_pobreza_estimada' in df.columns:
        colunas.append('taxa_pobreza_estimada')

    df_result = df[[c for c in colunas if c in df.columns]]

    return {
        "criterio": criterio,
        "total_municipios": len(df_result),
        "descricao": {
            "vulnerabilidade": "Indice multidimensional combinando saude, educacao e economia",
            "saude": "Prioriza alta mortalidade infantil e baixa cobertura vacinal",
            "educacao": "Prioriza baixo IDEB (anos iniciais)",
            "economia": "Prioriza alta taxa de pobreza"
        }.get(criterio, ""),
        "municipios": df_result.to_dict("records")
    }


@app.get("/analise/mesorregioes", tags=["Analise Multissetorial"])
async def comparativo_mesorregioes(
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Comparativo de indicadores por mesorregiao do Piaui.

    Calcula medias dos principais indicadores agrupados pelas
    4 mesorregioes do estado:
    - Norte Piauiense
    - Centro-Norte Piauiense (inclui Teresina)
    - Sudoeste Piauiense
    - Sudeste Piauiense (inclui Picos)

    **Caso de uso**: Identificar disparidades regionais
    """
    load_cached_data(generator)
    loader = get_loader()

    df = loader.get_comparativo_mesorregioes()

    if df.empty:
        raise HTTPException(status_code=404, detail="Dados insuficientes")

    return {
        "mesorregioes": list(df.index),
        "indicadores": list(df.columns),
        "dados": df.reset_index().to_dict("records")
    }


@app.get("/analise/integrado", tags=["Analise Multissetorial"])
async def dados_integrados(
    classificacao: Optional[str] = Query(
        None,
        description="Filtrar por classificacao: Baixa, Media, Alta, Muito Alta"
    ),
    mesorregiao: Optional[str] = Query(None, description="Filtrar por mesorregiao"),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    Dataset integrado com todos os indicadores (snapshot 2021).

    Retorna visao consolidada de todos os 224 municipios com
    indicadores de economia, saude, educacao e assistencia social
    ja integrados, incluindo indice de vulnerabilidade calculado.

    **Campos disponiveis**:
    - Identificacao: municipio_id, municipio_nome, mesorregiao
    - Saude: mortalidade_infantil, cobertura_vacinal, leitos, estabelecimentos
    - Educacao: ideb_anos_iniciais, ideb_anos_finais, taxa_aprovacao, escolas, matriculas
    - Assistencia: familias_cadunico, beneficiarios, taxa_pobreza_estimada
    - Calculado: indice_vulnerabilidade, classificacao_vulnerabilidade
    """
    load_cached_data(generator)
    loader = get_loader()

    df = loader.get_integrated_data()

    if df.empty:
        raise HTTPException(status_code=404, detail="Dados integrados nao disponiveis")

    # Aplicar filtros
    if classificacao:
        df = df[df['classificacao_vulnerabilidade'] == classificacao]
    if mesorregiao:
        df = df[df['mesorregiao'].str.contains(mesorregiao, case=False)]

    return {
        "total_municipios": len(df),
        "ano_referencia": 2021,
        "indicadores": list(df.columns),
        "data": df.to_dict("records")
    }


# ========== ENDPOINTS LEGADOS (COMPATIBILIDADE) ==========

@app.get("/saude/mortalidade", tags=["Saude (Legado)"])
async def consultar_mortalidade_legado(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    [LEGADO] Consulta dados de mortalidade (SIM/DATASUS).

    Mantido para compatibilidade. Use `/saude/indicadores` para novos projetos.
    """
    data = load_cached_data(generator)

    if "saude_mortalidade" not in data:
        return {"message": "Use /saude/indicadores para dados de saude"}

    df = data["saude_mortalidade"].copy()

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
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0
    )


@app.get("/educacao/ideb", tags=["Educacao (Legado)"])
async def consultar_ideb_legado(
    municipio_id: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    [LEGADO] Consulta dados do IDEB.

    Mantido para compatibilidade. Use `/educacao/indicadores` para novos projetos.
    """
    data = load_cached_data(generator)

    if "educacao_ideb" not in data:
        loader = get_loader()
        df = loader.get_educacao_data(municipio_id=municipio_id, ano=ano)
        return df.to_dict("records")

    df = data["educacao_ideb"].copy()

    if municipio_id:
        df = df[df["municipio_id"] == municipio_id]
    if ano:
        df = df[df["ano"] == ano]

    return df.to_dict("records")


@app.get("/indicadores/{municipio_id}", tags=["Indicadores (Legado)"])
async def indicadores_municipio_legado(
    municipio_id: int,
    ano: int = Query(2021),
    generator: SyntheticDataGenerator = Depends(get_data_generator)
):
    """
    [LEGADO] Retorna indicadores consolidados de um municipio.

    Mantido para compatibilidade. Use `/municipios/{codigo_ibge}/completo` para novos projetos.
    """
    return await get_municipio_completo(municipio_id, generator)


# ========== EXECUCAO ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
