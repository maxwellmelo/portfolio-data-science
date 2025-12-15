# Portfolio de Ciencia de Dados

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat&logo=python&logoColor=white)
![IBGE](https://img.shields.io/badge/Dados-IBGE_Real-009c3b.svg?style=flat)
![Plotly](https://img.shields.io/badge/Plotly-Interativo-3F4F75.svg?style=flat&logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat&logo=fastapi&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3+-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

### Portfolio completo de Ciencia de Dados com 5 projetos end-to-end

**ETL | Machine Learning | Dashboards | APIs REST | Data Privacy**

[Notebooks Demo](#notebooks-demonstrativos) | [Projetos](#projetos) | [Tecnologias](#tecnologias-e-competencias)

</div>

---

## Destaques do Portfolio

<table>
<tr>
<td align="center" width="20%">

**5 Projetos**

Completos end-to-end

</td>
<td align="center" width="20%">

**R2 = 0.90**

Modelo ML Safras

</td>
<td align="center" width="20%">

**224 Municipios**

Dados IBGE Piaui

</td>
<td align="center" width="20%">

**7 Metodos**

Anonimizacao LGPD

</td>
<td align="center" width="20%">

**6 Biomas**

Desmatamento Brasil

</td>
</tr>
</table>

---

## Notebooks Demonstrativos

Cada projeto possui um notebook interativo com visualizacoes Plotly. **Clique em "Ver no nbviewer"** para visualizar os graficos:

| # | Projeto | Notebook | Visualizar |
|:-:|---------|----------|:----------:|
| 1 | ETL IBGE | `demo_etl_ibge.ipynb` | [![nbviewer](https://img.shields.io/badge/ver-nbviewer-orange)](https://nbviewer.org/github/maxwellmelo/portfolio-data-science/blob/main/projeto1-etl-ibge/notebooks/demo_etl_ibge.ipynb) |
| 2 | Dashboard Ambiental | `demo_desmatamento.ipynb` | [![nbviewer](https://img.shields.io/badge/ver-nbviewer-orange)](https://nbviewer.org/github/maxwellmelo/portfolio-data-science/blob/main/projeto2-dashboard-ambiental/notebooks/demo_desmatamento.ipynb) |
| 3 | Modelo Preditivo | `demo_modelo_safras.ipynb` | [![nbviewer](https://img.shields.io/badge/ver-nbviewer-orange)](https://nbviewer.org/github/maxwellmelo/portfolio-data-science/blob/main/projeto3-modelo-preditivo-safras/notebooks/demo_modelo_safras.ipynb) |
| 4 | Integracao Multissetorial | `demo_dados_piaui.ipynb` | [![nbviewer](https://img.shields.io/badge/ver-nbviewer-orange)](https://nbviewer.org/github/maxwellmelo/portfolio-data-science/blob/main/projeto4-integracao-multissetorial/notebooks/demo_dados_piaui.ipynb) |
| 5 | Compliance LGPD | `demo_compliance_lgpd.ipynb` | [![nbviewer](https://img.shields.io/badge/ver-nbviewer-orange)](https://nbviewer.org/github/maxwellmelo/portfolio-data-science/blob/main/projeto5-compliance-lgpd/notebooks/demo_compliance_lgpd.ipynb) |

> Graficos interativos Plotly - use os links acima para visualizar corretamente.

---

## Sobre

Portfolio demonstrando competencias em todo o ciclo de vida de projetos de dados: desde a extracao e transformacao (ETL), passando por analise exploratoria e modelagem preditiva, ate a disponibilizacao via APIs e dashboards interativos.

**Diferenciais:**
- 5 projetos completos com **dados publicos brasileiros**
- **Dados reais do IBGE** integrados via API SIDRA
- Notebooks com **visualizacoes interativas** (Plotly)
- Boas praticas: testes, logging, documentacao
- Foco em **problemas reais de negocio**

---

## Projetos

### 1. Pipeline ETL - Dados Socioeconomicos IBGE

<img src="https://img.shields.io/badge/Status-Completo-success" /> <img src="https://img.shields.io/badge/Dados-5.570_Municipios-blue" />

**Localizacao**: [`projeto1-etl-ibge/`](projeto1-etl-ibge/)

Pipeline ETL robusto e escalavel para extracao, transformacao e armazenamento de dados socioeconomicos do Brasil fornecidos pelo IBGE.

| Caracteristica | Descricao |
|----------------|-----------|
| **Tecnologias** | Python, SQLAlchemy, PostgreSQL, Pydantic, Pytest |
| **Dados** | Localidades, Populacao, PIB Municipal |
| **Notebook** | [demo_etl_ibge.ipynb](projeto1-etl-ibge/notebooks/demo_etl_ibge.ipynb) |

```
DADOS EXTRAIDOS
   Regioes: 5 registros
   Estados: 27 registros
   Municipios: 5.570 registros
```

[Ver Documentacao Completa](projeto1-etl-ibge/README.md)

---

### 2. Dashboard Ambiental - Desmatamento no Brasil

<img src="https://img.shields.io/badge/Status-Completo-success" /> <img src="https://img.shields.io/badge/Periodo-2000--2025-blue" />

**Localizacao**: [`projeto2-dashboard-ambiental/`](projeto2-dashboard-ambiental/)

Dashboard interativo para analise de dados de desmatamento no Brasil, com foco no bioma Cerrado e no estado do Piaui, utilizando dados oficiais do PRODES/INPE.

| Caracteristica | Descricao |
|----------------|-----------|
| **Tecnologias** | Streamlit, Plotly, Folium, Pandas, GeoPandas |
| **Dados** | PRODES/INPE, TerraBrasilis |
| **Notebook** | [demo_desmatamento.ipynb](projeto2-dashboard-ambiental/notebooks/demo_desmatamento.ipynb) |

```
VISAO GERAL (2015-2025)
   Biomas cobertos: 6
   Estados monitorados: 27
   Reducao Cerrado 2025: -11.49%
```

[Ver Documentacao Completa](projeto2-dashboard-ambiental/README.md)

---

### 3. Modelo Preditivo - Safras Agricolas

<img src="https://img.shields.io/badge/Status-Completo-success" /> <img src="https://img.shields.io/badge/R2-0.90-blue" />

**Localizacao**: [`projeto3-modelo-preditivo-safras/`](projeto3-modelo-preditivo-safras/)

Sistema de Machine Learning para previsao de producao agricola usando dados historicos da Pesquisa Agricola Municipal (PAM) do IBGE.

| Caracteristica | Descricao |
|----------------|-----------|
| **Tecnologias** | Scikit-learn, XGBoost, LightGBM, Pandas |
| **Modelos** | Linear, Ridge, Random Forest, Gradient Boosting |
| **Notebook** | [demo_modelo_safras.ipynb](projeto3-modelo-preditivo-safras/notebooks/demo_modelo_safras.ipynb) |

```
MELHOR MODELO: Gradient Boosting
   R2: 0.90 (90% variancia explicada)
   RMSE: 704.86 kg/ha
   MAPE: 11.11%
```

[Ver Documentacao Completa](projeto3-modelo-preditivo-safras/README.md)

---

### 4. Sistema de Integracao Multissetorial - Piaui

<img src="https://img.shields.io/badge/Status-Completo-success" /> <img src="https://img.shields.io/badge/Dados-IBGE_Real-009c3b" />

**Localizacao**: [`projeto4-integracao-multissetorial/`](projeto4-integracao-multissetorial/)

Plataforma de integracao de dados governamentais de multiplos setores do estado do Piaui, com dados reais do IBGE integrados via API SIDRA.

| Caracteristica | Descricao |
|----------------|-----------|
| **Tecnologias** | FastAPI, SQLAlchemy, PostgreSQL, Pydantic |
| **Dados** | IBGE Real (PIB, Populacao), Sinteticos (Saude, Educacao) |
| **Notebook** | [demo_dados_piaui.ipynb](projeto4-integracao-multissetorial/notebooks/demo_dados_piaui.ipynb) |

```
DADOS REAIS INTEGRADOS
   Municipios: 224 (Piaui)
   PIB: 448 registros (2019-2021)
   Populacao: 896 registros (2020-2023)
```

**Endpoints Principais**:
| Endpoint | Descricao |
|----------|-----------|
| `/economia/pib` | PIB municipal real |
| `/economia/populacao` | Populacao estimada real |
| `/saude/mortalidade` | Dados de mortalidade (sintetico) |
| `/indicadores/{municipio}` | Consolidado por municipio |

[Ver Documentacao Completa](projeto4-integracao-multissetorial/README.md)

---

### 5. Sistema de Compliance LGPD - Auditoria de Dados

<img src="https://img.shields.io/badge/Status-Completo-success" /> <img src="https://img.shields.io/badge/LGPD-Compliance-blueviolet" />

**Localizacao**: [`projeto5-compliance-lgpd/`](projeto5-compliance-lgpd/)

Ferramenta automatizada para identificacao, classificacao e anonimizacao de dados pessoais (PII) em conformidade com a Lei Geral de Protecao de Dados.

| Caracteristica | Descricao |
|----------------|-----------|
| **Tecnologias** | Pandas, Faker, Jinja2, hashlib, regex |
| **Funcoes** | Scan PII, Anonimizacao, Relatorios |
| **Notebook** | [demo_compliance_lgpd.ipynb](projeto5-compliance-lgpd/notebooks/demo_compliance_lgpd.ipynb) |

```
METODOS DE ANONIMIZACAO: 7
   mask, hash, pseudonymize, generalize
   suppress, tokenize, noise

TIPOS DE PII DETECTADOS: 15+
   CPF, CNPJ, Email, Telefone, etc.
```

[Ver Documentacao Completa](projeto5-compliance-lgpd/README.md)

---

## Tecnologias e Competencias

### Stack Principal

| Categoria | Tecnologias |
|-----------|-------------|
| **Linguagem** | Python 3.11+ |
| **Data Science** | Pandas, NumPy, Scikit-learn |
| **Visualizacao** | Plotly, Streamlit, Folium, Matplotlib |
| **Machine Learning** | XGBoost, LightGBM, Scikit-learn |
| **Backend** | FastAPI, SQLAlchemy, Pydantic |
| **Banco de Dados** | PostgreSQL |
| **Testes** | Pytest |

### Habilidades Demonstradas

| Habilidade | Projetos |
|------------|----------|
| **ETL & Data Engineering** | 1, 4 |
| **Machine Learning** | 3 |
| **APIs REST** | 4 |
| **Dashboards** | 2 |
| **Data Privacy** | 5 |
| **Visualizacao de Dados** | 1, 2, 3, 4, 5 |

---

## Estrutura do Portfolio

```
Portifolio-cienciadedados/
│
├── README.md                              # Este arquivo
│
├── projeto1-etl-ibge/                     # Pipeline ETL IBGE
│   ├── src/extractors/, transformers/, loaders/
│   ├── notebooks/demo_etl_ibge.ipynb
│   └── tests/
│
├── projeto2-dashboard-ambiental/          # Dashboard Ambiental
│   ├── app.py
│   ├── notebooks/demo_desmatamento.ipynb
│   └── src/components/, utils/
│
├── projeto3-modelo-preditivo-safras/      # ML Agricola
│   ├── src/data/, features/, models/
│   ├── notebooks/demo_modelo_safras.ipynb
│   └── tests/
│
├── projeto4-integracao-multissetorial/    # API Multissetorial
│   ├── src/api/, extractors/
│   ├── notebooks/demo_dados_piaui.ipynb
│   └── data/real/  (dados IBGE)
│
└── projeto5-compliance-lgpd/              # Compliance LGPD
    ├── src/scanners/, anonymizers/, reporters/
    ├── notebooks/demo_compliance_lgpd.ipynb
    └── tests/
```

---

## Como Explorar os Projetos

### Opcao 1: Notebooks (Recomendado)

Navegue para o notebook de cada projeto para ver demonstracoes visuais:

```bash
# Instalar Jupyter
pip install jupyter plotly pandas

# Abrir notebooks
jupyter notebook
```

### Opcao 2: Executar Projetos

```bash
# Projeto 1: ETL IBGE
cd projeto1-etl-ibge && pip install -r requirements.txt
python main.py --extract all --output csv

# Projeto 2: Dashboard Ambiental
cd projeto2-dashboard-ambiental && pip install -r requirements.txt
streamlit run app.py

# Projeto 3: Modelo Preditivo
cd projeto3-modelo-preditivo-safras && pip install -r requirements.txt
python main.py --train

# Projeto 4: API Multissetorial
cd projeto4-integracao-multissetorial && pip install -r requirements.txt
python main.py api  # Acesse http://localhost:8000/docs

# Projeto 5: Compliance LGPD
cd projeto5-compliance-lgpd && pip install -r requirements.txt
python main.py scan data/input/sample_data.csv --report
```

---

## Status dos Projetos

| # | Projeto | Status | Notebook | Dados | Testes |
|:-:|---------|:------:|:--------:|:-----:|:------:|
| 1 | ETL IBGE | Completo | [Demo](projeto1-etl-ibge/notebooks/demo_etl_ibge.ipynb) | API IBGE | Pytest |
| 2 | Dashboard Ambiental | Completo | [Demo](projeto2-dashboard-ambiental/notebooks/demo_desmatamento.ipynb) | PRODES | - |
| 3 | Modelo Preditivo | Completo | [Demo](projeto3-modelo-preditivo-safras/notebooks/demo_modelo_safras.ipynb) | PAM/IBGE | Pytest |
| 4 | Integracao Multissetorial | Completo | [Demo](projeto4-integracao-multissetorial/notebooks/demo_dados_piaui.ipynb) | IBGE Real | Pytest |
| 5 | Compliance LGPD | Completo | [Demo](projeto5-compliance-lgpd/notebooks/demo_compliance_lgpd.ipynb) | Sintetico | Pytest |

---

## Metricas do Portfolio

<table>
<tr>
<td align="center">

**5**

Projetos Completos

</td>
<td align="center">

**5**

Notebooks Interativos

</td>
<td align="center">

**30+**

Tecnologias

</td>
<td align="center">

**100+**

Testes Automatizados

</td>
</tr>
</table>

---

## Fontes de Dados

| Projeto | Fonte | Tipo | URL |
|---------|-------|------|-----|
| 1 | IBGE - API de Servicos | Real | servicodados.ibge.gov.br |
| 2 | INPE - TerraBrasilis | Real | terrabrasilis.dpi.inpe.br |
| 3 | IBGE - SIDRA (PAM) | Real | sidra.ibge.gov.br |
| 4 | IBGE - SIDRA | Real + Sintetico | sidra.ibge.gov.br |
| 5 | Faker | Sintetico | - |

---

## Licenca

Todos os projetos estao licenciados sob a Licenca MIT.

---

## Autor

**Maxwell** - Especialista em Dados

Portfolio desenvolvido para demonstrar competencias em Data Science, Machine Learning e Engenharia de Dados.

---

<div align="center">

**Ultima Atualizacao**: Dezembro 2025

*Desenvolvido com Python, boas praticas de engenharia de software e foco em resultados de negocio.*

</div>
