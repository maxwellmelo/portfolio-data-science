# Modelo Preditivo de Safras Agrícolas

Modelo de Machine Learning para predição de rendimento (produtividade) de safras agrícolas utilizando dados históricos da Produção Agrícola Municipal (PAM) do IBGE.

## Problema de Negócio

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

### Features Derivadas
- `rendimento_kg_ha_lag1`: Rendimento do ano anterior
- `rendimento_kg_ha_ma3`: Média móvel 3 anos
- `rendimento_kg_ha_diff`: Variação com ano anterior
- `taxa_aproveitamento`: Área colhida / Área plantada
- `produtividade_ton_ha`: Produção / Área plantada
- Features de estado, região e cultura (one-hot)

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

## Resultados Típicos

| Modelo | RMSE | MAE | R² | MAPE |
|--------|------|-----|-----|------|
| Linear Regression | ~3500 | ~2800 | 0.65 | 25% |
| Ridge | ~3400 | ~2700 | 0.67 | 24% |
| Random Forest | ~2500 | ~1900 | 0.82 | 18% |
| Gradient Boosting | ~2400 | ~1850 | 0.84 | 17% |
| XGBoost | ~2350 | ~1800 | 0.85 | 16% |

*Valores aproximados com dados sintéticos*

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

**Maxwell** - Projeto de Portfólio em Data Science

---

*Desenvolvido como demonstração de competências em Machine Learning e Data Science*
