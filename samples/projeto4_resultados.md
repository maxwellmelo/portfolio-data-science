# Projeto 4 - Integração Multissetorial: Resultados da Execução

## Execução Realizada
**Data**: 14/12/2025

## Dados Gerados

### Resumo Geral
| Dataset | Registros |
|---------|-----------|
| Saúde - Mortalidade | 5.000 |
| Saúde - Nascimentos | 3.000 |
| Educação - Escolas | 500 |
| Educação - IDEB | 200 |
| Economia - PIB | 60 |
| Assistência - CadÚnico | 10.000 |
| **Total** | **18.760** |

### Cobertura Geográfica
- **Estado**: Piauí (PI)
- **Municípios**: 10 principais
  - Teresina
  - Parnaíba
  - Picos
  - Piripiri
  - Floriano
  - Campo Maior
  - Barras
  - Corrente
  - Oeiras
  - Esperantina

### Período dos Dados
- **Início**: 2018
- **Fim**: 2023

## Exemplos de Dados

### Mortalidade (Saúde)
| ID | Data | Município | Idade | Causa |
|----|------|-----------|-------|-------|
| bdd640fb | 2018-12-08 | Parnaíba | 74 | AVC |
| 23b8c1e9 | 2021-01-07 | Oeiras | 62 | Infarto |
| bd9c66b3 | 2021-04-26 | Esperantina | 77 | Hipertensão |

### PIB Municipal (Economia)
| Município | Ano | PIB Total (R$ mil) | PIB per Capita |
|-----------|-----|--------------------|----------------|
| Teresina | 2018 | 26.374.048 | R$ 30.525 |
| Teresina | 2019 | 26.236.381 | R$ 30.065 |
| Teresina | 2020 | 25.987.727 | R$ 29.488 |
| Teresina | 2021 | 26.470.089 | R$ 29.744 |

## API REST

### Endpoints Disponíveis
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações da API |
| GET | `/health` | Status de saúde |
| GET | `/fontes` | Lista fontes de dados |
| GET | `/municipios` | Lista municípios |
| GET | `/saude/mortalidade` | Dados de mortalidade |
| GET | `/saude/nascimentos` | Dados de nascimentos |
| GET | `/educacao/escolas` | Dados de escolas |
| GET | `/educacao/ideb` | Dados do IDEB |
| GET | `/economia/pib` | PIB municipal |
| GET | `/assistencia/cadunico` | Dados do CadÚnico |
| GET | `/indicadores/{id}` | Indicadores consolidados |

### Exemplo de Uso
```bash
# Iniciar API
python main.py api

# Consultar PIB de Teresina
curl "http://localhost:8000/economia/pib?municipio_id=2211001"

# Indicadores consolidados
curl "http://localhost:8000/indicadores/2211001?ano=2023"
```

## Documentação
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
