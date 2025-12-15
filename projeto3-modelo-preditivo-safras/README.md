# Modelo Preditivo de Safras Agricolas

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat&logo=python&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3+-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-337AB7.svg?style=flat)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458.svg?style=flat&logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Sistema de Machine Learning para previsao de rendimento agricola**

[Demo Notebook](#notebook-demonstrativo) | [Resultados](#resultados) | [Metodologia](#metodologia)

</div>

---

## Resultados em Destaque

| Metrica | Melhor Modelo (Gradient Boosting) |
|---------|-----------------------------------|
| **R2 (Coef. Determinacao)** | 0.90 |
| **RMSE** | 704.86 kg/ha |
| **MAE** | 519.62 kg/ha |
| **MAPE** | 11.11% |

> Metricas obtidas com validacao temporal (TimeSeriesSplit) e sem data leakage.

---

## Notebook Demonstrativo

O notebook [`notebooks/demo_modelo_safras.ipynb`](notebooks/demo_modelo_safras.ipynb) demonstra o pipeline de ML:

### Conteudo

| Secao | Descricao |
|-------|-----------|
| Analise Exploratoria | Estatisticas e visualizacoes |
| Feature Engineering | Criacao de lags e medias moveis |
| Treinamento | 4 modelos comparados |
| Avaliacao | Metricas e feature importance |

### Visualizacoes

- Evolucao do rendimento por cultura (linha)
- Box plot por estado
- Matriz de correlacao (heatmap)
- Comparacao de modelos (barras)
- Predicao vs Real (scatter)
- Feature Importance (barras)

### Resultado do Notebook

```
MELHOR MODELO: Gradient Boosting
   R2: 0.90 (90% da variancia explicada)
   RMSE: ~705 kg/ha
   MAPE: ~11%
```

---

## Problema de Negocio

A predição de rendimento agrícola é crucial para:
- **Planejamento da safra**: Estimar produção esperada
- **Gestão de riscos**: Identificar regiões/culturas de baixa produtividade
- **Políticas públicas**: Direcionar recursos e assistência técnica
- **Mercado de commodities**: Projeções de oferta

## Variável Alvo

**Rendimento (kg/ha)**: Quantidade produzida por hectare plantado, principal indicador de produtividade agrícola.

## Tecnologias Utilizadas

| Categoria | Tecnologia |
|-----------|------------|
| Linguagem | Python 3.10+ |
| ML | Scikit-learn, XGBoost, LightGBM |
| Dados | Pandas, NumPy |
| Visualização | Plotly, Matplotlib, Seaborn |
| Validação | Pydantic |
| Logging | Loguru |
| Testes | Pytest |

## Estrutura do Projeto

```
projeto3-modelo-preditivo-safras/
├── config/
│   └── settings.py           # Configurações centralizadas
├── src/
│   ├── data/
│   │   ├── pam_extractor.py  # Extração dados PAM/IBGE
│   │   └── data_loader.py    # Carregamento e preparação
│   ├── features/
│   │   └── feature_engineer.py # Engenharia de features
│   ├── models/
│   │   ├── trainer.py        # Treinamento de modelos
│   │   └── evaluator.py      # Avaliação e visualizações
│   └── visualization/
│       └── plots.py          # Gráficos agrícolas
├── notebooks/
│   └── 01_analise_e_modelagem.ipynb
├── data/
│   ├── raw/                  # Dados brutos
│   ├── processed/            # Dados processados
│   └── models/               # Modelos salvos
├── tests/
├── outputs/                  # Figuras e relatórios
├── main.py                   # Pipeline CLI
├── requirements.txt
└── README.md
```

## Modelos Implementados

| Modelo | Tipo | Características |
|--------|------|-----------------|
| Linear Regression | Linear | Baseline simples |
| Ridge | Linear | Regularização L2 |
| Lasso | Linear | Regularização L1 |
| Random Forest | Ensemble | Bagging de árvores |
| Gradient Boosting | Ensemble | Boosting sequencial |
| XGBoost | Boosting | Gradiente otimizado |
| LightGBM | Boosting | Histogramas eficientes |

## Features Utilizadas

### Features Originais (PAM)
- `area_plantada_ha`: Área plantada em hectares
- `area_colhida_ha`: Área efetivamente colhida
- `producao_ton`: Produção em toneladas
- `valor_producao_mil_reais`: Valor da produção

### Features Derivadas (Sem Data Leakage)
- `rendimento_kg_ha_lag1/2/3`: Rendimento dos anos anteriores (lags)
- `rendimento_kg_ha_growth_rate`: Taxa de crescimento baseada em lags
- `area_x_rend_lag`: Interacao area x rendimento historico
- `area_plantada_ha_estado_mean/dev`: Agregacoes por estado
- Features de estado, regiao e cultura (one-hot)

**Features Removidas (Data Leakage)**:
- ~~taxa_aproveitamento~~: Correlacionada com target
- ~~produtividade_ton_ha~~: Derivada do target
- ~~rendimento_kg_ha_ma3~~: Inclui valor atual
- ~~rendimento_kg_ha_diff~~: Usa valor atual

## Como Executar

### 1. Instalação

```bash
# Clonar repositório
cd projeto3-modelo-preditivo-safras

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar Pipeline

```bash
# Pipeline completo (EDA + Treinamento)
python main.py

# Apenas análise exploratória
python main.py --eda

# Apenas treinamento
python main.py --train

# Treinar modelos específicos
python main.py --train --models ridge random_forest xgboost

# Fazer predições
python main.py --predict --model-path data/models/model.pkl
```

### 3. Jupyter Notebook

```bash
jupyter notebook notebooks/
```

## Métricas de Avaliação

| Métrica | Descrição |
|---------|-----------|
| RMSE | Raiz do Erro Quadrático Médio |
| MAE | Erro Médio Absoluto |
| R² | Coeficiente de Determinação |
| MAPE | Erro Percentual Absoluto Médio |

## Resultados

| Modelo | RMSE | MAE | R2 | MAPE |
|--------|------|-----|-----|------|
| **Gradient Boosting** | **704.86** | **519.62** | **0.9004** | **11.11%** |
| Ridge | 759.05 | 580.81 | 0.8845 | 15.55% |
| Linear Regression | 759.20 | 581.15 | 0.8845 | 15.57% |
| Random Forest | 813.04 | 603.64 | 0.8675 | 12.86% |

*Metricas obtidas com TimeSeriesSplit (treino: 2000-2019, teste: 2019-2023)*

## Metodologia

### Prevencao de Data Leakage

Este projeto implementa boas praticas para evitar vazamento de dados:

1. **TimeSeriesSplit**: Dados de treino sempre anteriores aos de teste
2. **Lag Features**: Apenas valores passados sao usados como features
3. **VIF Analysis**: Deteccao automatica de multicolinearidade
4. **Feature Audit**: Features derivadas do target foram removidas

### Validacao

- Treino: Anos 2000-2019 (80% dos dados)
- Teste: Anos 2019-2023 (20% dos dados)
- Sem sobreposicao temporal entre treino e teste

## Fonte de Dados

### API SIDRA/IBGE

- **Agregado 1612**: Lavouras Temporárias (área, produção, rendimento)
- **Agregado 1613**: Lavouras Permanentes
- **Período**: 2000-2023
- **Granularidade**: Municipal (N6) ou Estadual (N3)

### Culturas Principais

- Soja (em grão)
- Milho (em grão)
- Arroz (em casca)
- Feijão (em grão)
- Cana-de-açúcar
- Café (em grão)
- Algodão herbáceo
- Mandioca

## Visualizações Geradas

- Séries temporais de rendimento por cultura
- Comparação entre estados
- Matriz de correlação
- Predições vs Valores Reais
- Análise de Resíduos
- Feature Importance
- Comparação de Modelos

## Limitações e Melhorias Futuras

### Limitações
- Dados sintéticos para demonstração (API pode ter rate limiting)
- Não inclui variáveis climáticas (precipitação, temperatura)
- Não considera fatores de solo

### Melhorias Futuras
1. Integrar dados climáticos (INMET)
2. Adicionar dados de solo (EMBRAPA)
3. Implementar modelos de séries temporais (LSTM, Prophet)
4. Criar API REST para servir predições
5. Dashboard interativo com Streamlit

## Testes

```bash
# Executar testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=src --cov-report=html
```

## Licença

MIT License - veja [LICENSE](LICENSE)

## Autor

**Maxwell** - Especialista em Dados

---

*Desenvolvido como demonstracao de competencias em Machine Learning e Data Science*
