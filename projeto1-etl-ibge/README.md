# Pipeline ETL - Dados Socioeconômicos do IBGE

Pipeline de extração, transformação e carregamento (ETL) de dados socioeconômicos brasileiros utilizando a API do IBGE.

## Problema de Negócio

O Brasil possui uma riqueza de dados públicos disponibilizados pelo IBGE, porém esses dados estão distribuídos em múltiplas APIs e formatos. Este projeto resolve o problema de:

- **Fragmentação de dados**: Consolida dados de localidades, população e PIB em uma base única
- **Atualização manual**: Automatiza o processo de extração e atualização
- **Qualidade de dados**: Implementa validação e limpeza sistemática
- **Acessibilidade**: Disponibiliza dados em formatos prontos para análise

## Tecnologias Utilizadas

| Categoria | Tecnologia | Versão |
|-----------|------------|--------|
| Linguagem | Python | 3.10+ |
| HTTP Client | httpx | 0.25+ |
| Dados | Pandas | 2.0+ |
| Validação | Pydantic | 2.5+ |
| Banco de Dados | PostgreSQL | 14+ |
| ORM | SQLAlchemy | 2.0+ |
| Visualização | Plotly | 5.18+ |
| Testes | pytest | 7.4+ |
| Logging | loguru | 0.7+ |

## Estrutura do Projeto

```
projeto1-etl-ibge/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configurações centralizadas
├── src/
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── ibge_client.py   # Cliente HTTP para API IBGE
│   │   ├── localidades.py   # Extrator de localidades
│   │   ├── populacao.py     # Extrator de população
│   │   └── pib.py           # Extrator de PIB
│   ├── transformers/
│   │   ├── __init__.py
│   │   ├── data_validator.py # Validação com Pydantic
│   │   └── data_cleaner.py   # Limpeza de dados
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── database.py      # Carregamento PostgreSQL
│   │   └── csv_loader.py    # Carregamento CSV
│   └── utils/
│       ├── __init__.py
│       └── logger.py        # Configuração de logging
├── notebooks/
│   └── 01_analise_exploratoria.ipynb
├── tests/
│   ├── __init__.py
│   └── test_extractors.py
├── data/
│   ├── raw/                 # Dados brutos
│   └── processed/           # Dados processados
├── docs/                    # Documentação detalhada
├── logs/                    # Arquivos de log
├── main.py                  # Script principal CLI
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Como Executar

### 1. Pré-requisitos

- Python 3.10 ou superior
- PostgreSQL 14+ (opcional, para persistência em banco)
- Git

### 2. Instalação

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/etl-ibge.git
cd etl-ibge/projeto1-etl-ibge

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações (opcional)
# O projeto funciona com configurações padrão para CSV
```

### 4. Execução

#### Extrair todos os dados para CSV:
```bash
python main.py --extract all --output csv
```

#### Extrair apenas localidades:
```bash
python main.py --extract localidades --output csv
```

#### Extrair dados de população de anos específicos:
```bash
python main.py --extract populacao --anos 2020|2021|2022|2023
```

#### Extrair para banco de dados PostgreSQL:
```bash
python main.py --extract all --output database
```

#### Ver ajuda:
```bash
python main.py --help
```

### 5. Jupyter Notebook

```bash
# Iniciar Jupyter
jupyter notebook notebooks/
```

## Resultados

### Dados Extraídos

| Entidade | Registros | Descrição |
|----------|-----------|-----------|
| Regiões | 5 | Norte, Nordeste, Sudeste, Sul, Centro-Oeste |
| Estados | 27 | Todos os estados + DF |
| Municípios | ~5.570 | Todos os municípios brasileiros |
| População | Variável | Estimativas populacionais por ano |
| PIB | Variável | PIB municipal e per capita |

### Exemplo de Saída

```
# População por Estado (2023)
Estado          | População
----------------|------------
São Paulo       | 44.411.238
Minas Gerais    | 21.292.666
Rio de Janeiro  | 16.054.524
Bahia           | 14.136.417
...
```

### Visualizações Geradas

O notebook inclui visualizações interativas:
- Distribuição de municípios por região (Treemap)
- Evolução da população brasileira (Linha temporal)
- PIB por estado (Barras)
- PIB per capita comparativo (Barras horizontais)

## API do IBGE

### Endpoints Utilizados

| API | Endpoint | Dados |
|-----|----------|-------|
| Localidades | `/v1/localidades/regioes` | Regiões |
| Localidades | `/v1/localidades/estados` | Estados |
| Localidades | `/v1/localidades/municipios` | Municípios |
| SIDRA | `/v3/agregados/6579` | População estimada |
| SIDRA | `/v3/agregados/5938` | PIB municipal |
| SIDRA | `/v3/agregados/37` | PIB per capita |

### Documentação Oficial
- [API de Localidades](https://servicodados.ibge.gov.br/api/docs/localidades)
- [API de Agregados (SIDRA)](https://servicodados.ibge.gov.br/api/docs/agregados)

## Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Executar com cobertura
pytest tests/ --cov=src --cov-report=html
```

## Modelo de Dados (PostgreSQL)

```
┌─────────────────┐     ┌─────────────────┐
│   dim_regiao    │     │   dim_estado    │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │◄────┤ regiao_id (FK)  │
│ sigla           │     │ id (PK)         │
│ nome            │     │ sigla           │
└─────────────────┘     │ nome            │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │  dim_municipio  │
                        ├─────────────────┤
                        │ id (PK)         │
                        │ estado_id (FK)  │
                        │ nome            │
                        └────────┬────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼───────┐       ┌───────▼───────┐       ┌───────▼───────┐
│ fato_populacao│       │   fato_pib    │       │ metadata_     │
├───────────────┤       ├───────────────┤       │ extracao      │
│ id (PK)       │       │ id (PK)       │       ├───────────────┤
│ municipio_id  │       │ municipio_id  │       │ id (PK)       │
│ ano           │       │ ano           │       │ tabela        │
│ populacao     │       │ pib_total     │       │ registros     │
└───────────────┘       │ pib_per_capita│       │ status        │
                        └───────────────┘       └───────────────┘
```

## Roadmap

- [x] Extração de localidades (regiões, estados, municípios)
- [x] Extração de dados populacionais
- [x] Extração de dados de PIB
- [x] Carregamento para CSV
- [x] Carregamento para PostgreSQL
- [x] Validação com Pydantic
- [x] Jupyter Notebook com análises
- [ ] Dashboard Streamlit
- [ ] Agendamento com Airflow
- [ ] Testes de integração
- [ ] Cache de requisições

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Autor

**Maxwell** - [GitHub](https://github.com/seu-usuario)

---

*Projeto desenvolvido como parte do portfólio de Data Science*
