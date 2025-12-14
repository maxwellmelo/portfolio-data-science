# Arquitetura ETL - Dados Socioeconômicos IBGE

## Sumário Executivo

Este documento descreve a arquitetura completa de um pipeline ETL (Extract, Transform, Load) para extração, transformação e armazenamento de dados socioeconômicos do IBGE utilizando Python, SQLAlchemy e PostgreSQL.

**Data de Criação:** 2025-12-14
**Status:** Planejamento
**Tecnologias:** Python 3.11+, PostgreSQL 15+, SQLAlchemy 2.0+

---

## 1. Visão Geral da Arquitetura

### 1.1 Princípios Arquiteturais

- **Separação de Responsabilidades**: Cada módulo tem uma única responsabilidade bem definida
- **Modularidade**: Componentes independentes e reutilizáveis
- **Testabilidade**: Toda lógica de negócio é testável unitariamente
- **Observabilidade**: Logs estruturados em todos os pontos críticos
- **Resiliência**: Tratamento robusto de erros com retry e circuit breaker
- **Escalabilidade**: Processamento em lotes configurável
- **Manutenibilidade**: Código limpo, documentado e seguindo padrões PEP 8

### 1.2 Fluxo do Pipeline ETL

```
┌─────────────────────────────────────────────────────────────────┐
│                        PIPELINE ETL IBGE                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│              │      │              │      │              │
│   EXTRACT    │ ───> │  TRANSFORM   │ ───> │     LOAD     │
│              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
      │                     │                      │
      │                     │                      │
      ▼                     ▼                      ▼
┌──────────┐          ┌──────────┐          ┌──────────┐
│ API IBGE │          │ Validação│          │PostgreSQL│
│ Múltiplos│          │ Limpeza  │          │ Transações│
│ Endpoints│          │ Enriquec.│          │ Indexação│
└──────────┘          └──────────┘          └──────────┘
```

---

## 2. Estrutura de Diretórios do Projeto

```
ibge-etl-pipeline/
│
├── README.md                          # Documentação principal do projeto
├── .env.example                       # Exemplo de variáveis de ambiente
├── .gitignore                         # Arquivos ignorados pelo Git
├── requirements.txt                   # Dependências do projeto
├── setup.py                           # Configuração de instalação
├── pyproject.toml                     # Configuração moderna do projeto
│
├── config/                            # Configurações
│   ├── __init__.py
│   ├── settings.py                    # Configurações centralizadas
│   ├── database.py                    # Configuração do banco de dados
│   └── logging_config.py              # Configuração de logs
│
├── src/                               # Código fonte principal
│   ├── __init__.py
│   │
│   ├── extractors/                    # Módulo de extração
│   │   ├── __init__.py
│   │   ├── base_extractor.py          # Classe base abstrata
│   │   ├── ibge_api_client.py         # Cliente HTTP para API IBGE
│   │   ├── localidades_extractor.py   # Extrator de municípios
│   │   ├── populacao_extractor.py     # Extrator de população
│   │   ├── pib_extractor.py           # Extrator de PIB
│   │   └── indicadores_extractor.py   # Extrator de indicadores sociais
│   │
│   ├── transformers/                  # Módulo de transformação
│   │   ├── __init__.py
│   │   ├── base_transformer.py        # Classe base de transformação
│   │   ├── data_cleaner.py            # Limpeza de dados
│   │   ├── data_validator.py          # Validação de dados
│   │   ├── data_enricher.py           # Enriquecimento de dados
│   │   └── normalizer.py              # Normalização de dados
│   │
│   ├── loaders/                       # Módulo de carga
│   │   ├── __init__.py
│   │   ├── base_loader.py             # Classe base de carga
│   │   ├── database_loader.py         # Carregador para PostgreSQL
│   │   └── batch_loader.py            # Carregamento em lotes
│   │
│   ├── models/                        # Modelos de dados
│   │   ├── __init__.py
│   │   ├── base.py                    # Base declarativa SQLAlchemy
│   │   ├── municipio.py               # Modelo de município
│   │   ├── populacao.py               # Modelo de população
│   │   ├── pib.py                     # Modelo de PIB
│   │   ├── indicador_social.py        # Modelo de indicadores
│   │   └── metadata_extracao.py       # Metadados de extração
│   │
│   ├── utils/                         # Utilitários
│   │   ├── __init__.py
│   │   ├── logger.py                  # Sistema de logging
│   │   ├── retry.py                   # Decorador de retry
│   │   ├── validators.py              # Validadores customizados
│   │   └── date_utils.py              # Utilitários de data
│   │
│   └── pipeline/                      # Orquestração do pipeline
│       ├── __init__.py
│       ├── etl_pipeline.py            # Pipeline principal
│       ├── orchestrator.py            # Orquestrador de tarefas
│       └── scheduler.py               # Agendador de execuções
│
├── tests/                             # Testes
│   ├── __init__.py
│   ├── conftest.py                    # Fixtures do pytest
│   │
│   ├── unit/                          # Testes unitários
│   │   ├── test_extractors.py
│   │   ├── test_transformers.py
│   │   ├── test_loaders.py
│   │   └── test_validators.py
│   │
│   ├── integration/                   # Testes de integração
│   │   ├── test_database.py
│   │   ├── test_api_integration.py
│   │   └── test_pipeline.py
│   │
│   └── fixtures/                      # Dados de teste
│       ├── sample_municipios.json
│       ├── sample_populacao.json
│       └── sample_pib.json
│
├── scripts/                           # Scripts auxiliares
│   ├── create_database.py             # Criação do banco de dados
│   ├── run_pipeline.py                # Executar pipeline
│   ├── migrate_schema.py              # Migração de schema
│   └── generate_reports.py            # Geração de relatórios
│
├── migrations/                        # Migrações do banco (Alembic)
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│
├── logs/                              # Arquivos de log
│   └── .gitkeep
│
├── data/                              # Dados temporários
│   ├── raw/                           # Dados brutos extraídos
│   ├── processed/                     # Dados processados
│   └── backups/                       # Backups
│
└── docs/                              # Documentação adicional
    ├── API_ENDPOINTS.md               # Documentação dos endpoints IBGE
    ├── DATABASE_SCHEMA.md             # Schema do banco de dados
    ├── DEPLOYMENT.md                  # Guia de deployment
    └── TROUBLESHOOTING.md             # Solução de problemas
```

---

## 3. Schema do Banco de Dados

### 3.1 Diagrama Entidade-Relacionamento

```
┌─────────────────────────────────────────────────────────────────┐
│                      SCHEMA: ibge_socioeconomico                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│    dim_regiao        │
├──────────────────────┤
│ PK id_regiao         │
│    codigo_ibge       │
│    nome              │
│    sigla             │
│    created_at        │
│    updated_at        │
└──────────────────────┘
           │
           │ 1:N
           ▼
┌──────────────────────┐
│    dim_estado        │
├──────────────────────┤
│ PK id_estado         │
│ FK id_regiao         │
│    codigo_ibge       │
│    nome              │
│    sigla             │
│    created_at        │
│    updated_at        │
└──────────────────────┘
           │
           │ 1:N
           ▼
┌──────────────────────┐
│   dim_municipio      │
├──────────────────────┤
│ PK id_municipio      │
│ FK id_estado         │
│    codigo_ibge       │
│    nome              │
│    area_km2          │
│    latitude          │
│    longitude         │
│    created_at        │
│    updated_at        │
└──────────────────────┘
           │
           │ 1:N
           ├────────────────┐
           │                │
           ▼                ▼
┌──────────────────────┐  ┌──────────────────────┐
│   fato_populacao     │  │     fato_pib         │
├──────────────────────┤  ├──────────────────────┤
│ PK id_populacao      │  │ PK id_pib            │
│ FK id_municipio      │  │ FK id_municipio      │
│    ano               │  │    ano               │
│    populacao_total   │  │    pib_total         │
│    populacao_urbana  │  │    pib_per_capita    │
│    populacao_rural   │  │    vab_agropecuaria  │
│    densidade_demog   │  │    vab_industria     │
│    created_at        │  │    vab_servicos      │
│    updated_at        │  │    impostos          │
└──────────────────────┘  │    created_at        │
           │              │    updated_at        │
           │              └──────────────────────┘
           │
           │ 1:N
           ▼
┌──────────────────────┐
│ fato_indicador_social│
├──────────────────────┤
│ PK id_indicador      │
│ FK id_municipio      │
│    ano               │
│    tipo_indicador    │
│    valor             │
│    unidade_medida    │
│    fonte             │
│    created_at        │
│    updated_at        │
└──────────────────────┘

┌──────────────────────┐
│ metadata_extracao    │
├──────────────────────┤
│ PK id_extracao       │
│    tipo_dados        │
│    data_extracao     │
│    status            │
│    registros_extraido│
│    registros_carregad│
│    tempo_execucao_seg│
│    mensagem_erro     │
│    created_at        │
└──────────────────────┘
```

### 3.2 Tabelas Detalhadas

#### 3.2.1 Dimensões (Tabelas de Referência)

**dim_regiao**
```sql
CREATE TABLE dim_regiao (
    id_regiao SERIAL PRIMARY KEY,
    codigo_ibge INTEGER UNIQUE NOT NULL,
    nome VARCHAR(50) NOT NULL,
    sigla VARCHAR(2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_regiao_codigo ON dim_regiao(codigo_ibge);
```

**dim_estado**
```sql
CREATE TABLE dim_estado (
    id_estado SERIAL PRIMARY KEY,
    id_regiao INTEGER NOT NULL REFERENCES dim_regiao(id_regiao),
    codigo_ibge INTEGER UNIQUE NOT NULL,
    nome VARCHAR(50) NOT NULL,
    sigla VARCHAR(2) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_estado_codigo ON dim_estado(codigo_ibge);
CREATE INDEX idx_estado_regiao ON dim_estado(id_regiao);
```

**dim_municipio**
```sql
CREATE TABLE dim_municipio (
    id_municipio SERIAL PRIMARY KEY,
    id_estado INTEGER NOT NULL REFERENCES dim_estado(id_estado),
    codigo_ibge INTEGER UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    area_km2 DECIMAL(12,4),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_municipio_codigo ON dim_municipio(codigo_ibge);
CREATE INDEX idx_municipio_estado ON dim_municipio(id_estado);
CREATE INDEX idx_municipio_nome ON dim_municipio(nome);
```

#### 3.2.2 Fatos (Tabelas de Medidas)

**fato_populacao**
```sql
CREATE TABLE fato_populacao (
    id_populacao SERIAL PRIMARY KEY,
    id_municipio INTEGER NOT NULL REFERENCES dim_municipio(id_municipio),
    ano INTEGER NOT NULL,
    populacao_total BIGINT NOT NULL,
    populacao_urbana BIGINT,
    populacao_rural BIGINT,
    densidade_demografica DECIMAL(12,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_populacao_municipio_ano UNIQUE(id_municipio, ano),
    CONSTRAINT chk_ano_valido CHECK (ano >= 1900 AND ano <= 2100),
    CONSTRAINT chk_populacao_positiva CHECK (populacao_total >= 0)
);

CREATE INDEX idx_populacao_municipio ON fato_populacao(id_municipio);
CREATE INDEX idx_populacao_ano ON fato_populacao(ano);
CREATE INDEX idx_populacao_municipio_ano ON fato_populacao(id_municipio, ano);
```

**fato_pib**
```sql
CREATE TABLE fato_pib (
    id_pib SERIAL PRIMARY KEY,
    id_municipio INTEGER NOT NULL REFERENCES dim_municipio(id_municipio),
    ano INTEGER NOT NULL,
    pib_total DECIMAL(18,2) NOT NULL,
    pib_per_capita DECIMAL(12,2),
    vab_agropecuaria DECIMAL(18,2),
    vab_industria DECIMAL(18,2),
    vab_servicos DECIMAL(18,2),
    impostos DECIMAL(18,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_pib_municipio_ano UNIQUE(id_municipio, ano),
    CONSTRAINT chk_pib_ano_valido CHECK (ano >= 1900 AND ano <= 2100),
    CONSTRAINT chk_pib_positivo CHECK (pib_total >= 0)
);

CREATE INDEX idx_pib_municipio ON fato_pib(id_municipio);
CREATE INDEX idx_pib_ano ON fato_pib(ano);
CREATE INDEX idx_pib_municipio_ano ON fato_pib(id_municipio, ano);
```

**fato_indicador_social**
```sql
CREATE TABLE fato_indicador_social (
    id_indicador SERIAL PRIMARY KEY,
    id_municipio INTEGER NOT NULL REFERENCES dim_municipio(id_municipio),
    ano INTEGER NOT NULL,
    tipo_indicador VARCHAR(100) NOT NULL,
    valor DECIMAL(18,6) NOT NULL,
    unidade_medida VARCHAR(50),
    fonte VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_indicador_municipio_ano_tipo UNIQUE(id_municipio, ano, tipo_indicador),
    CONSTRAINT chk_indicador_ano_valido CHECK (ano >= 1900 AND ano <= 2100)
);

CREATE INDEX idx_indicador_municipio ON fato_indicador_social(id_municipio);
CREATE INDEX idx_indicador_ano ON fato_indicador_social(ano);
CREATE INDEX idx_indicador_tipo ON fato_indicador_social(tipo_indicador);
CREATE INDEX idx_indicador_municipio_ano ON fato_indicador_social(id_municipio, ano);
```

#### 3.2.3 Metadados

**metadata_extracao**
```sql
CREATE TABLE metadata_extracao (
    id_extracao SERIAL PRIMARY KEY,
    tipo_dados VARCHAR(50) NOT NULL,
    data_extracao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('SUCESSO', 'ERRO', 'PARCIAL')),
    registros_extraidos INTEGER,
    registros_carregados INTEGER,
    tempo_execucao_segundos DECIMAL(10,2),
    mensagem_erro TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metadata_tipo ON metadata_extracao(tipo_dados);
CREATE INDEX idx_metadata_data ON metadata_extracao(data_extracao);
CREATE INDEX idx_metadata_status ON metadata_extracao(status);
```

---

## 4. Classes e Funções Principais

### 4.1 Módulo de Extração (Extractors)

#### 4.1.1 Base Extractor (Classe Abstrata)

```python
"""
src/extractors/base_extractor.py

Classe base abstrata para todos os extratores de dados.
Define a interface comum que todos os extratores devem implementar.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

class BaseExtractor(ABC):
    """
    Classe base abstrata para extratores de dados.

    Responsabilidades:
    - Definir interface comum para extração
    - Implementar logging padrão
    - Gerenciar metadados de extração
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Inicializa o extrator.

        Args:
            logger: Logger customizado (opcional)
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.extraction_metadata = {
            'start_time': None,
            'end_time': None,
            'records_extracted': 0,
            'status': 'PENDING'
        }

    @abstractmethod
    def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Método abstrato para extração de dados.

        Args:
            **kwargs: Parâmetros específicos de cada extrator

        Returns:
            Lista de dicionários com os dados extraídos

        Raises:
            ExtractionError: Quando ocorre erro na extração
        """
        pass

    @abstractmethod
    def validate_response(self, response: Any) -> bool:
        """
        Valida a resposta da fonte de dados.

        Args:
            response: Resposta a ser validada

        Returns:
            True se válida, False caso contrário
        """
        pass

    def _start_extraction(self):
        """Marca o início da extração."""
        self.extraction_metadata['start_time'] = datetime.utcnow()
        self.extraction_metadata['status'] = 'IN_PROGRESS'
        self.logger.info(f"Iniciando extração: {self.__class__.__name__}")

    def _end_extraction(self, success: bool = True):
        """
        Marca o fim da extração.

        Args:
            success: Se a extração foi bem-sucedida
        """
        self.extraction_metadata['end_time'] = datetime.utcnow()
        self.extraction_metadata['status'] = 'SUCCESS' if success else 'ERROR'

        duration = (self.extraction_metadata['end_time'] -
                   self.extraction_metadata['start_time']).total_seconds()

        self.logger.info(
            f"Extração finalizada: {self.__class__.__name__} | "
            f"Registros: {self.extraction_metadata['records_extracted']} | "
            f"Duração: {duration:.2f}s"
        )

    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados da extração."""
        return self.extraction_metadata.copy()
```

#### 4.1.2 IBGE API Client

```python
"""
src/extractors/ibge_api_client.py

Cliente HTTP para comunicação com a API do IBGE.
Implementa retry automático, rate limiting e tratamento de erros.
"""

import requests
from typing import Dict, Any, Optional, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import logging

class IBGEAPIClient:
    """
    Cliente HTTP para API do IBGE com retry e rate limiting.

    Features:
    - Retry automático em caso de falha
    - Rate limiting para respeitar limites da API
    - Logging de requisições
    - Cache de sessão
    """

    BASE_URL = "https://servicodados.ibge.gov.br/api/v1"
    BASE_URL_V3 = "https://servicodados.ibge.gov.br/api/v3"

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_delay: float = 0.5
    ):
        """
        Inicializa o cliente da API.

        Args:
            timeout: Timeout das requisições em segundos
            max_retries: Número máximo de tentativas
            rate_limit_delay: Delay entre requisições (segundos)
        """
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = self._create_session(max_retries)

    def _create_session(self, max_retries: int) -> requests.Session:
        """
        Cria sessão HTTP com retry strategy.

        Args:
            max_retries: Número máximo de tentativas

        Returns:
            Sessão configurada
        """
        session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            backoff_factor=1
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        use_v3: bool = False
    ) -> Dict[str, Any]:
        """
        Realiza requisição GET para a API.

        Args:
            endpoint: Endpoint da API (sem base URL)
            params: Parâmetros da query string
            use_v3: Se deve usar API v3

        Returns:
            Resposta JSON da API

        Raises:
            APIError: Quando a requisição falha
        """
        base_url = self.BASE_URL_V3 if use_v3 else self.BASE_URL
        url = f"{base_url}/{endpoint.lstrip('/')}"

        self.logger.debug(f"GET {url} | Params: {params}")

        try:
            # Rate limiting
            time.sleep(self.rate_limit_delay)

            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )

            response.raise_for_status()

            self.logger.debug(f"Response: {response.status_code}")

            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro na requisição: {e}")
            raise APIError(f"Falha ao acessar {url}: {str(e)}") from e

    def get_municipios(self) -> List[Dict[str, Any]]:
        """Obtém todos os municípios do Brasil."""
        return self.get("localidades/municipios")

    def get_estados(self) -> List[Dict[str, Any]]:
        """Obtém todos os estados do Brasil."""
        return self.get("localidades/estados")

    def get_regioes(self) -> List[Dict[str, Any]]:
        """Obtém todas as regiões do Brasil."""
        return self.get("localidades/regioes")

    def get_agregado(
        self,
        agregado_id: int,
        localidade: str,
        periodo: str,
        variaveis: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtém dados agregados do SIDRA.

        Args:
            agregado_id: ID do agregado (ex: 5938 para PIB)
            localidade: Nível geográfico (ex: 'N6[all]' para municípios)
            periodo: Período (ex: '2021')
            variaveis: Variáveis específicas

        Returns:
            Dados do agregado
        """
        endpoint = f"agregados/{agregado_id}/periodos/{periodo}/variaveis"

        if variaveis:
            endpoint += f"/{variaveis}"

        params = {"localidades": localidade}

        return self.get(endpoint, params=params, use_v3=True)

class APIError(Exception):
    """Exceção para erros da API."""
    pass
```

#### 4.1.3 Localidades Extractor

```python
"""
src/extractors/localidades_extractor.py

Extrator de dados de localidades (regiões, estados, municípios).
"""

from typing import List, Dict, Any
from .base_extractor import BaseExtractor
from .ibge_api_client import IBGEAPIClient

class LocalidadesExtractor(BaseExtractor):
    """
    Extrator de dados de localidades do IBGE.

    Extrai:
    - Regiões
    - Estados
    - Municípios
    """

    def __init__(self, api_client: IBGEAPIClient):
        """
        Inicializa o extrator.

        Args:
            api_client: Cliente da API do IBGE
        """
        super().__init__()
        self.api_client = api_client

    def extract(self, tipo: str = 'municipios') -> List[Dict[str, Any]]:
        """
        Extrai dados de localidades.

        Args:
            tipo: Tipo de localidade ('regioes', 'estados', 'municipios')

        Returns:
            Lista de localidades
        """
        self._start_extraction()

        try:
            if tipo == 'regioes':
                data = self.api_client.get_regioes()
            elif tipo == 'estados':
                data = self.api_client.get_estados()
            elif tipo == 'municipios':
                data = self.api_client.get_municipios()
            else:
                raise ValueError(f"Tipo inválido: {tipo}")

            if not self.validate_response(data):
                raise ValueError("Resposta inválida da API")

            self.extraction_metadata['records_extracted'] = len(data)
            self._end_extraction(success=True)

            return data

        except Exception as e:
            self.logger.error(f"Erro na extração: {e}")
            self._end_extraction(success=False)
            raise

    def validate_response(self, response: Any) -> bool:
        """
        Valida resposta da API.

        Args:
            response: Resposta a validar

        Returns:
            True se válida
        """
        if not isinstance(response, list):
            return False

        if len(response) == 0:
            self.logger.warning("Resposta vazia")
            return True

        # Valida estrutura do primeiro item
        required_fields = {'id', 'nome'}
        first_item = response[0]

        return all(field in first_item for field in required_fields)
```

### 4.2 Módulo de Transformação (Transformers)

#### 4.2.1 Data Validator

```python
"""
src/transformers/data_validator.py

Validador de qualidade de dados.
Implementa regras de validação para garantir integridade dos dados.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, validator, Field
import logging

class MunicipioSchema(BaseModel):
    """Schema de validação para município."""

    codigo_ibge: int = Field(..., ge=1000000, le=9999999)
    nome: str = Field(..., min_length=1, max_length=100)
    area_km2: Optional[float] = Field(None, ge=0)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    @validator('nome')
    def validate_nome(cls, v):
        """Valida e limpa nome do município."""
        return v.strip().title()

class PopulacaoSchema(BaseModel):
    """Schema de validação para população."""

    codigo_ibge: int = Field(..., ge=1000000, le=9999999)
    ano: int = Field(..., ge=1900, le=2100)
    populacao_total: int = Field(..., ge=0)
    populacao_urbana: Optional[int] = Field(None, ge=0)
    populacao_rural: Optional[int] = Field(None, ge=0)

    @validator('populacao_rural', always=True)
    def validate_populacao_components(cls, v, values):
        """Valida que urbana + rural = total."""
        if 'populacao_urbana' in values and values['populacao_urbana'] is not None:
            if v is not None:
                total_calc = values['populacao_urbana'] + v
                total_real = values.get('populacao_total', 0)

                # Permite diferença de até 1% devido a arredondamentos
                if abs(total_calc - total_real) / total_real > 0.01:
                    raise ValueError(
                        f"Soma urbana+rural ({total_calc}) difere do total ({total_real})"
                    )
        return v

class PIBSchema(BaseModel):
    """Schema de validação para PIB."""

    codigo_ibge: int = Field(..., ge=1000000, le=9999999)
    ano: int = Field(..., ge=1900, le=2100)
    pib_total: float = Field(..., ge=0)
    pib_per_capita: Optional[float] = Field(None, ge=0)

class DataValidator:
    """
    Validador de qualidade de dados.

    Responsabilidades:
    - Validar schemas
    - Detectar outliers
    - Gerar relatório de qualidade
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validation_errors = []

    def validate_batch(
        self,
        data: List[Dict[str, Any]],
        schema_class: type
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Valida lote de dados.

        Args:
            data: Lista de registros
            schema_class: Classe do schema Pydantic

        Returns:
            Tupla (dados_validos, dados_invalidos)
        """
        valid_records = []
        invalid_records = []

        for record in data:
            try:
                validated = schema_class(**record)
                valid_records.append(validated.dict())
            except Exception as e:
                self.logger.warning(f"Registro inválido: {e}")
                invalid_records.append({
                    'record': record,
                    'error': str(e)
                })
                self.validation_errors.append({
                    'record': record,
                    'error': str(e),
                    'schema': schema_class.__name__
                })

        self.logger.info(
            f"Validação: {len(valid_records)} válidos, "
            f"{len(invalid_records)} inválidos"
        )

        return valid_records, invalid_records

    def get_quality_report(self) -> Dict[str, Any]:
        """
        Gera relatório de qualidade dos dados.

        Returns:
            Relatório com métricas de qualidade
        """
        total_errors = len(self.validation_errors)

        error_types = {}
        for error in self.validation_errors:
            schema = error['schema']
            error_types[schema] = error_types.get(schema, 0) + 1

        return {
            'total_validation_errors': total_errors,
            'errors_by_schema': error_types,
            'sample_errors': self.validation_errors[:10]
        }
```

### 4.3 Módulo de Carga (Loaders)

#### 4.3.1 Database Loader

```python
"""
src/loaders/database_loader.py

Carregador de dados para PostgreSQL usando SQLAlchemy.
Implementa estratégias de upsert e processamento em lotes.
"""

from typing import List, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import and_
import logging

from ..models.base import Base

class DatabaseLoader:
    """
    Carregador de dados para PostgreSQL.

    Features:
    - Upsert (insert ou update)
    - Processamento em lotes
    - Transações atômicas
    - Rollback automático em caso de erro
    """

    def __init__(self, session: Session, batch_size: int = 1000):
        """
        Inicializa o loader.

        Args:
            session: Sessão SQLAlchemy
            batch_size: Tamanho do lote
        """
        self.session = session
        self.batch_size = batch_size
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_batch(
        self,
        data: List[Dict[str, Any]],
        model_class: Type[Base],
        unique_fields: List[str]
    ) -> int:
        """
        Carrega lote de dados com upsert.

        Args:
            data: Lista de dicionários com dados
            model_class: Classe do modelo SQLAlchemy
            unique_fields: Campos que identificam registro único

        Returns:
            Número de registros carregados
        """
        if not data:
            return 0

        total_loaded = 0

        try:
            # Processa em lotes
            for i in range(0, len(data), self.batch_size):
                batch = data[i:i + self.batch_size]

                stmt = insert(model_class).values(batch)

                # Configura ON CONFLICT para upsert
                update_dict = {
                    c.name: c
                    for c in stmt.excluded
                    if c.name not in unique_fields and c.name != 'created_at'
                }

                stmt = stmt.on_conflict_do_update(
                    index_elements=unique_fields,
                    set_=update_dict
                )

                self.session.execute(stmt)
                self.session.commit()

                total_loaded += len(batch)

                self.logger.debug(
                    f"Lote carregado: {total_loaded}/{len(data)} registros"
                )

            self.logger.info(
                f"Carga concluída: {total_loaded} registros em "
                f"{model_class.__tablename__}"
            )

            return total_loaded

        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            self.session.rollback()
            raise

    def delete_by_criteria(
        self,
        model_class: Type[Base],
        criteria: Dict[str, Any]
    ) -> int:
        """
        Deleta registros por critério.

        Args:
            model_class: Classe do modelo
            criteria: Dicionário com critérios de deleção

        Returns:
            Número de registros deletados
        """
        try:
            filters = [
                getattr(model_class, key) == value
                for key, value in criteria.items()
            ]

            deleted = self.session.query(model_class).filter(
                and_(*filters)
            ).delete()

            self.session.commit()

            self.logger.info(
                f"{deleted} registros deletados de {model_class.__tablename__}"
            )

            return deleted

        except Exception as e:
            self.logger.error(f"Erro ao deletar dados: {e}")
            self.session.rollback()
            raise
```

### 4.4 Pipeline Orchestrator

```python
"""
src/pipeline/orchestrator.py

Orquestrador principal do pipeline ETL.
Coordena extração, transformação e carga de dados.
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from ..extractors.localidades_extractor import LocalidadesExtractor
from ..extractors.ibge_api_client import IBGEAPIClient
from ..transformers.data_validator import DataValidator
from ..loaders.database_loader import DatabaseLoader
from ..models.metadata_extracao import MetadataExtracao
from ..utils.logger import setup_logger

class ETLOrchestrator:
    """
    Orquestrador do pipeline ETL.

    Responsabilidades:
    - Coordenar execução do pipeline
    - Gerenciar dependências entre etapas
    - Registrar metadados de execução
    - Tratar erros e rollback
    """

    def __init__(
        self,
        api_client: IBGEAPIClient,
        db_session,
        logger: logging.Logger = None
    ):
        """
        Inicializa o orquestrador.

        Args:
            api_client: Cliente da API IBGE
            db_session: Sessão do banco de dados
            logger: Logger customizado
        """
        self.api_client = api_client
        self.db_session = db_session
        self.logger = logger or setup_logger('ETLOrchestrator')

        # Inicializa componentes
        self.validator = DataValidator()
        self.loader = DatabaseLoader(db_session)

        # Metadados da execução
        self.execution_metadata = {
            'start_time': None,
            'end_time': None,
            'status': 'PENDING',
            'steps_completed': [],
            'errors': []
        }

    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Executa pipeline completo.

        Returns:
            Relatório de execução
        """
        self.execution_metadata['start_time'] = datetime.utcnow()
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO PIPELINE ETL IBGE")
        self.logger.info("=" * 60)

        try:
            # 1. Extrair e carregar localidades
            self._extract_and_load_regioes()
            self._extract_and_load_estados()
            self._extract_and_load_municipios()

            # 2. Extrair e carregar dados socioeconômicos
            self._extract_and_load_populacao()
            self._extract_and_load_pib()
            self._extract_and_load_indicadores()

            self.execution_metadata['status'] = 'SUCCESS'

        except Exception as e:
            self.logger.error(f"Erro crítico no pipeline: {e}")
            self.execution_metadata['status'] = 'ERROR'
            self.execution_metadata['errors'].append(str(e))
            raise

        finally:
            self.execution_metadata['end_time'] = datetime.utcnow()
            self._save_execution_metadata()
            self._print_summary()

        return self.execution_metadata

    def _extract_and_load_regioes(self):
        """Extrai e carrega dados de regiões."""
        self.logger.info("Processando REGIÕES...")

        extractor = LocalidadesExtractor(self.api_client)
        data = extractor.extract(tipo='regioes')

        # Transformação
        transformed_data = self._transform_regioes(data)

        # Validação
        valid_data, invalid_data = self.validator.validate_batch(
            transformed_data,
            RegiaoSchema
        )

        # Carga
        from ..models.municipio import DimRegiao
        loaded = self.loader.load_batch(
            valid_data,
            DimRegiao,
            unique_fields=['codigo_ibge']
        )

        self.execution_metadata['steps_completed'].append({
            'step': 'regioes',
            'extracted': len(data),
            'valid': len(valid_data),
            'invalid': len(invalid_data),
            'loaded': loaded
        })

        self.logger.info(f"REGIÕES concluído: {loaded} registros")

    def _transform_regioes(self, data: List[Dict]) -> List[Dict]:
        """Transforma dados de regiões."""
        return [
            {
                'codigo_ibge': item['id'],
                'nome': item['nome'],
                'sigla': item['sigla']
            }
            for item in data
        ]

    def _save_execution_metadata(self):
        """Salva metadados da execução no banco."""
        try:
            duration = (
                self.execution_metadata['end_time'] -
                self.execution_metadata['start_time']
            ).total_seconds()

            metadata = MetadataExtracao(
                tipo_dados='PIPELINE_COMPLETO',
                data_extracao=self.execution_metadata['start_time'],
                status=self.execution_metadata['status'],
                tempo_execucao_segundos=duration,
                mensagem_erro='; '.join(self.execution_metadata['errors'])
                              if self.execution_metadata['errors'] else None
            )

            self.db_session.add(metadata)
            self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Erro ao salvar metadados: {e}")

    def _print_summary(self):
        """Imprime resumo da execução."""
        duration = (
            self.execution_metadata['end_time'] -
            self.execution_metadata['start_time']
        ).total_seconds()

        self.logger.info("=" * 60)
        self.logger.info("RESUMO DA EXECUÇÃO")
        self.logger.info("=" * 60)
        self.logger.info(f"Status: {self.execution_metadata['status']}")
        self.logger.info(f"Duração: {duration:.2f} segundos")
        self.logger.info(f"Etapas: {len(self.execution_metadata['steps_completed'])}")

        for step in self.execution_metadata['steps_completed']:
            self.logger.info(
                f"  - {step['step']}: {step['loaded']} registros carregados"
            )

        if self.execution_metadata['errors']:
            self.logger.error("Erros encontrados:")
            for error in self.execution_metadata['errors']:
                self.logger.error(f"  - {error}")

        self.logger.info("=" * 60)
```

---

## 5. Fluxo Detalhado do Pipeline ETL

### 5.1 Fase de Extração (Extract)

```
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: EXTRAÇÃO                                            │
└─────────────────────────────────────────────────────────────┘

1. Inicialização
   ├─ Criar cliente HTTP com retry strategy
   ├─ Configurar rate limiting
   └─ Inicializar logger

2. Extração de Localidades (ordem hierárquica)
   ├─ Regiões (5 registros)
   │  └─ Endpoint: /localidades/regioes
   │
   ├─ Estados (27 registros)
   │  └─ Endpoint: /localidades/estados
   │
   └─ Municípios (~5570 registros)
      └─ Endpoint: /localidades/municipios

3. Extração de Dados Socioeconômicos
   ├─ População
   │  ├─ Censo (tabela 200 - SIDRA)
   │  ├─ Estimativas (tabela 6579 - SIDRA)
   │  └─ Projeções (/projecoes/populacao)
   │
   ├─ PIB Municipal
   │  ├─ Agregado 5938 (PIB total)
   │  ├─ Agregado 37 (PIB per capita)
   │  └─ VAB por setor
   │
   └─ Indicadores Sociais
      ├─ IDH (se disponível)
      ├─ Taxa de alfabetização
      └─ Outros indicadores SIDRA

4. Persistência Temporária
   ├─ Salvar dados brutos em JSON (data/raw/)
   └─ Registrar metadados de extração
```

### 5.2 Fase de Transformação (Transform)

```
┌─────────────────────────────────────────────────────────────┐
│ FASE 2: TRANSFORMAÇÃO                                       │
└─────────────────────────────────────────────────────────────┘

1. Limpeza de Dados
   ├─ Remover caracteres especiais
   ├─ Normalizar encodings (UTF-8)
   ├─ Tratar valores nulos
   └─ Padronizar formatos de data

2. Validação de Qualidade
   ├─ Validar schemas Pydantic
   ├─ Verificar constraints de negócio
   ├─ Detectar outliers estatísticos
   ├─ Validar integridade referencial
   └─ Gerar relatório de qualidade

3. Enriquecimento
   ├─ Calcular densidade demográfica
   ├─ Calcular PIB per capita
   ├─ Adicionar metadados temporais
   └─ Criar índices de busca

4. Normalização
   ├─ Separar dimensões de fatos
   ├─ Criar chaves estrangeiras
   ├─ Remover duplicatas
   └─ Ordenar por hierarquia

5. Segregação
   ├─ Dados válidos → para carga
   ├─ Dados inválidos → para revisão
   └─ Logs de transformação
```

### 5.3 Fase de Carga (Load)

```
┌─────────────────────────────────────────────────────────────┐
│ FASE 3: CARGA                                               │
└─────────────────────────────────────────────────────────────┘

1. Preparação do Banco
   ├─ Verificar conexão
   ├─ Iniciar transação
   └─ Desabilitar triggers (se necessário)

2. Carga de Dimensões (ordem hierárquica)
   ├─ dim_regiao
   │  └─ Upsert por codigo_ibge
   │
   ├─ dim_estado
   │  ├─ Resolver FK id_regiao
   │  └─ Upsert por codigo_ibge
   │
   └─ dim_municipio
      ├─ Resolver FK id_estado
      └─ Upsert por codigo_ibge

3. Carga de Fatos
   ├─ fato_populacao
   │  ├─ Resolver FK id_municipio
   │  └─ Upsert por (id_municipio, ano)
   │
   ├─ fato_pib
   │  ├─ Resolver FK id_municipio
   │  └─ Upsert por (id_municipio, ano)
   │
   └─ fato_indicador_social
      ├─ Resolver FK id_municipio
      └─ Upsert por (id_municipio, ano, tipo_indicador)

4. Processamento em Lotes
   ├─ Batch size: 1000 registros
   ├─ Commit a cada lote
   └─ Rollback em caso de erro

5. Pós-Carga
   ├─ Atualizar estatísticas de tabela
   ├─ Recriar índices (se removidos)
   ├─ Habilitar triggers
   └─ Registrar metadados de execução

6. Validação Pós-Carga
   ├─ Verificar contagem de registros
   ├─ Validar integridade referencial
   └─ Executar queries de sanidade
```

---

## 6. Endpoints da API IBGE Utilizados

### 6.1 API de Localidades (v1)

| Endpoint | Descrição | Retorno |
|----------|-----------|---------|
| `/localidades/regioes` | Regiões do Brasil | 5 regiões |
| `/localidades/estados` | Estados e DF | 27 UFs |
| `/localidades/municipios` | Todos os municípios | ~5570 municípios |
| `/localidades/estados/{UF}/municipios` | Municípios de uma UF | Municípios da UF |

### 6.2 API de Agregados - SIDRA (v3)

| Agregado | Descrição | Variáveis Principais |
|----------|-----------|---------------------|
| 200 | População dos Censos | População total |
| 6579 | Estimativas populacionais | População estimada |
| 5938 | PIB Municipal | PIB a preços correntes |
| 37 | PIB per capita | PIB per capita |

**Exemplo de URL:**
```
https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/2021/variaveis/37?localidades=N6[all]
```

### 6.3 API de Projeções (v1)

| Endpoint | Descrição |
|----------|-----------|
| `/projecoes/populacao` | Projeção populacional do Brasil |
| `/projecoes/populacao/{localidade}` | Projeção para localidade específica |

---

## 7. Tecnologias e Dependências

### 7.1 requirements.txt

```txt
# Core ETL
python>=3.11
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.12.0

# API e HTTP
requests>=2.31.0
urllib3>=2.0.0
httpx>=0.25.0  # Alternativa assíncrona

# Validação
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Logging e Monitoring
python-json-logger>=2.0.0
structlog>=23.2.0

# Utilitários
python-dotenv>=1.0.0
pendulum>=3.0.0  # Manipulação avançada de datas
tenacity>=8.2.0  # Retry avançado

# Qualidade de Código
black>=23.12.0
flake8>=7.0.0
mypy>=1.8.0
pylint>=3.0.0

# Testes
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
pytest-asyncio>=0.21.0
faker>=21.0.0  # Geração de dados fake para testes

# Performance
pandas>=2.1.0  # Para análise e transformação de dados
numpy>=1.26.0

# Opcional - Observabilidade
sentry-sdk>=1.39.0
prometheus-client>=0.19.0
```

### 7.2 Variáveis de Ambiente (.env.example)

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ibge_socioeconomico
DB_USER=ibge_user
DB_PASSWORD=your_secure_password

# API Configuration
IBGE_API_BASE_URL=https://servicodados.ibge.gov.br/api/v1
IBGE_API_TIMEOUT=30
IBGE_API_MAX_RETRIES=3
IBGE_API_RATE_LIMIT_DELAY=0.5

# ETL Configuration
ETL_BATCH_SIZE=1000
ETL_LOG_LEVEL=INFO
ETL_DATA_DIR=./data
ETL_ENABLE_PARALLEL=false

# Monitoring (opcional)
SENTRY_DSN=
PROMETHEUS_PORT=9090
```

---

## 8. Estratégias de Qualidade e Testes

### 8.1 Testes Unitários

```python
"""
tests/unit/test_extractors.py

Exemplo de teste unitário para extratores.
"""

import pytest
from unittest.mock import Mock, patch
from src.extractors.localidades_extractor import LocalidadesExtractor

class TestLocalidadesExtractor:

    @pytest.fixture
    def mock_api_client(self):
        """Fixture de API client mockado."""
        client = Mock()
        client.get_municipios.return_value = [
            {'id': 3550308, 'nome': 'São Paulo'},
            {'id': 3304557, 'nome': 'Rio de Janeiro'}
        ]
        return client

    def test_extract_municipios_success(self, mock_api_client):
        """Testa extração bem-sucedida de municípios."""
        extractor = LocalidadesExtractor(mock_api_client)

        result = extractor.extract(tipo='municipios')

        assert len(result) == 2
        assert result[0]['nome'] == 'São Paulo'
        mock_api_client.get_municipios.assert_called_once()

    def test_extract_invalid_tipo(self, mock_api_client):
        """Testa erro com tipo inválido."""
        extractor = LocalidadesExtractor(mock_api_client)

        with pytest.raises(ValueError, match="Tipo inválido"):
            extractor.extract(tipo='invalid')
```

### 8.2 Testes de Integração

```python
"""
tests/integration/test_database.py

Teste de integração com banco de dados.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.base import Base
from src.models.municipio import DimMunicipio
from src.loaders.database_loader import DatabaseLoader

@pytest.fixture(scope='module')
def test_db():
    """Fixture de banco de dados de teste."""
    engine = create_engine('postgresql://test:test@localhost/test_db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

def test_load_municipios(test_db):
    """Testa carga de municípios no banco."""
    loader = DatabaseLoader(test_db)

    data = [
        {
            'codigo_ibge': 3550308,
            'nome': 'São Paulo',
            'id_estado': 1
        }
    ]

    loaded = loader.load_batch(
        data,
        DimMunicipio,
        unique_fields=['codigo_ibge']
    )

    assert loaded == 1

    # Verifica se foi persistido
    municipio = test_db.query(DimMunicipio).filter_by(
        codigo_ibge=3550308
    ).first()

    assert municipio is not None
    assert municipio.nome == 'São Paulo'
```

### 8.3 Testes de Qualidade de Dados

```python
"""
tests/unit/test_data_quality.py

Testes de qualidade de dados.
"""

import pytest
from src.transformers.data_validator import DataValidator, PopulacaoSchema

class TestDataQuality:

    def test_populacao_validation_success(self):
        """Testa validação bem-sucedida de população."""
        validator = DataValidator()

        data = [{
            'codigo_ibge': 3550308,
            'ano': 2021,
            'populacao_total': 12000000,
            'populacao_urbana': 11500000,
            'populacao_rural': 500000
        }]

        valid, invalid = validator.validate_batch(data, PopulacaoSchema)

        assert len(valid) == 1
        assert len(invalid) == 0

    def test_populacao_validation_inconsistent_totals(self):
        """Testa detecção de inconsistência em totais."""
        validator = DataValidator()

        data = [{
            'codigo_ibge': 3550308,
            'ano': 2021,
            'populacao_total': 12000000,
            'populacao_urbana': 10000000,
            'populacao_rural': 3000000  # Soma não bate
        }]

        valid, invalid = validator.validate_batch(data, PopulacaoSchema)

        assert len(valid) == 0
        assert len(invalid) == 1
```

---

## 9. Estratégias de Logging

### 9.1 Configuração de Logging Estruturado

```python
"""
src/utils/logger.py

Sistema de logging estruturado com suporte a JSON.
"""

import logging
import sys
from pythonjsonlogger import jsonlogger
from pathlib import Path

def setup_logger(
    name: str,
    log_level: str = 'INFO',
    log_file: str = None
) -> logging.Logger:
    """
    Configura logger estruturado.

    Args:
        name: Nome do logger
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        log_file: Caminho do arquivo de log (opcional)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Remove handlers existentes
    logger.handlers.clear()

    # Formato JSON estruturado
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para arquivo (se especificado)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
```

### 9.2 Exemplo de Log Estruturado

```json
{
  "asctime": "2025-12-14T10:30:45.123Z",
  "name": "ETLOrchestrator",
  "levelname": "INFO",
  "message": "Pipeline iniciado",
  "pipeline_id": "etl_20251214_103045",
  "user": "system",
  "environment": "production"
}
```

---

## 10. Estratégias de Tratamento de Erros

### 10.1 Hierarquia de Exceções Customizadas

```python
"""
src/exceptions.py

Hierarquia de exceções customizadas para o pipeline.
"""

class ETLException(Exception):
    """Exceção base para erros do ETL."""
    pass

class ExtractionError(ETLException):
    """Erro durante extração de dados."""
    pass

class TransformationError(ETLException):
    """Erro durante transformação de dados."""
    pass

class ValidationError(ETLException):
    """Erro de validação de dados."""
    pass

class LoadError(ETLException):
    """Erro durante carga de dados."""
    pass

class APIError(ETLException):
    """Erro na comunicação com API externa."""
    pass

class DatabaseError(ETLException):
    """Erro de banco de dados."""
    pass
```

### 10.2 Retry com Backoff Exponencial

```python
"""
src/utils/retry.py

Decorador de retry com backoff exponencial.
"""

from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import logging

def retry_with_backoff(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 60,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para retry com backoff exponencial.

    Args:
        max_attempts: Número máximo de tentativas
        min_wait: Tempo mínimo de espera (segundos)
        max_wait: Tempo máximo de espera (segundos)
        exceptions: Tupla de exceções para retry
    """
    def decorator(func):
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(min=min_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            reraise=True
        )
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            logger.debug(f"Executando {func.__name__}")
            return func(*args, **kwargs)

        return wrapper
    return decorator

# Uso:
# @retry_with_backoff(max_attempts=3, exceptions=(APIError,))
# def fetch_data_from_api():
#     ...
```

---

## 11. Próximos Passos de Implementação

### 11.1 Ordem Recomendada

1. **Setup Inicial** (Dia 1)
   - Criar estrutura de diretórios
   - Configurar ambiente virtual
   - Instalar dependências
   - Configurar banco de dados PostgreSQL

2. **Modelos de Dados** (Dia 2)
   - Implementar modelos SQLAlchemy
   - Criar migrations com Alembic
   - Testar schema no banco

3. **Módulo de Extração** (Dia 3-4)
   - Implementar cliente HTTP
   - Implementar extratores
   - Testar conexão com API IBGE

4. **Módulo de Transformação** (Dia 5-6)
   - Implementar validadores
   - Implementar transformers
   - Criar testes de qualidade

5. **Módulo de Carga** (Dia 7)
   - Implementar loaders
   - Testar upsert
   - Otimizar performance

6. **Orquestração** (Dia 8-9)
   - Implementar pipeline principal
   - Integrar todos os módulos
   - Adicionar logging e monitoramento

7. **Testes** (Dia 10-11)
   - Escrever testes unitários
   - Escrever testes de integração
   - Atingir cobertura > 80%

8. **Documentação e Deploy** (Dia 12)
   - Documentar API
   - Criar guia de deployment
   - Preparar para produção

### 11.2 Scripts de Inicialização

**scripts/create_database.py**
```python
"""Script para criar banco de dados e schema inicial."""

from sqlalchemy import create_engine
from src.models.base import Base
from config.settings import settings

def create_database():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✓ Banco de dados criado com sucesso!")

if __name__ == '__main__':
    create_database()
```

**scripts/run_pipeline.py**
```python
"""Script para executar pipeline ETL."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.pipeline.orchestrator import ETLOrchestrator
from src.extractors.ibge_api_client import IBGEAPIClient
from config.settings import settings

def main():
    # Configurar banco
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Configurar API client
    api_client = IBGEAPIClient()

    # Executar pipeline
    orchestrator = ETLOrchestrator(api_client, session)
    result = orchestrator.run_full_pipeline()

    print(f"Pipeline finalizado: {result['status']}")

if __name__ == '__main__':
    main()
```

---

## 12. Considerações de Performance

### 12.1 Otimizações Recomendadas

1. **Extração**
   - Usar conexões persistentes (Session Pooling)
   - Implementar cache para dados estáticos
   - Paralelizar requisições independentes

2. **Transformação**
   - Processar em chunks (pandas)
   - Usar operações vetorizadas
   - Evitar loops explícitos

3. **Carga**
   - Usar COPY ao invés de INSERT individual
   - Desabilitar índices durante carga massiva
   - Usar transações em lote

4. **Banco de Dados**
   - Criar índices apropriados
   - Particionar tabelas grandes por ano
   - Usar materialized views para agregações

### 12.2 Métricas de Performance Esperadas

- **Extração**: ~5570 municípios em < 2 minutos
- **Transformação**: ~100k registros/segundo
- **Carga**: ~10k registros/segundo com upsert
- **Pipeline completo**: < 30 minutos

---

## 13. Segurança e Boas Práticas

### 13.1 Segurança

- Nunca commitar .env ou credenciais
- Usar variáveis de ambiente para secrets
- Implementar prepared statements (SQLAlchemy já faz)
- Validar inputs antes de queries
- Usar SSL para conexões de banco

### 13.2 Boas Práticas

- Seguir PEP 8 (formatação com black)
- Type hints em todas as funções
- Docstrings em formato Google/NumPy
- Logging estruturado (JSON)
- Testes com cobertura > 80%
- Code review antes de merge
- Versionamento semântico

---

## 14. Referências e Recursos

### 14.1 Documentação Oficial IBGE

- [API de Localidades](https://servicodados.ibge.gov.br/api/docs/localidades)
- [API de Agregados (SIDRA)](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3)
- [API de Projeções](https://servicodados.ibge.gov.br/api/docs/projecoes)
- [Catálogo de APIs Governamentais](https://www.gov.br/conecta/catalogo/apis/registro-referencia-municipios)

### 14.2 Bibliotecas e Frameworks

- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Pytest](https://docs.pytest.org/)

---

## Conclusão

Esta arquitetura fornece uma base sólida, escalável e manutenível para o pipeline ETL de dados do IBGE. O design modular permite fácil extensão para novos tipos de dados, e as estratégias de qualidade, logging e tratamento de erros garantem robustez em produção.

**Próximo Passo:** Comece pela implementação dos modelos de dados e configuração do banco de dados. Uma vez que a base esteja sólida, os demais componentes se encaixarão naturalmente.

**Autor:** Backend Architect Expert
**Versão:** 1.0
**Data:** 2025-12-14
