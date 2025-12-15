# Documentação - Melhorias do Modelo Preditivo v2.0

## Visão Geral

Esta pasta contém a documentação completa das melhorias implementadas no projeto de **Modelo Preditivo de Safras Agrícolas**.

**Data:** 2025-12-14
**Versão:** 2.0.0
**Status:** ✅ Production Ready

---

## Arquivos de Documentação

### 📋 CHANGELOG.md
**Resumo executivo de todas as mudanças**

Leia este arquivo primeiro para entender:
- O que mudou
- Por que mudou
- Impacto esperado nas métricas
- Checklist de validação
- Próximos passos

**Público-alvo:** Todos (desenvolvedores, cientistas de dados, gestores)

---

### 🔧 feature_engineer.md
**Documentação de mudanças em src/features/feature_engineer.py**

Detalhes sobre:
- Remoção de features com data leakage
- Features removidas e justificativas
- Impacto em cada tipo de modelo
- Comparação antes/depois

**Público-alvo:** Cientistas de dados, engenheiros de ML

---

### 📊 data_loader.md
**Documentação de mudanças em src/data/data_loader.py**

Detalhes sobre:
- Implementação de Time Series Split
- Verificação de multicolinearidade (VIF)
- Novos parâmetros e uso
- Exemplos práticos

**Público-alvo:** Cientistas de dados, engenheiros de dados

---

### ⚡ trainer.md
**Documentação de mudanças em src/models/trainer.py**

Detalhes sobre:
- Configurações otimizadas do XGBoost
- Hiperparâmetros default e grid search
- Exemplos de tuning avançado
- Troubleshooting

**Público-alvo:** Cientistas de dados, MLOps

---

### 🔍 multicollinearity.md
**Documentação do módulo src/features/multicollinearity.py**

Guia completo sobre:
- O que é VIF e multicolinearidade
- Como usar o VIFAnalyzer
- Exemplos de uso
- Interpretação de resultados

**Público-alvo:** Cientistas de dados, estatísticos

---

## Índice de Mudanças por Tema

### 🚨 Data Leakage (Crítico)
- **Arquivo:** feature_engineer.md, data_loader.md
- **Features removidas:** 7 features com vazamento de informação
- **Impacto:** Métricas realistas, modelo generalizável

### 📅 Validação Temporal
- **Arquivo:** data_loader.md
- **Mudança:** Split aleatório → Time Series Split
- **Impacto:** Avaliação realista de performance futura

### 📈 Otimização XGBoost
- **Arquivo:** trainer.md
- **Mudança:** Defaults genéricos → Configuração otimizada
- **Impacto:** Melhor performance + menos overfitting

### 🔗 Multicolinearidade
- **Arquivo:** multicollinearity.md
- **Mudança:** Novo módulo VIF completo
- **Impacto:** Detecção automática, coeficientes estáveis

---

## Quick Start

### 1. Entender as Mudanças (5 min)
```bash
# Ler resumo executivo
cat docs/CHANGELOG.md
```

### 2. Código Básico (Já Funciona!)
```python
# Código antigo continua funcionando (backward compatible)
from src.data.data_loader import DataLoader
from src.models.trainer import ModelTrainer

loader = DataLoader()
df = loader.load_data()

X_train, X_test, y_train, y_test = loader.prepare_for_modeling(df)

trainer = ModelTrainer()
trainer.train_multiple_models(X_train, y_train)
results = trainer.evaluate_all(X_test, y_test)
```

### 3. Código Recomendado (Com Novas Features)
```python
# Usar novas funcionalidades
X_train, X_test, y_train, y_test = loader.prepare_for_modeling(
    df,
    use_time_series_split=True,      # ✅ Validação temporal
    check_multicollinearity=True,    # ✅ Verificar VIF
    vif_threshold=10.0,              # ✅ Alertar VIF alto
    remove_high_vif=False            # ⚠️ Não remove automaticamente
)

# XGBoost agora tem defaults otimizados
trainer.train_model(X_train, y_train, "xgboost")
```

### 4. Verificar VIF Manualmente
```python
from src.features.multicollinearity import quick_vif_check

# Check rápido
vif_df = quick_vif_check(X_train, threshold=10.0)
print(vif_df)
```

---

## Fluxo de Leitura Recomendado

### Para Cientistas de Dados:
1. **CHANGELOG.md** - Visão geral
2. **data_loader.md** - Time series split + VIF
3. **feature_engineer.md** - Features removidas
4. **trainer.md** - XGBoost
5. **multicollinearity.md** - VIF detalhado

### Para Desenvolvedores/MLOps:
1. **CHANGELOG.md** - Mudanças implementadas
2. **data_loader.md** - Novos parâmetros
3. **trainer.md** - Configuração de modelos

### Para Gestores/Product Owners:
1. **CHANGELOG.md** - Seção "Resumo Executivo"
2. **CHANGELOG.md** - Seção "Impacto Esperado nas Métricas"

---

## Perguntas Frequentes

### Por que as métricas "pioraram"?

**Resposta:** As métricas não pioraram - elas agora refletem a **performance real** do modelo.

- **Antes:** R² = 0.98 (irreal, devido a data leakage)
- **Agora:** R² = 0.75-0.85 (realista para previsão agrícola)

A performance em **produção** será próxima dos novos valores de teste.

---

### Preciso re-treinar os modelos?

**Resposta:** Sim, é **altamente recomendado**.

Os modelos antigos:
- Usavam features com leakage
- Foram validados com split aleatório
- Não refletem performance real

Re-treinar com o código atualizado garantirá métricas confiáveis.

---

### O código antigo vai quebrar?

**Resposta:** Não, mantivemos **100% backward compatibility**.

Todos os novos parâmetros são **opcionais**:
- `use_time_series_split=True` (default)
- `check_multicollinearity=True` (default)
- `remove_high_vif=False` (default)

O código antigo continuará funcionando, mas **com as melhorias ativadas por padrão**.

---

### Como desabilitar as novas features?

**Resposta:** Passar parâmetros explicitamente:

```python
# Desabilitar time series split (não recomendado)
X_train, X_test, y_train, y_test = loader.prepare_for_modeling(
    df,
    use_time_series_split=False
)

# Desabilitar VIF check
X_train, X_test, y_train, y_test = loader.prepare_for_modeling(
    df,
    check_multicollinearity=False
)
```

---

### Qual threshold de VIF devo usar?

**Resposta:** Depende do seu caso:

| Threshold | Uso |
|-----------|-----|
| VIF > 5 | Modelos lineares (Ridge, Lasso) |
| VIF > 10 | Padrão (recomendado) |
| VIF > 20 | Apenas problemas severos |

**Recomendação:** Comece com 10.0, ajuste conforme necessário.

---

### XGBoost está muito lento no grid search

**Resposta:** Reduza o espaço de busca:

```python
# Grid menor (36 combinações vs 108)
params = {
    "n_estimators": [100, 200],
    "max_depth": [3, 5, 7],
    "learning_rate": [0.05, 0.1],
    "subsample": [0.8],
    "colsample_bytree": [0.8]
}

best_model, best_params = trainer.grid_search(
    X_train, y_train, "xgboost",
    param_grid=params,
    cv=3  # Menos folds
)
```

---

## Validação e Testes

### Checklist de Validação:

```python
# 1. Verificar que split é temporal
assert X_train["ano"].max() < X_test["ano"].min()

# 2. Verificar ausência de features com leakage
leakage_features = [
    "eficiencia", "valor_por_ton", "razao_colheita", "perda_area",
    "taxa_aproveitamento", "produtividade_ton_ha", "valor_por_ha",
    "rendimento_tendencia"
]
assert not any(f in X_train.columns for f in leakage_features)

# 3. Verificar VIF
from src.features.multicollinearity import quick_vif_check
vif_df = quick_vif_check(X_train)
assert (vif_df["vif"] <= 10).all() or len(vif_df[vif_df["vif"] > 10]) <= 2
```

---

## Suporte e Contribuição

### Reportar Problemas:
- Verificar documentação primeiro
- Criar issue com exemplo reproduzível
- Incluir versão do código e ambiente

### Contribuir:
- Seguir estilo de código existente
- Adicionar testes para novas funcionalidades
- Atualizar documentação correspondente

---

## Versionamento

### v2.0.0 (2025-12-14)
- ✅ Remoção de data leakage
- ✅ Time series split
- ✅ XGBoost otimizado
- ✅ Módulo VIF

### v1.0.0 (Anterior)
- ❌ Features com leakage
- ❌ Split aleatório
- ❌ XGBoost sem otimização
- ❌ Sem detecção de multicolinearidade

---

## Licença

Este projeto é parte do portfólio de Ciência de Dados.

---

**Última atualização:** 2025-12-14
**Mantenedor:** Time de Ciência de Dados
**Versão da Documentação:** 2.0
