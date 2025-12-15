# Integração de Dados Reais do IBGE

## Resumo das Alterações

Esta documentação descreve a integração de dados reais do IBGE na API do Projeto 4.

## Arquivos Modificados/Criados

### 1. `src/extractors/ibge_extractor.py` (NOVO)
Extrator de dados reais da API SIDRA do IBGE.

**Funcionalidades:**
- Extração de população estimada (Tabela 6579)
- Extração de PIB municipal (Tabela 5938)
- Processamento em lotes de 50 municípios
- Retry automático com backoff exponencial
- Variáveis solicitadas uma por vez (limitação da API)

**Dados Extraídos:**
- População: 896 registros (2019-2024, 224 municípios)
- PIB: 448 registros (2020-2021, 224 municípios)

### 2. `src/api/data_loader.py` (NOVO)
Gerenciador de fontes de dados.

**Antes:** API usava apenas dados sintéticos do `SyntheticDataGenerator`.

**Depois:**
- Carrega dados reais primeiro (se disponíveis)
- Dados reais sobrescrevem dados sintéticos
- Calcula PIB per capita automaticamente: `(pib_total_mil_reais * 1000) / populacao_estimada`
- Indica fonte dos dados (IBGE vs Sintético)

```python
class DataLoader:
    def load_all(self, generator=None) -> Dict[str, pd.DataFrame]:
        # 1. Carrega dados reais primeiro
        real_data = self.load_real_data()
        # 2. Carrega dados sintéticos
        synthetic_data = generator.generate_all() if generator else {}
        # 3. Combina (reais sobrescrevem sintéticos)
        self._cache = {**synthetic_data, **real_data}
        return self._cache
```

### 3. `src/api/main.py` (MODIFICADO)
Endpoints atualizados para indicar fonte dos dados.

**Novo endpoint:** `GET /fontes/status`
```json
{
    "resumo": {
        "total_datasets": 7,
        "datasets_reais": 2,
        "datasets_sinteticos": 5
    },
    "datasets": { ... }
}
```

**Endpoint atualizado:** `GET /economia/pib`
```json
{
    "dados_reais": true,
    "fonte": "IBGE - Sistema de Contas Regionais",
    "total_registros": 2,
    "data": [ ... ]
}
```

**Endpoint atualizado:** `GET /indicadores/{municipio_id}`
```json
{
    "fontes": {
        "economia": "IBGE - Dados Reais",
        "saude": "Dados Sintéticos"
    },
    "economia": {
        "dados_reais": true,
        "pib_total_mil_reais": 23895231.0
    }
}
```

## Dados Reais Disponíveis

### PIB Municipal (economia_pib)
| Campo | Descrição | Fonte |
|-------|-----------|-------|
| municipio_id | Código IBGE | IBGE |
| municipio_nome | Nome do município | IBGE |
| ano | Ano de referência | IBGE |
| pib_total_mil_reais | PIB total em mil R$ | IBGE SIDRA |
| populacao_estimada | População estimada | IBGE SIDRA |
| pib_per_capita | PIB per capita (calculado) | Derivado |

**Anos disponíveis:** 2020, 2021

### População (populacao)
| Campo | Descrição | Fonte |
|-------|-----------|-------|
| municipio_id | Código IBGE | IBGE |
| municipio_nome | Nome do município | IBGE |
| ano | Ano de referência | IBGE |
| populacao_estimada | População estimada | IBGE SIDRA |

**Anos disponíveis:** 2019, 2020, 2021, 2024

## Exemplo: Teresina

**PIB 2021 (dados reais do IBGE):**
- PIB Total: R$ 23.895.231 mil (R$ 23,9 bilhões)
- População: 871.126 habitantes
- PIB per capita: R$ 27.430,28

## Vantagens da Integração

1. **Transparência:** API indica claramente quais dados são reais vs sintéticos
2. **Confiabilidade:** Dados econômicos oficiais do IBGE
3. **Flexibilidade:** Fallback para dados sintéticos quando reais não disponíveis
4. **Atualização:** Fácil atualizar dados re-executando `ibge_extractor.py`

## Como Atualizar os Dados

```bash
cd projeto4-integracao-multissetorial
python src/extractors/ibge_extractor.py
```

Os dados serão salvos em:
- `data/real/populacao.csv`
- `data/real/pib_municipal.csv`
- `data/real/economia_completo.csv`
