# Projeto 3 - Modelo Preditivo Safras: Resultados da Execução

## Execução Realizada
**Data**: 14/12/2025

## Dataset Utilizado

### Resumo
| Métrica | Valor |
|---------|-------|
| Total de registros | 4.800 |
| Período | 2000-2023 |
| Culturas | 5 |
| Estados | 27 |
| Features | 19 |

### Culturas Analisadas
1. Soja
2. Milho
3. Algodão
4. Cana-de-açúcar
5. Feijão

### Estatísticas Descritivas
| Variável | Média | Std | Min | Max |
|----------|-------|-----|-----|-----|
| Área Plantada (ha) | 4.236 | 14.788 | 5,81 | 572.362 |
| Produção (ton) | 17.852 | 78.848 | 6,37 | 4.316.234 |
| Rendimento (kg/ha) | 2.631 | 1.053 | 500 | 6.000 |

### Features Engenheiradas
- Lag features (t-1)
- Tendência de rendimento
- Variáveis climáticas (simuladas)
- Indicadores temporais

## Modelos Disponíveis
| Modelo | Descrição |
|--------|-----------|
| Linear Regression | Baseline |
| Ridge | Regularização L2 |
| Lasso | Regularização L1 |
| Random Forest | Ensemble de árvores |
| Gradient Boosting | Boosting tradicional |
| XGBoost | Gradient boosting otimizado |
| LightGBM | Boosting eficiente |

## Valores Nulos (após feature engineering)
| Feature | Nulos |
|---------|-------|
| rendimento_kg_ha_lag1 | 135 |
| area_plantada_ha_lag1 | 135 |
| producao_ton_lag1 | 135 |
| rendimento_tendencia | 135 |

*Nota: Valores nulos são esperados para o primeiro ano de cada série.*

## Como Executar
```bash
cd projeto3-modelo-preditivo-safras

# Treinar modelo com dados sintéticos
python main.py --synthetic --train --models random_forest xgboost

# Avaliar modelo
python main.py --synthetic --evaluate --model-path models/best_model.joblib
```
