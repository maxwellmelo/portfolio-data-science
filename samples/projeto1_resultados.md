# Projeto 1 - ETL IBGE: Resultados da Execução

## Execução Realizada
**Data**: 14/12/2025

## Dados Extraídos

### Regiões (5 registros)
| ID | Sigla | Nome |
|----|-------|------|
| 1 | N | Norte |
| 2 | NE | Nordeste |
| 3 | SE | Sudeste |
| 4 | S | Sul |
| 5 | CO | Centro-Oeste |

### Estados (27 registros)
| UF | Nome | Região |
|----|------|--------|
| RO | Rondônia | Norte |
| AC | Acre | Norte |
| AM | Amazonas | Norte |
| RR | Roraima | Norte |
| PA | Pará | Norte |
| AP | Amapá | Norte |
| TO | Tocantins | Norte |
| MA | Maranhão | Nordeste |
| PI | Piauí | Nordeste |
| CE | Ceará | Nordeste |
| ... | ... | ... |

### Municípios (5.571 registros)
Exemplo dos primeiros registros:

| ID | Nome | UF | Microrregião | Mesorregião |
|----|------|-----|--------------|-------------|
| 1100015 | Alta Floresta D'Oeste | RO | Cacoal | Leste Rondoniense |
| 1100023 | Ariquemes | RO | Ariquemes | Leste Rondoniense |
| 1100031 | Cabixi | RO | Colorado Do Oeste | Leste Rondoniense |

## Métricas de Execução

| Métrica | Valor |
|---------|-------|
| Total de registros | 5.603 |
| Tempo de execução | 1.36s |
| Arquivos gerados | 3 |
| Fonte | API IBGE v1 |

## Arquivos Gerados
- `data/processed/regioes.csv` - 5 registros
- `data/processed/estados.csv` - 27 registros
- `data/processed/municipios.csv` - 5.571 registros
