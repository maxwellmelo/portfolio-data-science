# Sistema Integrado de Dados do Piaui - Prototipo BDG

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg?style=flat&logo=fastapi&logoColor=white)
![IBGE](https://img.shields.io/badge/Dados-IBGE_Real-009c3b.svg?style=flat)
![Status](https://img.shields.io/badge/Status-Completo-success.svg?style=flat)

**Prototipo de Banco de Dados Geografico Multissetorial (BDG) para apoio a gestao de politicas publicas do Piaui**

[Demo Online](https://maxwellmelo.github.io/portfolio-data-science/projetos/projeto4-integracao-multissetorial.html) | [Notebook Colab](#notebook-demonstrativo) | [API Docs](#endpoints-da-api)

</div>

---

## Visao Geral

Sistema integrado de dados governamentais que unifica informacoes de **economia, saude, educacao e assistencia social** dos 224 municipios do Piaui. Desenvolvido como prova de conceito para demonstrar capacidade de construcao de sistemas de integracao de dados multissetoriais.

### Contexto do Projeto

| Aspecto | Descricao |
|---------|-----------|
| **Alinhamento** | Projeto Pilares II (Banco Mundial) |
| **Objetivo** | Apoiar gestao de politicas publicas baseadas em dados |
| **Cobertura** | 224 municipios do Piaui |
| **Setores** | Economia + Saude + Educacao + Assistencia Social |

---

## Objetivo de Negocio

Apoiar gestores publicos na **tomada de decisao baseada em evidencias**, permitindo:

- **Identificacao de municipios vulneraveis** que necessitam investimento prioritario
- **Analise de correlacoes** entre desenvolvimento economico, saude e educacao
- **Monitoramento de politicas publicas** atraves de indicadores integrados
- **Alocacao eficiente de recursos** estaduais e federais
- **Planejamento setorial** com visao multidimensional

---

## Setores Integrados

### 1. Economia (IBGE - DADOS REAIS)

| Indicador | Fonte | Anos |
|-----------|-------|------|
| PIB Municipal | IBGE SIDRA | 2020-2021 |
| PIB per capita | IBGE SIDRA | 2020-2021 |
| Populacao | IBGE SIDRA | 2019-2024 |

### 2. Saude (DATASUS - Simulado)

| Indicador | Descricao |
|-----------|-----------|
| Mortalidade Infantil | Por mil nascidos vivos |
| Cobertura Vacinal | Percentual da populacao |
| Leitos SUS | Por 1000 habitantes |
| Estabelecimentos | Total por municipio |

### 3. Educacao (INEP - Simulado)

| Indicador | Descricao |
|-----------|-----------|
| IDEB Anos Iniciais | 1o ao 5o ano |
| IDEB Anos Finais | 6o ao 9o ano |
| Taxa de Aprovacao | Percentual |
| Escolas | Total por municipio |
| Matriculas | Total por municipio |

### 4. Assistencia Social (MDS - Simulado)

| Indicador | Descricao |
|-----------|-----------|
| Familias CadUnico | Total cadastradas |
| Beneficiarios | Programas sociais |
| Taxa de Pobreza | Estimativa percentual |

---

## Funcionalidades

### API REST (FastAPI)

**20+ endpoints** para consulta e analise de dados:

#### Endpoints Setoriais
- `GET /economia/pib` - PIB municipal (dados reais IBGE)
- `GET /saude/indicadores` - Indicadores de saude
- `GET /educacao/indicadores` - Indicadores de educacao
- `GET /assistencia/indicadores` - Indicadores de assistencia social

#### Endpoints de Analise Multissetorial
- `GET /municipios/{codigo_ibge}/completo` - Perfil completo do municipio
- `GET /analise/correlacao` - Correlacao entre indicadores
- `GET /analise/prioridade` - Municipios prioritarios
- `GET /analise/mesorregioes` - Comparativo regional
- `GET /analise/integrado` - Dataset consolidado

### Analises Automaticas

| Analise | Descricao |
|---------|-----------|
| **Correlacao** | Relacoes entre PIB, IDEB, mortalidade |
| **Vulnerabilidade** | Indice multidimensional calculado |
| **Prioridade** | Ranking de municipios para investimento |
| **Clusters** | Agrupamento por perfil similar |

---

## Casos de Uso Reais

### Caso 1: Planejamento de Programas Sociais

**Pergunta**: "Quais municipios tem baixo desenvolvimento economico E alta mortalidade infantil E baixo IDEB?"

**Uso da API**:
```bash
GET /analise/prioridade?criterio=vulnerabilidade&top_n=20
```

**Resultado**: Lista de 20 municipios prioritarios para programas integrados de combate a pobreza.

### Caso 2: Avaliacao de Impacto Regional

**Pergunta**: "Quais mesorregioes apresentam maiores disparidades em indicadores de saude e educacao?"

**Uso da API**:
```bash
GET /analise/mesorregioes
```

**Resultado**: Comparativo mostrando que Sudoeste Piauiense tem indicadores significativamente inferiores ao Centro-Norte.

### Caso 3: Perfil Municipal para Investimento

**Pergunta**: "Qual o perfil completo de Teresina para planejamento orcamentario?"

**Uso da API**:
```bash
GET /municipios/2211001/completo
```

**Resultado**: Indicadores de todos os setores consolidados em uma unica resposta.

---

## Tecnologias Utilizadas

| Categoria | Tecnologia | Versao |
|-----------|------------|--------|
| Linguagem | Python | 3.11+ |
| Framework API | FastAPI | 0.104+ |
| Dados | Pandas, NumPy | 2.1+ |
| Validacao | Pydantic | 2.5+ |
| Database | SQLAlchemy | 2.0+ |
| HTTP | Requests, HTTPX | - |
| Logging | Loguru | 0.7+ |
| Testes | Pytest | 7.4+ |

---

## Estrutura do Projeto

```
projeto4-integracao-multissetorial/
├── src/
│   ├── api/
│   │   ├── main.py              # API FastAPI (20+ endpoints)
│   │   └── data_loader.py       # Carregador de dados integrado
│   │
│   └── extractors/
│       ├── ibge_extractor.py    # ETL dados reais IBGE
│       ├── multissetorial_extractor.py  # ETL Saude/Educacao/Assist
│       └── synthetic_generator.py       # Gerador de dados demo
│
├── data/
│   ├── real/                    # Dados reais IBGE (PIB, Populacao)
│   └── multissetorial/          # Dados integrados por setor
│       ├── indicadores_saude.csv
│       ├── indicadores_educacao.csv
│       ├── indicadores_assistencia.csv
│       └── dados_integrados.csv
│
├── config/
│   └── settings.py              # Configuracoes e lista de municipios
│
├── notebooks/
│   └── demo_dados_piaui.ipynb   # Demonstracao com visualizacoes
│
├── tests/
│   ├── test_extractors.py
│   └── test_api.py
│
├── main.py                      # CLI de entrada
├── requirements.txt
└── README.md
```

---

## Como Executar

### Pre-requisitos

- Python 3.11+
- pip

### Instalacao

```bash
# Clone o repositorio
git clone https://github.com/maxwellmelo/portfolio-data-science.git
cd portfolio-data-science/projeto4-integracao-multissetorial

# Crie ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instale dependencias
pip install -r requirements.txt
```

### Executar API

```bash
python main.py api
```

Acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Gerar Dados

```bash
# Gerar dados sinteticos
python main.py generate

# Executar pipeline completo
python main.py pipeline
```

---

## Endpoints da API

### Metadados

| Endpoint | Descricao |
|----------|-----------|
| `GET /` | Informacoes da API |
| `GET /health` | Status de saude |
| `GET /fontes` | Fontes de dados disponiveis |
| `GET /fontes/status` | Status real vs simulado |
| `GET /municipios` | Lista 224 municipios |

### Setoriais

| Endpoint | Dados | Status |
|----------|-------|--------|
| `GET /economia/pib` | PIB, populacao | **REAL (IBGE)** |
| `GET /saude/indicadores` | Mortalidade, vacinacao | Simulado |
| `GET /educacao/indicadores` | IDEB, escolas | Simulado |
| `GET /assistencia/indicadores` | CadUnico, pobreza | Simulado |

### Analise Multissetorial

| Endpoint | Descricao |
|----------|-----------|
| `GET /municipios/{id}/completo` | Todos indicadores de um municipio |
| `GET /analise/correlacao` | Matriz de correlacao entre setores |
| `GET /analise/prioridade` | Municipios prioritarios por criterio |
| `GET /analise/mesorregioes` | Comparativo entre 4 mesorregioes |
| `GET /analise/integrado` | Dataset consolidado 224 municipios |

---

## Notebook Demonstrativo

O notebook demonstra visualmente as analises multissetoriais:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maxwellmelo/portfolio-data-science/blob/main/projeto4-integracao-multissetorial/notebooks/demo_dados_piaui.ipynb)

### Conteudo

| Secao | Descricao |
|-------|-----------|
| 1 | Carregamento de dados multissetoriais |
| 2 | Analise de correlacao PIB x IDEB |
| 3 | Mapa de vulnerabilidade municipal |
| 4 | Comparativo de mesorregioes |
| 5 | Identificacao de municipios prioritarios |
| 6 | Insights e recomendacoes |

---

## Dados

### Fontes Oficiais

| Setor | Fonte | Tipo | URL |
|-------|-------|------|-----|
| Economia | IBGE SIDRA | **Real** | sidra.ibge.gov.br |
| Saude | DATASUS | Simulado* | datasus.saude.gov.br |
| Educacao | INEP | Simulado* | gov.br/inep |
| Assistencia | MDS | Simulado* | mds.gov.br |

*Dados simulados com base em estatisticas reais do Piaui para demonstracao.

### Estatisticas dos Dados

| Dataset | Registros | Municipios | Anos |
|---------|-----------|------------|------|
| economia_pib | 448 | 224 | 2020-2021 |
| populacao | 896 | 224 | 2019-2024 |
| indicadores_saude | 1120 | 224 | 2019-2023 |
| indicadores_educacao | 896 | 224 | 2017-2023 |
| indicadores_assistencia | 1120 | 224 | 2019-2023 |
| dados_integrados | 224 | 224 | 2021 |

---

## Diferenciais Tecnicos

- [x] Integracao real de **4 setores governamentais**
- [x] Dados oficiais do **IBGE** (economia)
- [x] API REST documentada (**Swagger/OpenAPI**)
- [x] Analises cruzadas automaticas
- [x] Indice de vulnerabilidade calculado
- [x] **20+ endpoints** para consulta
- [x] Testes automatizados (Pytest)
- [x] Logging estruturado

---

## Relacao com Projeto Pilares II

Este sistema foi desenvolvido considerando as necessidades do **Projeto Pilares II** (Banco Mundial) para o Governo do Piaui:

| Requisito TdR | Implementacao |
|---------------|---------------|
| Integracao de dados multissetoriais | 4 setores integrados |
| Apoio ao planejamento setorial | Endpoints de analise |
| Gestao de politicas publicas | Identificacao de prioridades |
| Banco de Dados Geografico | Prototipo BDG com 224 municipios |

---

## Melhorias Futuras

- [ ] Integracao real com API DATASUS (pysus)
- [ ] Integracao real com dados INEP
- [ ] Mapa coropletico interativo (GeoJSON)
- [ ] Dashboard Streamlit/Dash
- [ ] Cache Redis para alta performance
- [ ] Autenticacao JWT
- [ ] Deploy em container Docker

---

## Licenca

MIT License - veja [LICENSE](../LICENSE)

---

## Autor

**Maxwell Melo** - Especialista em Dados

Portfolio: [maxwellmelo.github.io/portfolio-data-science](https://maxwellmelo.github.io/portfolio-data-science/)

---

<div align="center">

**Sistema desenvolvido para demonstrar capacidade de construcao de plataformas de integracao de dados governamentais multissetoriais.**

*Dados reais IBGE + Simulacoes calibradas | API REST com 20+ endpoints | Foco em gestao publica*

</div>
