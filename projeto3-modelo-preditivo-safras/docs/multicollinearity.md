# Documentação - multicollinearity.py

## Data: 2025-12-14
## Módulo: src/features/multicollinearity.py (NOVO)

---

## Resumo

Novo módulo para **detecção e tratamento de multicolinearidade** usando Variance Inflation Factor (VIF). Identifica features altamente correlacionadas que podem prejudicar modelos lineares e inflar variância dos coeficientes.

---

## O que é Multicolinearidade?

### Definição
Multicolinearidade ocorre quando duas ou mais features independentes são altamente correlacionadas entre si, tornando difícil determinar o efeito individual de cada uma sobre a variável alvo.

### Problemas Causados

1. **Coeficientes Instáveis** (Modelos Lineares)
   - Pequenas mudanças nos dados causam grandes mudanças nos coeficientes
   - Coeficientes com sinais errados (positivo quando deveria ser negativo)
   - Intervalos de confiança muito largos

2. **Interpretabilidade Reduzida**
   - Difícil determinar importância real de cada feature
   - Coeficientes não refletem relacionamento verdadeiro

3. **Overfitting**
   - Modelo se ajusta a padrões espúrios na correlação
   - Generalização prejudicada

---

## Variance Inflation Factor (VIF)

### O que é VIF?

VIF mede o quanto a **variância** de um coeficiente de regressão é **inflada** devido à correlação com outras features.

### Fórmula

```
VIF_i = 1 / (1 - R²_i)
```

Onde:
- **VIF_i**: VIF da feature i
- **R²_i**: R² da regressão da feature i contra todas as outras features

### Interpretação

| VIF | Interpretação | Ação |
|-----|---------------|------|
| VIF = 1 | Sem correlação | ✅ OK |
| VIF < 5 | Multicolinearidade baixa | ✅ OK |
| VIF 5-10 | Multicolinearidade moderada | ⚠️ Atenção |
| VIF > 10 | Multicolinearidade alta | ❌ Remover |
| VIF > 20 | Multicolinearidade severa | ❌❌ Remover urgente |

### Exemplo Intuitivo

```python
# Feature sem correlação: VIF = 1
area_plantada (independente de outras features)
VIF = 1.2

# Feature moderadamente correlacionada: VIF = 5-10
area_colhida vs area_plantada (R² = 0.80)
VIF = 1 / (1 - 0.80) = 5.0

# Feature altamente correlacionada: VIF > 10
producao_ton vs rendimento_kg_ha (R² = 0.95)
VIF = 1 / (1 - 0.95) = 20.0  ❌ REMOVER
```

---

## Classes e Funções

### Classe Principal: `VIFAnalyzer`

```python
class VIFAnalyzer:
    """
    Analisador de multicolinearidade usando VIF.

    Attributes:
        threshold: Limite superior de VIF (default: 10.0)
        warning_threshold: Limite de aviso (default: 5.0)
        vif_results: DataFrame com últimos resultados calculados
    """

    def __init__(self, threshold: float = 10.0, warning_threshold: float = 5.0):
        ...

    def calculate_vif(self, df: pd.DataFrame, features: Optional[List[str]] = None) -> pd.DataFrame:
        """Calcula VIF para todas features numéricas."""
        ...

    def get_high_vif_features(self, vif_df: Optional[pd.DataFrame] = None) -> List[str]:
        """Retorna lista de features com VIF > threshold."""
        ...

    def remove_high_vif_features(
        self, df: pd.DataFrame, max_iterations: int = 10
    ) -> Tuple[pd.DataFrame, List[str]]:
        """Remove iterativamente features com VIF alto."""
        ...

    def get_correlation_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula matriz de correlação."""
        ...

    def get_highly_correlated_pairs(
        self, df: pd.DataFrame, threshold: float = 0.8
    ) -> pd.DataFrame:
        """Identifica pares de features com correlação > threshold."""
        ...

    def generate_report(self) -> Dict[str, any]:
        """Gera relatório completo de multicolinearidade."""
        ...
```

---

## Exemplos de Uso

### 1. Análise Básica de VIF

```python
from src.features.multicollinearity import VIFAnalyzer

# Criar analisador
analyzer = VIFAnalyzer(threshold=10.0, warning_threshold=5.0)

# Calcular VIF
vif_df = analyzer.calculate_vif(X_train)

print(vif_df)
# Output:
#                 feature     vif    status  severity
# 0      producao_ton_lag1  45.23   REMOVER      high
# 1        area_colhida_ha  12.56   REMOVER      high
# 2        area_plantada_ha   8.90   ATENÇÃO  moderate
# 3                    ano   2.15        OK       low
# 4  rendimento_kg_ha_lag1   1.89        OK       low
```

### 2. Função Rápida (Quick Check)

```python
from src.features.multicollinearity import quick_vif_check

# Check rápido com logging automático
vif_df = quick_vif_check(X_train, threshold=10.0)

# Se houver problemas, automaticamente loga:
# WARNING: 2 features com VIF > 10.0:
#            feature     vif
#    producao_ton_lag1  45.23
#      area_colhida_ha  12.56
```

### 3. Remoção Automática

```python
from src.features.multicollinearity import auto_remove_multicollinearity

# Remove automaticamente features problemáticas
X_clean, report = auto_remove_multicollinearity(
    X_train,
    threshold=10.0,
    max_iterations=10
)

print(f"Features removidas: {report['removed_features']}")
print(f"VIF médio antes: {report['mean_vif']:.2f}")

# Output:
# Iteração 1: Removendo 'producao_ton_lag1' (VIF = 45.23)
# Iteração 2: Removendo 'area_colhida_ha' (VIF = 12.56)
# Convergência alcançada após 2 iterações
# Features removidas: ['producao_ton_lag1', 'area_colhida_ha']
```

### 4. Análise de Pares Correlacionados

```python
analyzer = VIFAnalyzer()

# Identificar pares altamente correlacionados
corr_pairs = analyzer.get_highly_correlated_pairs(
    X_train,
    threshold=0.8
)

print(corr_pairs)
# Output:
#           feature_1          feature_2  correlation  abs_correlation
# 0   area_plantada_ha    area_colhida_ha         0.92             0.92
# 1      producao_ton  rendimento_kg_ha_lag1      -0.85             0.85
# 2               ano   area_plantada_ha_lag1       0.81             0.81
```

### 5. Remoção Iterativa Manual

```python
analyzer = VIFAnalyzer(threshold=10.0)

# Remover iterativamente
X_clean, removed_features = analyzer.remove_high_vif_features(
    X_train,
    max_iterations=5
)

print(f"Removidas: {removed_features}")
print(f"Features restantes: {list(X_clean.columns)}")

# Validar resultado
final_vif = analyzer.calculate_vif(X_clean)
assert (final_vif["vif"] <= 10.0).all(), "Ainda há features com VIF alto!"
```

### 6. Relatório Completo

```python
analyzer = VIFAnalyzer()
vif_df = analyzer.calculate_vif(X_train)

report = analyzer.generate_report()

print(f"Total features: {report['total_features']}")
print(f"Alta multicolinearidade: {report['high_vif_count']}")
print(f"Moderada: {report['moderate_vif_count']}")
print(f"Baixa: {report['low_vif_count']}")
print(f"VIF médio: {report['mean_vif']:.2f}")
print(f"VIF máximo: {report['max_vif']:.2f} ({report['max_vif_feature']})")
print(f"Features para remover: {report['features_to_remove']}")

# Output:
# Total features: 15
# Alta multicolinearidade: 2
# Moderada: 3
# Baixa: 10
# VIF médio: 6.34
# VIF máximo: 45.23 (producao_ton_lag1)
# Features para remover: ['producao_ton_lag1', 'area_colhida_ha']
```

---

## Integração com DataLoader

### Uso Automático no Pipeline

```python
from src.data.data_loader import DataLoader

loader = DataLoader()
df = loader.load_data()

# VIF check automático durante preparação
X_train, X_test, y_train, y_test = loader.prepare_for_modeling(
    df,
    check_multicollinearity=True,   # Verifica VIF
    vif_threshold=10.0,              # Alerta se VIF > 10
    remove_high_vif=False            # Apenas alerta (não remove)
)

# Se quiser remoção automática:
X_train, X_test, y_train, y_test = loader.prepare_for_modeling(
    df,
    check_multicollinearity=True,
    remove_high_vif=True  # Remove automaticamente
)
```

---

## Algoritmo de Remoção Iterativa

### Como Funciona

```python
def remove_high_vif_features(df, threshold=10, max_iterations=10):
    """
    1. Calcular VIF para todas features
    2. Se todas VIF <= threshold: PARAR ✅
    3. Identificar feature com MAIOR VIF
    4. REMOVER essa feature
    5. Voltar para passo 1

    Repete até convergência ou max_iterations
    """
```

### Exemplo de Execução

```
Iteração 0: VIF máximo = 45.2 (producao_ton_lag1)
  ↓ REMOVE producao_ton_lag1

Iteração 1: VIF máximo = 12.6 (area_colhida_ha)
  ↓ REMOVE area_colhida_ha

Iteração 2: VIF máximo = 8.9 (area_plantada_ha)
  ✅ CONVERGÊNCIA (8.9 <= 10.0)

Total removidas: 2 features
Features restantes: 13
```

### Por quê Iterativo?

Remoção de uma feature **muda o VIF das outras**:

```
ANTES da remoção:
- producao_ton_lag1: VIF = 45.2
- area_colhida_ha: VIF = 12.6  (correlacionada com producao_ton)
- area_plantada_ha: VIF = 8.9

DEPOIS de remover producao_ton_lag1:
- area_colhida_ha: VIF = 6.3  ✅ (reduziu!)
- area_plantada_ha: VIF = 4.2  ✅ (reduziu!)
```

---

## Quando Usar VIF?

### ✅ Use VIF Quando:

1. **Modelos Lineares**
   - Ridge, Lasso, ElasticNet
   - Regressão Linear
   - Logística

2. **Interpretabilidade é Importante**
   - Precisa entender coeficientes
   - Modelo usado para inferência (não só predição)

3. **Features Derivadas/Engenheiradas**
   - Muitas features criadas manualmente
   - Interações e transformações

4. **Coeficientes Instáveis**
   - Coeficientes mudam muito entre treinos
   - Sinais dos coeficientes não fazem sentido

### ❌ VIF é Menos Importante Para:

1. **Tree-Based Models**
   - Random Forest
   - Gradient Boosting
   - XGBoost
   - *Motivo:* Árvores lidam bem com correlação

2. **Redes Neurais**
   - Deep Learning
   - *Motivo:* Regularização implícita

3. **Apenas Predição**
   - Não se importa com interpretabilidade
   - Só quer melhor R² ou RMSE

---

## Comparação: VIF vs Correlação

### Correlação Simples (Pairwise)

```python
# Detecta apenas correlação DIRETA entre 2 features
corr = df[["area_plantada", "area_colhida"]].corr()
# Problema: Não detecta correlação INDIRETA

# Exemplo:
# A correlaciona com B: r = 0.3
# B correlaciona com C: r = 0.3
# Mas A+B predizem perfeitamente C!
# Correlação pairwise não detecta isso
```

### VIF (Multicolinearidade Completa)

```python
# Detecta correlação DIRETA e INDIRETA
# Regride cada feature contra TODAS as outras
# Captura relações lineares complexas

vif = calculate_vif(df)
# VIF alto mesmo se correlações pairwise são baixas
```

### Quando Usar Cada Um

| Situação | Use | Motivo |
|----------|-----|--------|
| Análise exploratória inicial | Correlação | Rápido e visual (heatmap) |
| Feature engineering | Correlação | Identificar features redundantes |
| Preparação para modelo linear | **VIF** | Captura multicolinearidade completa |
| Diagnóstico de coeficientes estranhos | **VIF** | Identifica causa raiz |

---

## Performance e Complexidade

### Complexidade Computacional

```python
# Para n features:
# - Correlação: O(n²)
# - VIF: O(n³)  [precisa regressão para cada feature]

# Exemplo de tempo:
n_features = 50
correlation_time = 0.1s
vif_time = 2.5s  # Mais lento, mas aceitável
```

### Otimizações Implementadas

1. **Remoção de features constantes** (VIF infinito)
2. **Cálculo vetorizado** (statsmodels)
3. **Cache de resultados** (atributo `vif_results`)
4. **Processamento apenas de numéricas**

---

## Troubleshooting

### Problema: VIF Infinito

```python
# Causa: Feature constante ou combinação linear perfeita
# Solução: Remover features constantes automaticamente

# Implementado:
constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
df = df.drop(columns=constant_cols)
```

### Problema: Remoção Não Converge

```python
# Causa: Threshold muito rigoroso ou features intrinsecamente correlacionadas
# Solução: Aumentar threshold ou max_iterations

analyzer = VIFAnalyzer(threshold=15.0)  # Menos rigoroso
X_clean, removed = analyzer.remove_high_vif_features(
    X, max_iterations=20  # Mais iterações
)
```

### Problema: VIF Alto Mas Correlação Baixa

```python
# Possível causa: Correlação indireta (A+B predizem C)
# Solução: Analisar matriz de correlação E VIF

# Ver pares correlacionados
corr_pairs = analyzer.get_highly_correlated_pairs(df, threshold=0.7)

# Ver VIF
vif_df = analyzer.calculate_vif(df)

# Comparar ambos para entender estrutura
```

---

## Checklist de Uso

- [ ] Calculado VIF para features numéricas
- [ ] Identificadas features com VIF > 10
- [ ] Analisados pares altamente correlacionados
- [ ] Decidido entre remover automaticamente ou manualmente
- [ ] Validado que remoção melhorou estabilidade dos coeficientes
- [ ] Re-treinado modelos após remoção
- [ ] Documentado features removidas e justificativa

---

## Próximos Passos

1. **Implementar em pipeline de produção**
2. **Adicionar visualização de VIF** (barplot)
3. **Integrar com feature importance** (combinar VIF + importância)
4. **Automatizar threshold selection** (validação cruzada)
5. **Adicionar testes unitários** para todas as funções

---

## Referências

- **VIF:** Belsley, Kuh, and Welsch (1980) "Regression Diagnostics: Identifying Influential Data and Sources of Collinearity"
- **Multicollinearity:** Kutner et al. (2004) "Applied Linear Statistical Models"
- **Statsmodels VIF:** https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
- **Best Practices:** O'Brien (2007) "A Caution Regarding Rules of Thumb for Variance Inflation Factors"
