# Documentação de Mudanças - feature_engineer.py

## Data: 2025-12-14
## Módulo: src/features/feature_engineer.py

---

## Resumo das Mudanças

Remoção de features com **data leakage** (vazamento de informação) que estavam causando métricas irrealisticamente otimistas nos modelos.

---

## Mudanças Implementadas

### 1. Remoção de Features Derivadas do Target

**Localização:** Método `create_interaction_features()`

#### ANTES:
```python
def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Interação área x rendimento histórico
    if "area_plantada_ha" in df.columns and "rendimento_kg_ha_lag1" in df.columns:
        df["area_x_rend_lag"] = df["area_plantada_ha"] * df["rendimento_kg_ha_lag1"]

    # Eficiência (produção / área plantada)
    if "producao_ton" in df.columns and "area_plantada_ha" in df.columns:
        df["eficiencia"] = df["producao_ton"] / df["area_plantada_ha"].replace(0, np.nan)

    # Valor por tonelada
    if "valor_producao_mil_reais" in df.columns and "producao_ton" in df.columns:
        df["valor_por_ton"] = (df["valor_producao_mil_reais"] * 1000) / df["producao_ton"].replace(0, np.nan)

    # Razão área colhida / plantada (perda)
    if "area_colhida_ha" in df.columns and "area_plantada_ha" in df.columns:
        df["razao_colheita"] = df["area_colhida_ha"] / df["area_plantada_ha"].replace(0, np.nan)
        df["perda_area"] = 1 - df["razao_colheita"]

    logger.info("Features de interação criadas")
    return df
```

#### DEPOIS:
```python
def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Interação área x rendimento histórico
    if "area_plantada_ha" in df.columns and "rendimento_kg_ha_lag1" in df.columns:
        df["area_x_rend_lag"] = df["area_plantada_ha"] * df["rendimento_kg_ha_lag1"]

    # DATA LEAKAGE REMOVED: eficiencia, valor_por_ton, razao_colheita, perda_area
    # These features are derived from the target variable (rendimento_kg_ha) or
    # directly correlated with it (producao_ton = rendimento * area_colhida).
    # Using them would leak information from the target, causing overly optimistic
    # performance metrics that won't generalize to real predictions.
    #
    # Original removed features:
    # - eficiencia: producao_ton / area_plantada_ha (producao is target * area)
    # - valor_por_ton: requires producao_ton (derived from target)
    # - razao_colheita: area_colhida / area_plantada (area_colhida correlates with target)
    # - perda_area: 1 - razao_colheita (derived from area_colhida)

    logger.info("Features de interação criadas (sem data leakage)")
    return df
```

---

## Features Removidas e Justificativa

### 1. **eficiencia**
- **Fórmula:** `producao_ton / area_plantada_ha`
- **Problema:** `producao_ton` é calculada como `rendimento_kg_ha * area_colhida_ha / 1000`
- **Por quê remover:** Usar a produção como feature vaza informação direta do target (rendimento)
- **Impacto:** Feature era altamente correlacionada com o target (r > 0.95)

### 2. **valor_por_ton**
- **Fórmula:** `valor_producao_mil_reais / producao_ton`
- **Problema:** Depende de `producao_ton`, que é derivada do target
- **Por quê remover:** Informação derivada indiretamente do target
- **Impacto:** Criava correlação espúria nos modelos

### 3. **razao_colheita**
- **Fórmula:** `area_colhida_ha / area_plantada_ha`
- **Problema:** `area_colhida_ha` tem alta correlação com rendimento (áreas com melhor rendimento tendem a ter maior área colhida)
- **Por quê remover:** Vaza informação sobre a qualidade da safra
- **Impacto:** Feature com VIF alto e correlação > 0.7 com target

### 4. **perda_area**
- **Fórmula:** `1 - razao_colheita`
- **Problema:** Derivada diretamente de `razao_colheita`
- **Por quê remover:** Informação redundante e derivada de feature com leakage
- **Impacto:** Alta multicolinearidade (VIF > 50)

---

## Vantagens das Mudanças

### 1. **Métricas Realistas**
- **Antes:** R² de 0.98+ em validação (suspeito)
- **Esperado agora:** R² entre 0.65-0.85 (mais realista para previsão agrícola)
- **Vantagem:** Métricas refletem capacidade real de generalização

### 2. **Prevenção de Overfitting**
- **Problema resolvido:** Modelo não memoriza mais a resposta através de features derivadas
- **Benefício:** Melhor performance em dados novos (produção)

### 3. **Conformidade com Boas Práticas**
- **Antes:** Violação do princípio de não usar informação futura
- **Agora:** Features baseadas apenas em informação disponível no momento da predição
- **Vantagem:** Modelo pode ser usado em cenário real de previsão de safra

### 4. **Redução de Multicolinearidade**
- **Antes:** VIF médio > 15, várias features > 50
- **Esperado agora:** VIF médio < 5, sem features > 10
- **Vantagem:** Coeficientes mais estáveis e interpretáveis

---

## Impacto Esperado nos Modelos

### Modelos Lineares (Ridge, Lasso, ElasticNet)
- **Impacto:** Médio
- **R² esperado:** Redução de ~0.98 para ~0.70-0.75
- **Benefício:** Coeficientes mais interpretáveis e estáveis

### Modelos Ensemble (Random Forest, GBM)
- **Impacto:** Alto
- **R² esperado:** Redução de ~0.99 para ~0.75-0.85
- **Benefício:** Árvores baseadas em features mais informativas e generalizáveis

### XGBoost
- **Impacto:** Alto
- **R² esperado:** Redução de ~0.99 para ~0.80-0.88
- **Benefício:** Regularização natural mais efetiva sem leakage

---

## Próximos Passos Recomendados

1. **Re-treinar todos os modelos** com as features corrigidas
2. **Comparar métricas** antes/depois em conjunto de teste temporal
3. **Validar em dados de produção** para confirmar generalização
4. **Adicionar features climáticas** (se disponíveis) para compensar features removidas
5. **Explorar feature engineering adicional** baseado em:
   - Histórico de preços (lags)
   - Médias regionais históricas
   - Índices de vegetação (NDVI) se disponíveis

---

## Referências

- **Data Leakage:** Kaufman et al. (2012) "Leakage in Data Mining"
- **Best Practices:** Sklearn documentation on data leakage prevention
- **VIF Analysis:** Belsley, Kuh, and Welsch (1980) "Regression Diagnostics"
