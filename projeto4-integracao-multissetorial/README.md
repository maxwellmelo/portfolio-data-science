# Sistema de Integraçao Multissetorial - Piauí

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat&logo=fastapi&logoColor=white)
![IBGE](https://img.shields.io/badge/Dados-IBGE%20Real-blue.svg?style=flat)
![Plotly](https://img.shields.io/badge/Plotly-Interativo-3F4F75.svg?style=flat&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**API REST para integração de dados governamentais multissetoriais do Piauí**

[Demo Notebook](#-notebook-demonstrativo) | [Endpoints](#endpoints-da-api) | [Como Executar](#como-executar)

</div>

---

## Resultados em Destaque

| Métrica | Valor |
|---------|-------|
| **Dados Reais IBGE** | PIB + População (2020-2024) |
| **Municípios Cobertos** | 224 municípios do Piauí |
| **PIB Total do Estado** | R$ 64 bilhões (2021) |
| **Endpoints da API** | 13 endpoints REST |
| **Visualizações** | 10+ gráficos interativos (Plotly) |

---

## Notebook Demonstrativo

O notebook [`notebooks/demo_dados_piaui.ipynb`](notebooks/demo_dados_piaui.ipynb) apresenta análises visuais dos dados reais do IBGE:

### Visualizações Incluídas

| Análise | Tipo de Gráfico |
|---------|-----------------|
| Indicadores do Estado | Cards interativos |
| Top 10 Maiores Economias | Barras horizontais |
| Distribuição PIB per Capita | Histograma + Box plot |
| Crescimento PIB 2020-2021 | Barras com cores |
| Evolução Populacional | Linha temporal |
| Municípios por Porte | Pizza + Barras |
| PIB x População | Scatter interativo |
| Correlações | Heatmap |
| Composição do PIB | Treemap hierárquico |

### Principais Insights (Dados Reais 2021)

```
📊 ECONOMIA:
   • PIB Total do Piauí: R$ 64.0 bilhões
   • Crescimento médio 2020-2021: 14.7%
   • PIB per capita médio: R$ 15.839

🏙️ CONCENTRAÇÃO:
   • Teresina concentra 37.3% do PIB estadual
   • Top 10 municípios: 57.4% do PIB

👥 POPULAÇÃO:
   • Total: 3.28 milhões de habitantes
   • 164 municípios com menos de 10 mil habitantes (73%)
```

---

## Fontes de Dados

### Dados Reais (IBGE)
| Dataset | Registros | Anos | Fonte |
|---------|-----------|------|-------|
| PIB Municipal | 448 | 2020-2021 | IBGE SIDRA |
| População | 896 | 2019-2024 | IBGE SIDRA |

### Dados Sintéticos (Demonstração)
| Dataset | Registros | Fonte Simulada |
|---------|-----------|----------------|
| Mortalidade | 5.000 | DATASUS/SIM |
| Nascimentos | 3.000 | DATASUS/SINASC |
| Escolas | 500 | INEP |
| IDEB | 4.480 | INEP |
| CadÚnico | 10.000 | MDS |

---

## Tecnologias Utilizadas

| Categoria | Tecnologia |
|-----------|------------|
| API REST | FastAPI |
| Dados Reais | IBGE SIDRA API |
| Visualização | Plotly, Matplotlib, Seaborn |
| Validação | Pydantic |
| Análise | Pandas, NumPy |
| Containerização | Docker |

## Estrutura do Projeto

```
projeto4-integracao-multissetorial/
├── config/
│   └── settings.py              # Configurações centralizadas
├── src/
│   ├── extractors/
│   │   ├── synthetic_generator.py  # Gerador de dados sintéticos
│   │   └── ibge_extractor.py       # Extrator de dados reais IBGE
│   ├── api/
│   │   ├── main.py              # API FastAPI
│   │   └── data_loader.py       # Gerenciador de fontes de dados
│   └── ...
├── notebooks/
│   └── demo_dados_piaui.ipynb   # 📊 Notebook demonstrativo
├── data/
│   ├── real/                    # Dados reais do IBGE
│   │   ├── economia_completo.csv
│   │   └── populacao.csv
│   └── processed/               # Dados sintéticos
├── tests/
├── docs/
├── main.py                      # CLI principal
└── README.md
```

## Como Executar

### 1. Instalação

```bash
cd projeto4-integracao-multissetorial

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 2. Visualizar Notebook Demonstrativo

```bash
jupyter notebook notebooks/demo_dados_piaui.ipynb
```

### 3. Atualizar Dados Reais do IBGE (opcional)

```bash
python src/extractors/ibge_extractor.py
```

### 4. Iniciar API REST

```bash
python main.py api
```

A API estará disponível em: http://localhost:8000

### 5. Acessar Documentação

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints da API

| Endpoint | Método | Descrição | Dados |
|----------|--------|-----------|-------|
| `/` | GET | Informações da API | - |
| `/health` | GET | Status de saúde | - |
| `/fontes` | GET | Lista fontes de dados | - |
| `/fontes/status` | GET | **Status real vs sintético** | - |
| `/municipios` | GET | Lista 224 municípios do PI | - |
| `/saude/mortalidade` | GET | Dados de mortalidade | Sintético |
| `/saude/nascimentos` | GET | Dados de nascimentos | Sintético |
| `/educacao/escolas` | GET | Dados de escolas | Sintético |
| `/educacao/ideb` | GET | Dados do IDEB | Sintético |
| `/economia/pib` | GET | **PIB municipal** | **IBGE Real** |
| `/assistencia/cadunico` | GET | Dados do CadÚnico | Sintético |
| `/indicadores/{id}` | GET | Indicadores consolidados | Misto |

### Exemplo: Consultar PIB de Teresina (Dados Reais)

```python
import requests

response = requests.get("http://localhost:8000/economia/pib?municipio_id=2211001")
data = response.json()

print(f"Dados Reais: {data['dados_reais']}")  # True
print(f"Fonte: {data['fonte']}")  # IBGE - Sistema de Contas Regionais

for registro in data['data']:
    print(f"Ano {registro['ano']}: R$ {registro['pib_total_mil_reais']/1_000_000:.1f} bilhões")
```

**Saída:**
```
Dados Reais: True
Fonte: IBGE - Sistema de Contas Regionais
Ano 2020: R$ 21.6 bilhões
Ano 2021: R$ 23.9 bilhões
```

### Exemplo: Status das Fontes de Dados

```bash
curl http://localhost:8000/fontes/status
```

```json
{
    "resumo": {
        "total_datasets": 7,
        "datasets_reais": 2,
        "datasets_sinteticos": 5
    },
    "datasets": {
        "economia_pib": {
            "dados_reais": true,
            "fonte": "IBGE - SIDRA",
            "registros": 448
        },
        "populacao": {
            "dados_reais": true,
            "fonte": "IBGE - SIDRA",
            "registros": 896
        }
    }
}
```

## Modelo de Dados

```
┌─────────────────┐     ┌─────────────────┐
│  dim_municipio  │     │  dim_tempo      │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ ano (PK)        │
│ nome            │     │ mes             │
│ uf              │     │ trimestre       │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│fato_saude │  │fato_educa │  │fato_econ  │
│(sintético)│  │(sintético)│  │(IBGE real)│
└───────────┘  └───────────┘  └───────────┘
```

## Testes

```bash
pytest tests/ -v
```

## Roadmap

- [x] Geração de dados sintéticos
- [x] API REST com FastAPI
- [x] Documentação automática (Swagger)
- [x] **Integração com dados reais do IBGE**
- [x] **Notebook demonstrativo com visualizações**
- [x] Indicação de fonte (real vs sintético)
- [ ] Dashboard interativo (Streamlit)
- [ ] Mais dados reais (DATASUS, INEP)
- [ ] Cache com Redis

## Licença

MIT License

## Autor

**Maxwell** - Especialista em Dados

---

<div align="center">

**[Ver Notebook Demonstrativo](notebooks/demo_dados_piaui.ipynb)**

*Integração de dados governamentais com API REST e visualizações interativas*

</div>
