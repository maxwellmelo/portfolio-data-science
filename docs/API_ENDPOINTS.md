# Documentação dos Endpoints da API IBGE

## Visão Geral

Este documento detalha todos os endpoints da API do IBGE que serão utilizados no pipeline ETL.

**Base URL:** `https://servicodados.ibge.gov.br/api`

**Versões:**
- v1: Localidades, Projeções, Pesquisas
- v3: Agregados (SIDRA)

**Formato de Resposta:** JSON
**Autenticação:** Não requerida (API pública)
**Rate Limiting:** Recomendado 0.5-1s entre requisições

---

## Índice

1. [API de Localidades (v1)](#1-api-de-localidades-v1)
2. [API de Agregados - SIDRA (v3)](#2-api-de-agregados---sidra-v3)
3. [API de Projeções (v1)](#3-api-de-projeções-v1)
4. [Códigos e Tabelas de Referência](#4-códigos-e-tabelas-de-referência)
5. [Exemplos de Uso](#5-exemplos-de-uso)
6. [Tratamento de Erros](#6-tratamento-de-erros)

---

## 1. API de Localidades (v1)

Base URL: `https://servicodados.ibge.gov.br/api/v1/localidades`

### 1.1 Listar Regiões

**Endpoint:** `GET /localidades/regioes`

**Descrição:** Retorna as 5 regiões geográficas do Brasil.

**Parâmetros:** Nenhum

**Resposta:**
```json
[
  {
    "id": 1,
    "sigla": "N",
    "nome": "Norte"
  },
  {
    "id": 2,
    "sigla": "NE",
    "nome": "Nordeste"
  },
  {
    "id": 3,
    "sigla": "SE",
    "nome": "Sudeste"
  },
  {
    "id": 4,
    "sigla": "S",
    "nome": "Sul"
  },
  {
    "id": 5,
    "sigla": "CO",
    "nome": "Centro-Oeste"
  }
]
```

**Campos:**
- `id`: Código da região (1-5)
- `sigla`: Sigla da região
- `nome`: Nome completo da região

---

### 1.2 Listar Estados

**Endpoint:** `GET /localidades/estados`

**Descrição:** Retorna todos os estados e o Distrito Federal (27 UFs).

**Parâmetros:**
- `orderBy` (opcional): Campo para ordenação (`id` ou `nome`)

**Exemplo de Requisição:**
```
GET /localidades/estados?orderBy=nome
```

**Resposta:**
```json
[
  {
    "id": 12,
    "sigla": "AC",
    "nome": "Acre",
    "regiao": {
      "id": 1,
      "sigla": "N",
      "nome": "Norte"
    }
  },
  {
    "id": 27,
    "sigla": "AL",
    "nome": "Alagoas",
    "regiao": {
      "id": 2,
      "sigla": "NE",
      "nome": "Nordeste"
    }
  }
  // ... demais estados
]
```

**Campos:**
- `id`: Código IBGE do estado (2 dígitos)
- `sigla`: Sigla da UF (2 letras)
- `nome`: Nome completo do estado
- `regiao`: Objeto com dados da região

---

### 1.3 Obter Estado Específico

**Endpoint:** `GET /localidades/estados/{UF}`

**Descrição:** Retorna dados de um estado específico.

**Parâmetros de Path:**
- `{UF}`: Código IBGE (ex: 35) ou sigla (ex: SP)

**Exemplo:**
```
GET /localidades/estados/SP
```

**Resposta:**
```json
{
  "id": 35,
  "sigla": "SP",
  "nome": "São Paulo",
  "regiao": {
    "id": 3,
    "sigla": "SE",
    "nome": "Sudeste"
  }
}
```

---

### 1.4 Listar Municípios

**Endpoint:** `GET /localidades/municipios`

**Descrição:** Retorna todos os municípios do Brasil (~5.570).

**Parâmetros:**
- `orderBy` (opcional): `id` ou `nome`

**Exemplo:**
```
GET /localidades/municipios?orderBy=nome
```

**Resposta (parcial):**
```json
[
  {
    "id": 3550308,
    "nome": "São Paulo",
    "microrregiao": {
      "id": 35061,
      "nome": "São Paulo",
      "mesorregiao": {
        "id": 3515,
        "nome": "Metropolitana de São Paulo",
        "UF": {
          "id": 35,
          "sigla": "SP",
          "nome": "São Paulo",
          "regiao": {
            "id": 3,
            "sigla": "SE",
            "nome": "Sudeste"
          }
        }
      }
    },
    "regiao-imediata": {
      "id": 350001,
      "nome": "São Paulo",
      "regiao-intermediaria": {
        "id": 3501,
        "nome": "São Paulo",
        "UF": {
          "id": 35,
          "sigla": "SP",
          "nome": "São Paulo",
          "regiao": {
            "id": 3,
            "sigla": "SE",
            "nome": "Sudeste"
          }
        }
      }
    }
  }
  // ... demais municípios
]
```

**Campos:**
- `id`: Código IBGE do município (7 dígitos)
- `nome`: Nome do município
- `microrregiao`: Dados da microrregião
- `mesorregiao`: Dados da mesorregião (dentro de microrregiao)
- `regiao-imediata`: Nova divisão regional
- `regiao-intermediaria`: Nova divisão regional
- `UF`: Dados do estado

---

### 1.5 Listar Municípios por Estado

**Endpoint:** `GET /localidades/estados/{UF}/municipios`

**Descrição:** Retorna municípios de um estado específico.

**Parâmetros de Path:**
- `{UF}`: Código IBGE ou sigla do estado

**Exemplo:**
```
GET /localidades/estados/SP/municipios
```

**Resposta:** Array de municípios (formato igual ao anterior)

---

### 1.6 Obter Município Específico

**Endpoint:** `GET /localidades/municipios/{municipio}`

**Descrição:** Retorna dados de um município específico.

**Parâmetros de Path:**
- `{municipio}`: Código IBGE do município (7 dígitos)

**Exemplo:**
```
GET /localidades/municipios/3550308
```

**Resposta:** Objeto do município (formato igual ao anterior)

---

## 2. API de Agregados - SIDRA (v3)

Base URL: `https://servicodados.ibge.gov.br/api/v3/agregados`

**Importante:** Esta API retorna dados de pesquisas estatísticas do IBGE.

### 2.1 Estrutura Geral de Agregados

**Endpoint Base:** `GET /agregados/{agregado}/periodos/{periodo}/variaveis/{variavel}`

**Query Parameters:**
- `localidades`: Nível geográfico e IDs
  - Formato: `{nivel}[{ids}]`
  - Níveis: `N1` (Brasil), `N2` (Região), `N3` (Estado), `N6` (Município)
  - `all` para todos: `N6[all]` (todos os municípios)

**Exemplo Genérico:**
```
GET /agregados/5938/periodos/2021/variaveis/37?localidades=N6[all]
```

---

### 2.2 Agregado 200 - População dos Censos

**ID:** 200
**Descrição:** População residente por situação do domicílio e sexo
**Fonte:** Censos Demográficos
**Anos Disponíveis:** 1970, 1980, 1991, 2000, 2010

**Variáveis:**
- `93`: População residente

**Endpoint:**
```
GET /agregados/200/periodos/2010/variaveis/93?localidades=N6[all]
```

**Resposta (simplificada):**
```json
[
  {
    "id": "200",
    "variavel": "93",
    "unidade": "Pessoas",
    "resultados": [
      {
        "localidade": {
          "id": "3550308",
          "nome": "São Paulo - SP",
          "nivel": {
            "id": "N6",
            "nome": "Município"
          }
        },
        "series": [
          {
            "serie": {
              "2010": "11253503"
            }
          }
        ]
      }
    ]
  }
]
```

---

### 2.3 Agregado 6579 - Estimativas de População

**ID:** 6579
**Descrição:** Estimativas de população residente
**Fonte:** Estimativas Populacionais
**Anos:** 2001 em diante (anual)

**Variáveis:**
- `9324`: População residente estimada

**Endpoint:**
```
GET /agregados/6579/periodos/2022/variaveis/9324?localidades=N6[all]
```

**Exemplo de Resposta:**
```json
[
  {
    "id": "6579",
    "variavel": "9324",
    "unidade": "Pessoas",
    "resultados": [
      {
        "localidade": {
          "id": "3550308",
          "nome": "São Paulo - SP"
        },
        "series": [
          {
            "serie": {
              "2022": "11451245"
            }
          }
        ]
      }
    ]
  }
]
```

---

### 2.4 Agregado 5938 - PIB Municipal

**ID:** 5938
**Descrição:** Produto Interno Bruto dos Municípios
**Fonte:** Contas Nacionais
**Anos:** 2002 em diante

**Variáveis Principais:**
- `37`: PIB a preços correntes (mil Reais)
- `513`: Valor adicionado bruto da Agropecuária
- `514`: Valor adicionado bruto da Indústria
- `515`: Valor adicionado bruto dos Serviços
- `516`: Impostos sobre produtos líquidos de subsídios

**Endpoint para PIB Total:**
```
GET /agregados/5938/periodos/2021/variaveis/37?localidades=N6[all]
```

**Endpoint para Múltiplas Variáveis:**
```
GET /agregados/5938/periodos/2021/variaveis/37|513|514|515|516?localidades=N6[all]
```

**Resposta (PIB Total):**
```json
[
  {
    "id": "5938",
    "variavel": "37",
    "unidade": "Mil Reais",
    "resultados": [
      {
        "localidade": {
          "id": "3550308",
          "nome": "São Paulo - SP"
        },
        "series": [
          {
            "serie": {
              "2021": "763634978"
            }
          }
        ]
      }
    ]
  }
]
```

**Resposta (Múltiplas Variáveis):**
```json
[
  {
    "id": "5938",
    "variavel": "37",
    "unidade": "Mil Reais",
    "resultados": [
      {
        "localidade": {
          "id": "3550308",
          "nome": "São Paulo - SP"
        },
        "series": [
          {
            "serie": {
              "2021": "763634978"
            }
          }
        ]
      }
    ]
  },
  {
    "id": "5938",
    "variavel": "513",
    "unidade": "Mil Reais",
    "resultados": [
      {
        "localidade": {
          "id": "3550308",
          "nome": "São Paulo - SP"
        },
        "series": [
          {
            "serie": {
              "2021": "382156"
            }
          }
        ]
      }
    ]
  }
  // ... demais variáveis
]
```

---

### 2.5 Agregado 37 - PIB per capita

**ID:** 37
**Descrição:** PIB per capita
**Anos:** 2002 em diante

**Variáveis:**
- `47`: PIB per capita (Reais)

**Endpoint:**
```
GET /agregados/37/periodos/2021/variaveis/47?localidades=N6[all]
```

---

### 2.6 Outros Agregados Úteis

| ID | Descrição | Variáveis Principais |
|----|-----------|---------------------|
| 793 | Índice de Gini | 933 (Índice de Gini) |
| 1171 | Renda domiciliar per capita | 897 (Valor médio) |
| 7358 | IDH Municipal | 120 (IDHM) |

**Nota:** Nem todos os indicadores estão disponíveis para todos os municípios e anos.

---

## 3. API de Projeções (v1)

Base URL: `https://servicodados.ibge.gov.br/api/v1/projecoes`

### 3.1 Projeção Populacional

**Endpoint:** `GET /projecoes/populacao/{localidade}`

**Descrição:** Retorna projeções de população

**Parâmetros de Path:**
- `{localidade}`:
  - `BR` ou `0`: Brasil
  - `1-5`: Grandes Regiões
  - `11-53`: Estados (código IBGE)

**Exemplo Brasil:**
```
GET /projecoes/populacao/BR
```

**Exemplo Estado:**
```
GET /projecoes/populacao/35
```

**Resposta:**
```json
{
  "localidade": "Brasil",
  "horario": "2025-12-14T10:30:00",
  "projecao": {
    "populacao": 215313498,
    "periodoMedio": "2025-07-01"
  }
}
```

**Nota:** Projeções estão disponíveis apenas para Brasil, Regiões e Estados, não para municípios individuais.

---

## 4. Códigos e Tabelas de Referência

### 4.1 Códigos IBGE

**Estrutura do Código de Município (7 dígitos):**
- 2 primeiros dígitos: Código do estado
- 5 últimos dígitos: Código sequencial do município

**Exemplos:**
- `3550308`: São Paulo (35 = SP, 50308 = São Paulo)
- `3304557`: Rio de Janeiro (33 = RJ, 04557 = Rio de Janeiro)
- `5300108`: Brasília (53 = DF, 00108 = Brasília)

### 4.2 Níveis Geográficos

| Código | Descrição | Exemplo |
|--------|-----------|---------|
| N1 | Brasil | `N1[1]` ou `N1[all]` |
| N2 | Grande Região | `N2[3]` (Sudeste) |
| N3 | Unidade da Federação | `N3[35]` (SP) |
| N6 | Município | `N6[3550308]` (São Paulo) |

### 4.3 Tabelas SIDRA Principais

| Tabela | Descrição | URL |
|--------|-----------|-----|
| 200 | População dos Censos | [Tabela 200](https://sidra.ibge.gov.br/tabela/200) |
| 6579 | Estimativas de População | [Tabela 6579](https://sidra.ibge.gov.br/tabela/6579) |
| 5938 | PIB Municipal | [Tabela 5938](https://sidra.ibge.gov.br/tabela/5938) |
| 37 | PIB per capita | [Tabela 37](https://sidra.ibge.gov.br/tabela/37) |

---

## 5. Exemplos de Uso

### 5.1 Obter População de Todos os Municípios (2022)

```python
import requests

url = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2022/variaveis/9324"
params = {"localidades": "N6[all]"}

response = requests.get(url, params=params)
data = response.json()

# Processar resultados
for resultado in data[0]['resultados']:
    localidade = resultado['localidade']
    populacao = resultado['series'][0]['serie']['2022']

    print(f"{localidade['nome']}: {populacao}")
```

### 5.2 Obter PIB de um Estado Específico

```python
import requests

# PIB de São Paulo (estado)
url = "https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/2021/variaveis/37"
params = {"localidades": "N3[35]"}  # N3 = estado, 35 = SP

response = requests.get(url, params=params)
data = response.json()

pib = data[0]['resultados'][0]['series'][0]['serie']['2021']
print(f"PIB de São Paulo (2021): R$ {pib} mil")
```

### 5.3 Obter Municípios de um Estado

```python
import requests

url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios"

response = requests.get(url)
municipios = response.json()

for municipio in municipios:
    print(f"{municipio['id']} - {municipio['nome']}")
```

### 5.4 Múltiplos Períodos

```python
# PIB de 2019 a 2021
url = "https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/2019|2020|2021/variaveis/37"
params = {"localidades": "N6[3550308]"}  # São Paulo

response = requests.get(url, params=params)
data = response.json()

serie = data[0]['resultados'][0]['series'][0]['serie']
for ano, valor in serie.items():
    print(f"{ano}: R$ {valor} mil")
```

---

## 6. Tratamento de Erros

### 6.1 Códigos HTTP

| Código | Descrição | Ação |
|--------|-----------|------|
| 200 | Sucesso | Processar resposta |
| 400 | Requisição inválida | Verificar parâmetros |
| 404 | Recurso não encontrado | Verificar IDs |
| 429 | Too Many Requests | Implementar retry com backoff |
| 500 | Erro do servidor | Retry com backoff exponencial |
| 503 | Serviço indisponível | Retry após delay |

### 6.2 Exemplo de Tratamento

```python
import requests
from time import sleep
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=10)
)
def fetch_ibge_data(url, params=None):
    """
    Busca dados da API IBGE com retry automático.
    """
    response = requests.get(url, params=params, timeout=30)

    # Levanta exceção para códigos 4xx e 5xx
    response.raise_for_status()

    return response.json()

# Uso
try:
    data = fetch_ibge_data(
        "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    )
    print(f"Obtidos {len(data)} municípios")

except requests.exceptions.HTTPError as e:
    print(f"Erro HTTP: {e}")

except requests.exceptions.Timeout:
    print("Timeout na requisição")

except requests.exceptions.RequestException as e:
    print(f"Erro na requisição: {e}")
```

### 6.3 Validação de Resposta

```python
def validate_ibge_response(data):
    """
    Valida estrutura da resposta da API IBGE.
    """
    if not data:
        raise ValueError("Resposta vazia")

    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError("Array vazio")

        # Valida primeiro item
        first_item = data[0]
        if 'id' not in first_item and 'localidade' not in first_item:
            raise ValueError("Estrutura de resposta inválida")

    return True
```

---

## 7. Boas Práticas

### 7.1 Rate Limiting

```python
import time
from functools import wraps

def rate_limit(min_interval=0.5):
    """
    Decorador para garantir intervalo mínimo entre chamadas.
    """
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            result = func(*args, **kwargs)
            last_called[0] = time.time()

            return result
        return wrapper
    return decorator

@rate_limit(min_interval=0.5)
def fetch_data(url):
    return requests.get(url).json()
```

### 7.2 Cache de Dados Estáticos

```python
from functools import lru_cache
import requests

@lru_cache(maxsize=128)
def get_estados():
    """
    Cache de lista de estados (dados estáticos).
    """
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    response = requests.get(url)
    return response.json()

# Primeira chamada busca da API
estados = get_estados()

# Chamadas subsequentes retornam do cache
estados = get_estados()  # Não faz nova requisição
```

### 7.3 Timeout Configurável

```python
# Sempre configurar timeout
response = requests.get(url, timeout=30)

# Timeout separado para conexão e leitura
response = requests.get(url, timeout=(5, 30))  # (connect, read)
```

---

## 8. Recursos Adicionais

### 8.1 Documentação Oficial

- **API de Localidades:** https://servicodados.ibge.gov.br/api/docs/localidades
- **API de Agregados:** https://servicodados.ibge.gov.br/api/docs/agregados?versao=3
- **SIDRA (Interface Web):** https://sidra.ibge.gov.br/
- **Metadados:** https://metadados.ibge.gov.br/

### 8.2 Ferramentas Úteis

- **Explorador SIDRA:** https://sidra.ibge.gov.br/home/cnt/brasil
- **Tabelas Agregadas:** https://sidra.ibge.gov.br/pesquisa
- **Catálogo de APIs Gov.br:** https://www.gov.br/conecta/catalogo/apis

---

## Conclusão

A API do IBGE fornece dados abrangentes e bem estruturados sobre localidades e indicadores socioeconômicos do Brasil. O uso adequado de rate limiting, retry, cache e validação garante uma integração robusta e confiável com o pipeline ETL.

**Observações Importantes:**
1. Sempre verificar documentação oficial para mudanças
2. Respeitar rate limits para não sobrecarregar a API
3. Cachear dados estáticos (localidades)
4. Validar estrutura de respostas
5. Implementar retry para lidar com falhas temporárias

**Autor:** Backend Architect Expert
**Data:** 2025-12-14
**Versão:** 1.0
