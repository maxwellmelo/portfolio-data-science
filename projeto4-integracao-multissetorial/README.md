# Sistema de Integração Multissetorial - Piauí

Plataforma de integração de dados governamentais de múltiplos setores do estado do Piauí, simulando cenário real de data lake governamental.

## Problema de Negócio

Dados governamentais estão fragmentados em múltiplas fontes:
- **Saúde** (DATASUS)
- **Educação** (INEP)
- **Economia** (IBGE)
- **Assistência Social** (MDS)

Este projeto demonstra como integrar essas fontes em uma base unificada para análises multissetoriais e tomada de decisão baseada em dados.

## Tecnologias Utilizadas

| Categoria | Tecnologia |
|-----------|------------|
| API REST | FastAPI |
| Orquestração | Prefect |
| Banco de Dados | PostgreSQL |
| ORM | SQLAlchemy |
| Validação | Pydantic |
| Containerização | Docker |
| Documentação | MkDocs |

## Estrutura do Projeto

```
projeto4-integracao-multissetorial/
├── config/
│   └── settings.py           # Configurações centralizadas
├── src/
│   ├── extractors/
│   │   ├── base_extractor.py # Classe base
│   │   └── synthetic_generator.py # Gerador de dados
│   ├── api/
│   │   └── main.py           # API FastAPI
│   ├── transformers/         # Transformações ETL
│   ├── loaders/              # Carregamento de dados
│   └── orchestration/        # Workflows Prefect
├── docker/
│   └── docker-compose.yml
├── data/
│   ├── raw/
│   ├── processed/
│   └── staging/
├── tests/
├── docs/
├── main.py                   # CLI principal
├── requirements.txt
└── README.md
```

## Fontes de Dados Integradas

### 1. Saúde (DATASUS)
- **SIM**: Sistema de Informações sobre Mortalidade
- **SINASC**: Nascidos Vivos
- **SIH**: Internações Hospitalares

### 2. Educação (INEP)
- **Censo Escolar**: Dados de escolas e matrículas
- **IDEB**: Índice de Desenvolvimento da Educação Básica

### 3. Economia (IBGE)
- **PIB Municipal**: Produto Interno Bruto
- **Cadastro de Empresas**: CEMPRE

### 4. Assistência Social (MDS)
- **Cadastro Único**: Famílias em situação de vulnerabilidade
- **Bolsa Família**: Beneficiários

## Como Executar

### 1. Instalação

```bash
cd projeto4-integracao-multissetorial

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Gerar Dados Sintéticos

```bash
python main.py generate
```

### 3. Iniciar API REST

```bash
python main.py api
```

A API estará disponível em: http://localhost:8000

### 4. Acessar Documentação

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações da API |
| `/health` | GET | Status de saúde |
| `/fontes` | GET | Lista fontes de dados |
| `/municipios` | GET | Lista municípios do PI |
| `/saude/mortalidade` | GET | Dados de mortalidade |
| `/saude/nascimentos` | GET | Dados de nascimentos |
| `/educacao/escolas` | GET | Dados de escolas |
| `/educacao/ideb` | GET | Dados do IDEB |
| `/economia/pib` | GET | PIB municipal |
| `/assistencia/cadunico` | GET | Dados do CadÚnico |
| `/indicadores/{municipio_id}` | GET | Indicadores consolidados |

### Exemplo de Uso

```python
import requests

# Indicadores de Teresina
response = requests.get("http://localhost:8000/indicadores/2211001?ano=2023")
data = response.json()

print(f"PIB: R$ {data['economia']['pib_total_mil_reais']:,.2f} mil")
print(f"População: {data['economia']['populacao']:,}")
print(f"Escolas: {data['educacao']['total_escolas']}")
```

## Modelo de Dados

```
┌─────────────────┐     ┌─────────────────┐
│  dim_municipio  │     │  dim_tempo      │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ ano (PK)        │
│ nome            │     │ mes             │
│ uf              │     │ trimestre       │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│fato_saude │  │fato_educa │  │fato_econ  │
└───────────┘  └───────────┘  └───────────┘
```

## Governança de Dados

### Metadados Registrados
- Origem dos dados
- Data de extração
- Transformações aplicadas
- Qualidade dos dados

### Linhagem de Dados
- Rastreamento de origem
- Histórico de transformações
- Versionamento

## Docker (Opcional)

```bash
# Construir e iniciar serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f api
```

## Testes

```bash
pytest tests/ -v
```

## Roadmap

- [x] Geração de dados sintéticos
- [x] API REST com FastAPI
- [x] Documentação automática
- [ ] Orquestração com Prefect/Airflow
- [ ] Dashboard de monitoramento
- [ ] Integração com banco de dados real
- [ ] Cache com Redis

## Licença

MIT License

## Autor

**Maxwell** - Projeto de Portfólio em Data Science

---

*Simulação de sistema de integração de dados governamentais*
