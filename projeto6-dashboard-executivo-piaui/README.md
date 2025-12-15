# Dashboard Executivo - Indicadores Socioeconomicos do Piaui

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat&logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Plotly_Dash-2.14+-3F4F75.svg?style=flat&logo=plotly&logoColor=white)
![IBGE](https://img.shields.io/badge/Dados-IBGE_Real-009c3b.svg?style=flat)
![Status](https://img.shields.io/badge/Status-Completo-success.svg?style=flat)

**Dashboard interativo para analise multissetorial de dados governamentais do Piaui**

[Ver Demo Online](https://maxwellmelo.github.io/portfolio-data-science/projetos/projeto6-dashboard-executivo.html) | [Notebook Colab](#notebook-demonstrativo) | [Como Executar](#como-executar)

</div>

---

## Visao Geral

Dashboard executivo desenvolvido para apoiar **tomada de decisao em politicas publicas** no Estado do Piaui. A ferramenta integra dados oficiais do IBGE e fornece visualizacoes interativas dos principais indicadores socioeconomicos dos 224 municipios piauienses.

### Contexto do Piaui

| Indicador | Valor | Observacao |
|-----------|-------|------------|
| Populacao | ~3.3 milhoes | 21o estado mais populoso |
| PIB | R$ 64 bilhoes | 2o menor PIB per capita do Brasil |
| Municipios | 224 | 73% com menos de 10 mil habitantes |
| Desafio | Disparidades regionais | Teresina concentra ~37% do PIB |

---

## Objetivo de Negocio

Fornecer aos **gestores publicos** uma visao consolidada e interativa de indicadores economicos e sociais, facilitando:

- **Identificacao de municipios prioritarios** para investimento
- **Analise de disparidades regionais** entre mesorregioes
- **Acompanhamento da evolucao** temporal de indicadores
- **Suporte a alocacao** de recursos estaduais
- **Monitoramento de politicas** do Projeto Pilares II (Banco Mundial)

---

## Funcionalidades

### Pagina 1: Visao Geral do Estado

- KPIs principais (Populacao, PIB, PIB per capita, Municipios)
- Top 10 municipios por PIB (grafico de barras)
- Distribuicao populacional por mesorregiao (grafico de pizza)
- Evolucao do PIB estadual (linha temporal)

### Pagina 2: Analise Multissetorial

- Scatter plot: PIB x Populacao (escala logaritmica)
- Matriz de correlacao entre indicadores
- Comparativo entre mesorregioes
- Tabela dinamica dos 224 municipios

### Pagina 3: Foco Municipal

- Selecao de municipio especifico
- Cards com perfil completo
- Comparacao com media estadual
- Ranking na mesorregiao

### Recursos Interativos

- [x] Filtros por mesorregiao
- [x] Filtro de faixa populacional (slider)
- [x] Exportacao de dados (CSV)
- [x] Cross-filtering entre visualizacoes
- [x] Design responsivo
- [x] Navegacao multi-pagina

---

## Tecnologias Utilizadas

| Categoria | Tecnologia | Versao |
|-----------|------------|--------|
| Linguagem | Python | 3.11+ |
| Framework | Plotly Dash | 2.14+ |
| UI | Dash Bootstrap Components | 1.5+ |
| Visualizacao | Plotly | 5.18+ |
| Dados | Pandas | 2.1+ |
| API | IBGE SIDRA | - |
| Deploy | Gunicorn | 21.2+ |

---

## Estrutura do Projeto

```
projeto6-dashboard-executivo-piaui/
├── app.py                    # Aplicacao Dash principal
├── requirements.txt          # Dependencias
├── README.md                 # Documentacao
├── data/
│   ├── __init__.py
│   └── load_data.py          # ETL - Carga de dados IBGE
├── components/
│   ├── __init__.py
│   └── charts.py             # Funcoes de visualizacao
├── notebooks/
│   └── demo_dashboard.ipynb  # Notebook demonstrativo
└── assets/                   # Arquivos estaticos (CSS, imagens)
```

---

## Como Executar

### Pre-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes)

### Instalacao

```bash
# Clone o repositorio
git clone https://github.com/maxwellmelo/portfolio-data-science.git

# Acesse o projeto
cd portfolio-data-science/projeto6-dashboard-executivo-piaui

# Crie ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instale dependencias
pip install -r requirements.txt
```

### Executar Localmente

```bash
python app.py
```

Acesse: **http://localhost:8050**

### Deploy (Render.com)

1. Conecte o repositorio no Render
2. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:server`
3. Deploy automatico

---

## Notebook Demonstrativo

O notebook [`notebooks/demo_dashboard.ipynb`](notebooks/demo_dashboard.ipynb) demonstra as visualizacoes do dashboard:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maxwellmelo/portfolio-data-science/blob/main/projeto6-dashboard-executivo-piaui/notebooks/demo_dashboard.ipynb)

### Conteudo do Notebook

| Secao | Descricao |
|-------|-----------|
| 1 | Carregamento de dados IBGE |
| 2 | KPIs principais |
| 3 | Top municipios por PIB |
| 4 | Distribuicao por mesorregiao |
| 5 | Analise PIB x Populacao |
| 6 | Comparativo regional |
| 7 | Tabela de municipios |
| 8 | Insights e conclusoes |

---

## Dados

### Fonte

Todos os dados sao **oficiais e publicos**:

- **Fonte**: IBGE (Instituto Brasileiro de Geografia e Estatistica)
- **API**: SIDRA (Sistema IBGE de Recuperacao Automatica)
- **Cobertura**: 224 municipios do Piaui
- **Periodo**: 2020-2024

### Tabelas SIDRA Utilizadas

| Tabela | Descricao | Variaveis |
|--------|-----------|-----------|
| 6579 | Populacao estimada | Populacao total |
| 5938 | PIB dos Municipios | PIB total, PIB per capita |

### Mesorregioes do Piaui

1. **Norte Piauiense** - Litoral e Parnaiba
2. **Centro-Norte Piauiense** - Capital Teresina
3. **Sudoeste Piauiense** - Cerrado, agronegocio
4. **Sudeste Piauiense** - Regiao de Picos

---

## Casos de Uso

### 1. Planejamento Orcamentario

Identificar municipios com baixo PIB per capita para priorizar repasses estaduais e investimentos em infraestrutura.

### 2. Analise Regional

Comparar desempenho economico entre mesorregioes para direcionar politicas setoriais (agricultura, industria, servicos).

### 3. Monitoramento de Politicas

Acompanhar evolucao de indicadores para avaliar impacto de programas como o Projeto Pilares II (Banco Mundial).

### 4. Transparencia Governamental

Disponibilizar dados publicos de forma acessivel para cidadaos, pesquisadores e jornalistas.

---

## Insights Principais

```
CONCENTRACAO ECONOMICA:
- Teresina concentra 37% do PIB estadual
- Top 10 municipios = 57% do PIB
- 164 municipios (73%) tem menos de 10 mil habitantes

DISPARIDADES:
- PIB per capita varia de R$ 5.000 a R$ 30.000
- Mesorregiao Centro-Norte concentra populacao e economia
- Interior (Sudoeste/Sudeste) com maior potencial de crescimento

OPORTUNIDADES:
- Desenvolvimento do Cerrado piauiense
- Diversificacao economica do interior
- Investimento em municipios de baixo IDH
```

---

## Melhorias Futuras

- [ ] Integracao com dados DATASUS (saude)
- [ ] Integracao com dados INEP (educacao)
- [ ] Mapa coropletico interativo com GeoJSON
- [ ] Machine learning para projecoes economicas
- [ ] Alertas automaticos para anomalias
- [ ] Comparativo historico (serie temporal longa)
- [ ] API REST para acesso programatico

---

## Relacao com Projeto Pilares II

Este dashboard foi desenvolvido considerando as necessidades do **Projeto Pilares II** (Banco Mundial), que visa fortalecer a gestao publica do Piaui atraves de:

- Modernizacao da gestao fiscal
- Melhoria na alocacao de recursos
- Transparencia e accountability
- Tomada de decisao baseada em dados

O dashboard demonstra capacidade de criar ferramentas de **Business Intelligence** para o setor publico, competencia especificada no Termo de Referencia para Consultor em Ciencia de Dados.

---

## Licenca

MIT License - veja [LICENSE](../LICENSE)

---

## Autor

**Maxwell Melo** - Especialista em Dados

Portfolio: [maxwellmelo.github.io/portfolio-data-science](https://maxwellmelo.github.io/portfolio-data-science/)

GitHub: [@maxwellmelo](https://github.com/maxwellmelo)

---

<div align="center">

**Dashboard desenvolvido para demonstrar competencias em Business Intelligence e Data Science aplicados ao setor publico.**

*Dados oficiais do IBGE | Visualizacoes interativas com Plotly Dash*

</div>
