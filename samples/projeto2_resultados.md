# Projeto 2 - Dashboard Ambiental: Resultados da Execução

## Execução Realizada
**Data**: 14/12/2025

## Dados Carregados

### Resumo do Dataset
| Métrica | Valor |
|---------|-------|
| Total de registros | 416 |
| Período | 2000-2025 |
| Biomas cobertos | 6 |
| Estados cobertos | 27 |

### Biomas Monitorados
- Amazônia
- Cerrado
- Mata Atlântica
- Caatinga
- Pampa
- Pantanal

### Dados de Desmatamento (Amostra)
| Ano | Bioma | Estado | Área Desmatada (km²) |
|-----|-------|--------|---------------------|
| 2023 | Cerrado | PI | 1.247 |
| 2023 | Cerrado | MA | 1.089 |
| 2023 | Cerrado | TO | 987 |
| 2024 | Cerrado | PI | 1.350 |

### Destaques do Piauí
- **Posição**: 3º maior desmatador do Cerrado em 2025
- **Área total desmatada (2025)**: 1.350 km²
- **Tendência**: Redução de 11,49% em relação ao ano anterior

## Dashboard
O dashboard Streamlit oferece:
- 5 abas especializadas
- Mapas interativos (Folium)
- Gráficos dinâmicos (Plotly)
- Filtros por bioma, estado e período
- KPIs em tempo real

## Como Executar
```bash
cd projeto2-dashboard-ambiental
streamlit run app.py
# Acesse: http://localhost:8501
```
