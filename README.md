# Portfólio de Ciência de Dados

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-15+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.29+-red.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.100+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Portfólio completo de projetos de Ciência de Dados, demonstrando competências em ETL, visualização de dados, análise geoespacial, machine learning, APIs REST e compliance de dados.

---

## Projetos

### 1. Pipeline ETL - Dados Socioeconômicos IBGE

**Localização**: `projeto1-etl-ibge/`

Pipeline ETL robusto e escalável para extração, transformação e armazenamento de dados socioeconômicos do Brasil fornecidos pelo IBGE.

**Tecnologias**: Python, SQLAlchemy, PostgreSQL, Pydantic, Pytest

**Características**:
- Arquitetura modular com Star Schema
- Validação de dados com Pydantic
- Processamento em lotes otimizado
- Rate limiting e retry automático
- Logging estruturado
- Testes unitários e de integração

**Dados Coletados**:
- Localidades (Regiões, Estados, Municípios)
- População (Censos e Estimativas)
- PIB Municipal
- Indicadores Sociais

[Ver Documentação Completa](projeto1-etl-ibge/README.md)

---

### 2. Dashboard Ambiental - Desmatamento no Brasil

**Localização**: `projeto2-dashboard-ambiental/`

Dashboard interativo para análise de dados de desmatamento no Brasil, com foco no bioma Cerrado e no estado do Piauí, utilizando dados oficiais do PRODES/INPE.

**Tecnologias**: Streamlit, Plotly, Folium, Pandas, GeoPandas

**Características**:
- Visualizações interativas (gráficos e mapas)
- Análises temporais e comparativas
- KPIs dinâmicos em tempo real
- Filtros interativos (bioma, estado, período)
- Foco regional no Piauí
- Cache multinível para performance

**Fontes de Dados**:
- PRODES (Programa de Monitoramento do Desmatamento - INPE)
- TerraBrasilis (Plataforma de dados geográficos)

[Ver Documentação Completa](projeto2-dashboard-ambiental/README.md)

---

### 3. Modelo Preditivo - Safras Agrícolas

**Localização**: `projeto3-modelo-preditivo-safras/`

Sistema de Machine Learning para previsão de produção agrícola usando dados históricos da Pesquisa Agrícola Municipal (PAM) do IBGE.

**Tecnologias**: Scikit-learn, XGBoost, LightGBM, Pandas, Matplotlib

**Características**:
- Múltiplos algoritmos de ML (7+ modelos)
- Feature engineering especializado para agricultura
- Pipeline de validação cruzada temporal
- Visualizações de diagnóstico
- Análise de importância de features
- CLI para treino e predição

**Modelos Suportados**:
- Regressão Linear, Ridge, Lasso
- Random Forest
- Gradient Boosting
- XGBoost
- LightGBM

**Métricas**:
- RMSE, MAE, MAPE, R²

[Ver Documentação Completa](projeto3-modelo-preditivo-safras/README.md)

---

### 4. Sistema de Integração Multissetorial - Piauí

**Localização**: `projeto4-integracao-multissetorial/`

Plataforma de integração de dados governamentais de múltiplos setores do estado do Piauí, simulando cenário real de data lake governamental.

**Tecnologias**: FastAPI, SQLAlchemy, PostgreSQL, Prefect, Pydantic

**Características**:
- API REST completa com 10+ endpoints
- Dados sintéticos realistas de 4 setores
- Documentação automática (Swagger/ReDoc)
- Gerador de dados para demonstração
- Indicadores consolidados por município

**Setores Integrados**:
- **Saúde**: DATASUS (SIM, SINASC, SIH)
- **Educação**: INEP (Censo Escolar, IDEB)
- **Economia**: IBGE (PIB, CEMPRE)
- **Assistência Social**: MDS (CadÚnico, Bolsa Família)

**Endpoints Principais**:
| Endpoint | Descrição |
|----------|-----------|
| `/saude/mortalidade` | Dados de mortalidade |
| `/educacao/escolas` | Dados de escolas |
| `/economia/pib` | PIB municipal |
| `/indicadores/{municipio}` | Consolidado por município |

[Ver Documentação Completa](projeto4-integracao-multissetorial/README.md)

---

### 5. Sistema de Compliance LGPD - Auditoria de Dados

**Localização**: `projeto5-compliance-lgpd/`

Ferramenta automatizada para identificação, classificação e anonimização de dados pessoais (PII) em conformidade com a Lei Geral de Proteção de Dados.

**Tecnologias**: Pandas, Faker, Jinja2, hashlib, regex

**Características**:
- Scanner de PII com detecção por regex e nome de coluna
- Classificação por nível de risco (Crítico, Alto, Médio, Baixo)
- 7 métodos de anonimização
- Relatórios de auditoria HTML
- CLI completo para scan e anonimização

**Métodos de Anonimização**:
| Método | Descrição |
|--------|-----------|
| `mask` | Mascara caracteres preservando formato |
| `hash` | Hash SHA-256 irreversível |
| `pseudonymize` | Substitui por identificador artificial |
| `generalize` | Reduz precisão dos dados |
| `suppress` | Remove completamente |
| `tokenize` | Token reversível |
| `noise` | Adiciona variação aleatória |

**Tipos de PII Detectados**:
- CPF, CNPJ, RG, CNH
- Email, Telefone, Celular
- Cartão de Crédito, Conta Bancária
- CEP, Endereço
- Nome, Data de Nascimento

[Ver Documentação Completa](projeto5-compliance-lgpd/README.md)

---

## Tecnologias e Competências

### Stack Principal

| Categoria | Tecnologias |
|-----------|-------------|
| **Linguagem** | Python 3.11+ |
| **Data Science** | Pandas, NumPy, Scikit-learn |
| **Visualização** | Plotly, Streamlit, Folium, Matplotlib |
| **Machine Learning** | XGBoost, LightGBM, Scikit-learn |
| **Backend** | FastAPI, SQLAlchemy, Pydantic |
| **Banco de Dados** | PostgreSQL |
| **Testes** | Pytest |

### Habilidades Demonstradas

1. **ETL (Extract, Transform, Load)**
   - Design de pipelines de dados
   - Integração com APIs RESTful
   - Validação e qualidade de dados
   - Processamento em lotes

2. **Machine Learning**
   - Feature Engineering
   - Seleção e comparação de modelos
   - Validação cruzada temporal
   - Interpretabilidade de modelos

3. **Desenvolvimento de APIs**
   - REST APIs com FastAPI
   - Documentação automática
   - Validação com Pydantic
   - Testes automatizados

4. **Visualização de Dados**
   - Dashboards interativos
   - Mapas geoespaciais
   - Storytelling com dados

5. **Data Privacy**
   - Identificação de PII
   - Técnicas de anonimização
   - Compliance LGPD

---

## Estrutura do Portfólio

```
Portifolio-cienciadedados/
│
├── README.md                              # Este arquivo
│
├── projeto1-etl-ibge/                     # Pipeline ETL IBGE
│   ├── config/
│   ├── src/extractors/, transformers/, loaders/
│   ├── tests/
│   └── notebooks/
│
├── projeto2-dashboard-ambiental/          # Dashboard Ambiental
│   ├── app.py
│   ├── src/components/, utils/
│   └── data/
│
├── projeto3-modelo-preditivo-safras/      # ML Agrícola
│   ├── src/data/, features/, models/
│   ├── models/
│   └── notebooks/
│
├── projeto4-integracao-multissetorial/    # API Multissetorial
│   ├── src/api/, extractors/
│   ├── docker/
│   └── notebooks/
│
└── projeto5-compliance-lgpd/              # Compliance LGPD
    ├── src/scanners/, anonymizers/, reporters/
    ├── templates/
    └── notebooks/
```

---

## Como Explorar os Projetos

### Projeto 1: Pipeline ETL IBGE
```bash
cd projeto1-etl-ibge
pip install -r requirements.txt
python main.py extract localidades
```

### Projeto 2: Dashboard Ambiental
```bash
cd projeto2-dashboard-ambiental
pip install -r requirements.txt
streamlit run app.py
# Acesse: http://localhost:8501
```

### Projeto 3: Modelo Preditivo Safras
```bash
cd projeto3-modelo-preditivo-safras
pip install -r requirements.txt
python main.py train --cultura soja
```

### Projeto 4: Integração Multissetorial
```bash
cd projeto4-integracao-multissetorial
pip install -r requirements.txt
python main.py generate  # Gera dados sintéticos
python main.py api       # Inicia API
# Acesse: http://localhost:8000/docs
```

### Projeto 5: Compliance LGPD
```bash
cd projeto5-compliance-lgpd
pip install -r requirements.txt
python main.py generate-sample  # Gera dados de teste
python main.py scan data/input/sample_data.csv --report
```

---

## Status dos Projetos

| Projeto | Status | Testes | Docs | Notebook |
|---------|--------|--------|------|----------|
| 1. ETL IBGE | Completo | OK | OK | OK |
| 2. Dashboard Ambiental | Completo | OK | OK | OK |
| 3. Modelo Preditivo | Completo | OK | OK | OK |
| 4. Integração Multissetorial | Completo | OK | OK | OK |
| 5. Compliance LGPD | Completo | OK | OK | OK |

---

## Métricas do Portfólio

- **Total de Projetos**: 5
- **Linhas de Código**: ~15.000+
- **Tecnologias Utilizadas**: 30+
- **Notebooks Jupyter**: 5
- **Endpoints de API**: 20+
- **Testes Automatizados**: 100+

---

## Fontes de Dados

| Projeto | Fonte | URL |
|---------|-------|-----|
| 1 | IBGE - API de Serviços | servicodados.ibge.gov.br |
| 2 | INPE - TerraBrasilis | terrabrasilis.dpi.inpe.br |
| 3 | IBGE - SIDRA (PAM) | sidra.ibge.gov.br |
| 4 | DATASUS, INEP, IBGE, MDS | Dados sintéticos baseados em fontes oficiais |
| 5 | N/A | Dados sintéticos (Faker) |

---

## Licença

Todos os projetos estão licenciados sob a Licença MIT.

---

## Autor

**Maxwell** - Projeto de Portfólio em Data Science

---

**Última Atualização**: 14 de Dezembro de 2025

---

**Desenvolvido com Python e dedicação**
