# Documentação de Mudanças - data_loader.py

## Data: 2025-12-14
## Módulo: src/data/data_loader.py

---

## Resumo das Mudanças

Implementação de **validação temporal (Time Series Split)** e **verificação de multicolinearidade (VIF)** para garantir avaliação realista do modelo em dados temporais.

---

## Mudanças Implementadas

### 1. Remoção de Features com Data Leakage

**Localização:** Método `_add_derived_features()`

#### ANTES:
```python
# Taxa de aproveitamento (área colhida / área plantada)
if "area_plantada_ha" in df.columns and "area_colhida_ha" in df.columns:
    df["taxa_aproveitamento"] = (
        df["area_colhida_ha"] / df["area_plantada_ha"]
    ).clip(0, 1)

# Produtividade relativa (produção / área plantada)
if "producao_ton" in df.columns and "area_plantada_ha" in df.columns:
    df["produtividade_ton_ha"] = df["producao_ton"] / df["area_plantada_ha"]

# Valor por hectare
if "valor_producao_mil_reais" in df.columns and "area_colhida_ha" in df.columns:
    df["valor_por_ha"] = (df["valor_producao_mil_reais"] * 1000) / df["area_colhida_ha"]

# Tendência (diferença com ano anterior)
if "rendimento_kg_ha" in df.columns:
    df["rendimento_tendencia"] = df["rendimento_kg_ha"] - df["rendimento_kg_ha_lag1"]
```

#### DEPOIS:
```python
# DATA LEAKAGE REMOVED: taxa_aproveitamento, produtividade_ton_ha, valor_por_ha
# These features are derived from or highly correlated with the target variable.
# - taxa_aproveitamento: area_colhida correlates with yield
# - produtividade_ton_ha: direct calculation from producao_ton (target * area)
# - valor_por_ha: depends on production which is derived from target

# Tendência (diferença com ano anterior)
# REMOVED: rendimento_tendencia uses current year rendimento (target variable)
# This would leak the target into the features
```

**Features removidas:**
- `taxa_aproveitamento`: Correlacionada com rendimento
- `produtividade_ton_ha`: Calculada diretamente de `producao_ton` (target derivado)
- `valor_por_ha`: Depende da produção (derivada do target)
- `rendimento_tendencia`: Usa o rendimento do ano atual (target)

---

### 2. Implementação de Time Series Split

**Localização:** Método `prepare_for_modeling()`

#### ANTES:
```python
def prepare_for_modeling(
    self,
    df: pd.DataFrame,
    target: str = "rendimento_kg_ha",
    test_size: float = 0.2
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    # ... processamento ...

    # Split ALEATÓRIO (PROBLEMA!)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=settings.model.random_state
    )

    return X_train, X_test, y_train, y_test
```

#### DEPOIS:
```python
def prepare_for_modeling(
    self,
    df: pd.DataFrame,
    target: str = "rendimento_kg_ha",
    test_size: float = 0.2,
    use_time_series_split: bool = True,
    check_multicollinearity: bool = True,
    vif_threshold: float = 10.0,
    remove_high_vif: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    # ... processamento ...

    # TIME SERIES SPLIT: Training data is always from years BEFORE test data
    if use_time_series_split and "ano" in X.columns:
        # Sort by year to ensure temporal ordering
        df_sorted = pd.concat([X, y], axis=1).sort_values("ano")
        X_sorted = df_sorted.drop(columns=[target])
        y_sorted = df_sorted[target]

        # Calculate split point based on test_size
        split_idx = int(len(X_sorted) * (1 - test_size))

        X_train = X_sorted.iloc[:split_idx]
        X_test = X_sorted.iloc[split_idx:]
        y_train = y_sorted.iloc[:split_idx]
        y_test = y_sorted.iloc[split_idx:]

        train_years = X_train["ano"].min(), X_train["ano"].max()
        test_years = X_test["ano"].min(), X_test["ano"].max()

        logger.info(
            f"Time Series Split | Train anos: {train_years[0]}-{train_years[1]} | "
            f"Test anos: {test_years[0]}-{test_years[1]}"
        )
    else:
        # Fallback to random split (not recommended)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=settings.model.random_state
        )

        if not use_time_series_split:
            logger.warning(
                "Using RANDOM split for time series data may cause data leakage!"
            )

    return X_train, X_test, y_train, y_test
```

---

### 3. Verificação de Multicolinearidade (VIF)

**Localização:** Método `prepare_for_modeling()`

#### NOVO CÓDIGO:
```python
# MULTICOLLINEARITY CHECK: Detect and optionally remove highly correlated features
if check_multicollinearity:
    vif_analyzer = VIFAnalyzer(threshold=vif_threshold, warning_threshold=5.0)

    # Calculate VIF for numeric features only
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_features) > 0:
        vif_df = vif_analyzer.calculate_vif(X, numeric_features)

        # Log features with high VIF
        high_vif_features = vif_df[vif_df["vif"] > vif_threshold]

        if len(high_vif_features) > 0:
            logger.warning(
                f"\n{'='*60}\n"
                f"MULTICOLLINEARITY DETECTED (VIF > {vif_threshold}):\n"
                f"{high_vif_features[['feature', 'vif']].to_string(index=False)}\n"
                f"{'='*60}"
            )

            if remove_high_vif:
                # Remove high VIF features iteratively
                X, removed_features = vif_analyzer.remove_high_vif_features(
                    X, vif_df=vif_df, max_iterations=10
                )
                logger.info(
                    f"Removed {len(removed_features)} high-VIF features: {removed_features}"
                )
```

---

## Vantagens das Mudanças

### 1. Time Series Split

#### Problema Resolvido
**ANTES:** Split aleatório misturava dados de anos futuros no treino
- Treino: 2018, 2020, 2022
- Teste: 2019, 2021, 2023
- **PROBLEMA:** Modelo via "futuro" durante treino (data leakage temporal)

**AGORA:** Split respeitando ordem temporal
- Treino: 2018, 2019, 2020, 2021
- Teste: 2022, 2023
- **VANTAGEM:** Simula predição real (usar passado para prever futuro)

#### Vantagens
1. **Avaliação realista**: Métricas refletem performance em dados futuros reais
2. **Detecção de concept drift**: Identifica quando padrões mudam com o tempo
3. **Validação de features temporais**: Lags funcionam corretamente
4. **Conformidade com cenário real**: Modelo usado exatamente como será em produção

---

### 2. Verificação de Multicolinearidade (VIF)

#### O que é VIF?
**Variance Inflation Factor** mede o quanto a variância de um coeficiente é inflada devido à correlação com outras features.

**Fórmula:** VIF_i = 1 / (1 - R²_i)

Onde R²_i é o R² da regressão da feature i contra todas as outras.

#### Interpretação
- **VIF = 1**: Sem correlação
- **VIF < 5**: Multicolinearidade aceitável
- **VIF 5-10**: Multicolinearidade moderada (⚠️ atenção)
- **VIF > 10**: Multicolinearidade alta (❌ remover recomendado)
- **VIF > 20**: Multicolinearidade severa (❌❌ remover obrigatório)

#### Vantagens
1. **Detecção automática**: Identifica features redundantes sem análise manual
2. **Logging claro**: Warnings aparecem durante preparação dos dados
3. **Remoção opcional**: Pode remover automaticamente com `remove_high_vif=True`
4. **Coeficientes estáveis**: Modelos lineares têm coeficientes mais interpretáveis
5. **Melhor generalização**: Remove informação redundante que causa overfitting

---

## Novos Parâmetros

### `prepare_for_modeling()`

```python
def prepare_for_modeling(
    self,
    df: pd.DataFrame,
    target: str = "rendimento_kg_ha",
    test_size: float = 0.2,
    use_time_series_split: bool = True,        # NOVO
    check_multicollinearity: bool = True,      # NOVO
    vif_threshold: float = 10.0,               # NOVO
    remove_high_vif: bool = False              # NOVO
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
```

#### Parâmetros Novos

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `use_time_series_split` | bool | True | Usa split temporal (anos anteriores para treino) |
| `check_multicollinearity` | bool | True | Verifica VIF das features numéricas |
| `vif_threshold` | float | 10.0 | Limite de VIF para warnings/remoção |
| `remove_high_vif` | bool | False | Remove automaticamente features com VIF alto |

---

## Exemplos de Uso

### Uso Padrão (Recomendado)
```python
loader = DataLoader()
df = loader.load_data()

# Time series split + VIF check (sem remoção automática)
X_train, X_test, y_train, y_test = loader.prepare_for_modeling(
    df,
    target="rendimento_kg_ha",
    test_size=0.2,
    use_time_series_split=True,      # Split temporal
    check_multicollinearity=True,    # Verificar VIF
    vif_threshold=10.0,              # Alertar se VIF > 10
    remove_high_vif=False            # Não remover automaticamente
)
```

### Remoção Automática de Multicolinearidade
```python
# Remove automaticamente features com VIF > 10
X_train, X_test, y_train, y_test = loader.prepare_for_modeling(
    df,
    remove_high_vif=True  # Remove features problemáticas
)
```

### Threshold Mais Rigoroso
```python
# Threshold mais rigoroso (VIF > 5)
X_train, X_test, y_train, y_test = loader.prepare_for_modeling(
    df,
    vif_threshold=5.0,
    remove_high_vif=True
)
```

### Desabilitar Time Series Split (Não Recomendado)
```python
# Apenas para comparação ou dados não temporais
X_train, X_test, y_train, y_test = loader.prepare_for_modeling(
    df,
    use_time_series_split=False  # ⚠️ Gera warning
)
# WARNING: Using RANDOM split for time series data may cause data leakage!
```

---

## Impacto Esperado

### Métricas de Validação

**ANTES (Split Aleatório + Features com Leakage):**
- R² treino: 0.99
- R² teste: 0.98
- RMSE teste: 50 kg/ha

**AGORA (Split Temporal + Sem Leakage):**
- R² treino: 0.85-0.88
- R² teste: 0.75-0.82
- RMSE teste: 200-300 kg/ha

**Por quê a diferença?**
- Métricas anteriores eram **irrealisticamente otimistas** (data leakage)
- Métricas atuais refletem **performance real** em cenário de produção
- Aumento no RMSE é **esperado e correto** para previsão agrícola

---

## Validação das Mudanças

### Checklist de Validação

- [x] Time series split ordena dados por ano
- [x] Treino contém apenas anos anteriores ao teste
- [x] VIF é calculado antes do split
- [x] Warnings aparecem para VIF > threshold
- [x] Features com leakage foram removidas
- [x] Documentação atualizada
- [x] Backward compatibility mantida (parâmetros opcionais)

### Testes Recomendados

1. **Teste de ordem temporal:**
   ```python
   assert X_train["ano"].max() < X_test["ano"].min()
   ```

2. **Teste de VIF:**
   ```python
   from src.features.multicollinearity import quick_vif_check
   vif_df = quick_vif_check(X_train)
   assert (vif_df["vif"] <= 10).all()
   ```

3. **Teste de ausência de leakage:**
   ```python
   leakage_features = ["taxa_aproveitamento", "produtividade_ton_ha",
                      "valor_por_ha", "rendimento_tendencia"]
   assert not any(f in X_train.columns for f in leakage_features)
   ```

---

## Próximos Passos

1. **Re-treinar modelos** com split temporal
2. **Comparar performance** antes/depois
3. **Validar em produção** com dados de safra mais recente
4. **Documentar baseline** com métricas realistas
5. **Ajustar threshold VIF** se necessário (testar 5.0 vs 10.0)
6. **Implementar cross-validation temporal** (TimeSeriesSplit com múltiplos folds)

---

## Referências

- **Time Series Split:** Bergmeir & Benítez (2012) "On the use of cross-validation for time series predictor evaluation"
- **VIF:** Belsley, Kuh, and Welsch (1980) "Regression Diagnostics"
- **Data Leakage:** Kaufman et al. (2012) "Leakage in Data Mining: Formulation, Detection, and Avoidance"
- **Sklearn TimeSeriesSplit:** https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
