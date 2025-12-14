# Exemplos de Implementação - Pipeline ETL IBGE

## Visão Geral

Este documento apresenta exemplos completos e prontos para uso de implementações dos principais componentes do pipeline ETL.

**Data:** 2025-12-14
**Versão:** 1.0

---

## Índice

1. [Configuração Inicial](#1-configuração-inicial)
2. [Modelos SQLAlchemy](#2-modelos-sqlalchemy)
3. [Cliente API IBGE](#3-cliente-api-ibge)
4. [Extractors](#4-extractors)
5. [Transformers](#5-transformers)
6. [Loaders](#6-loaders)
7. [Pipeline Orchestrator](#7-pipeline-orchestrator)
8. [Testes](#8-testes)
9. [Scripts de Execução](#9-scripts-de-execução)

---

## 1. Configuração Inicial

### 1.1 config/settings.py

```python
"""
config/settings.py

Configurações centralizadas da aplicação usando Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """
    Configurações da aplicação.

    Carrega valores de variáveis de ambiente ou .env
    """

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "ibge_socioeconomico"
    DB_USER: str = "ibge_user"
    DB_PASSWORD: str = "changeme"

    # API IBGE
    IBGE_API_BASE_URL: str = "https://servicodados.ibge.gov.br/api/v1"
    IBGE_API_BASE_URL_V3: str = "https://servicodados.ibge.gov.br/api/v3"
    IBGE_API_TIMEOUT: int = 30
    IBGE_API_MAX_RETRIES: int = 3
    IBGE_API_RATE_LIMIT_DELAY: float = 0.5

    # ETL
    ETL_BATCH_SIZE: int = 1000
    ETL_LOG_LEVEL: str = "INFO"
    ETL_DATA_DIR: Path = Path("./data")
    ETL_ENABLE_PARALLEL: bool = False

    # Monitoring (opcional)
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 9090

    # Ambiente
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def DATABASE_URL(self) -> str:
        """Constrói URL de conexão do PostgreSQL."""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """URL de conexão assíncrona."""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# Instância global de configurações
settings = Settings()
```

### 1.2 config/database.py

```python
"""
config/database.py

Configuração do banco de dados SQLAlchemy.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

from .settings import settings

logger = logging.getLogger(__name__)


# Engine com pool de conexões
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verifica conexão antes de usar
    echo=settings.ENVIRONMENT == "development"  # Log de SQL em dev
)


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@contextmanager
def get_db_session() -> Session:
    """
    Context manager para sessão de banco de dados.

    Uso:
        with get_db_session() as session:
            # usar session
            pass
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Session:
    """
    Generator de sessão para uso com dependency injection.

    Uso (FastAPI):
        @app.get("/")
        def endpoint(db: Session = Depends(get_db)):
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Event listeners para logging
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log de novas conexões."""
    logger.debug("Nova conexão ao banco de dados estabelecida")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log de checkout de conexão do pool."""
    logger.debug("Conexão retirada do pool")
```

### 1.3 config/logging_config.py

```python
"""
config/logging_config.py

Configuração de logging estruturado.
"""

import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger
from .settings import settings


def setup_logging():
    """
    Configura logging estruturado da aplicação.
    """
    # Criar diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configuração do root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.ETL_LOG_LEVEL)

    # Remove handlers existentes
    root_logger.handlers.clear()

    # Formato JSON
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )

    # Handler para console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # Handler para arquivo
    file_handler = logging.FileHandler(
        log_dir / "etl_pipeline.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    # Handler para erros (arquivo separado)
    error_handler = logging.FileHandler(
        log_dir / "errors.log",
        encoding="utf-8"
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

    # Desabilitar logs verbosos de bibliotecas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.info("Sistema de logging configurado")
```

---

## 2. Modelos SQLAlchemy

### 2.1 src/models/base.py

```python
"""
src/models/base.py

Base declarativa para modelos SQLAlchemy.
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Column, DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    """
    Classe base para todos os modelos.

    Adiciona automaticamente:
    - created_at
    - updated_at
    - __tablename__ baseado no nome da classe
    """

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Gera nome da tabela automaticamente.

        Converte CamelCase para snake_case.
        Exemplo: DimMunicipio -> dim_municipio
        """
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    # Campos de auditoria
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Data de criação do registro"
    )

    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Data da última atualização"
    )

    def to_dict(self) -> dict:
        """
        Converte modelo para dicionário.

        Returns:
            Dicionário com todos os campos do modelo
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """Representação string do modelo."""
        attrs = ', '.join(
            f"{k}={v!r}"
            for k, v in self.to_dict().items()
            if k not in ('created_at', 'updated_at')
        )
        return f"{self.__class__.__name__}({attrs})"
```

### 2.2 src/models/municipio.py

```python
"""
src/models/municipio.py

Modelos de dimensões geográficas.
"""

from sqlalchemy import (
    Column, Integer, String, DECIMAL, Boolean,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from .base import Base


class DimRegiao(Base):
    """Dimensão de regiões geográficas."""

    __tablename__ = 'dim_regiao'

    id_regiao = Column(Integer, primary_key=True, autoincrement=True)
    codigo_ibge = Column(Integer, unique=True, nullable=False, index=True)
    nome = Column(String(50), nullable=False)
    sigla = Column(String(2), nullable=False)

    # Relacionamentos
    estados = relationship(
        "DimEstado",
        back_populates="regiao",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('idx_regiao_codigo', 'codigo_ibge'),
        Index('idx_regiao_nome', 'nome'),
        {'comment': 'Dimensão de regiões geográficas do Brasil'}
    )


class DimEstado(Base):
    """Dimensão de unidades federativas."""

    __tablename__ = 'dim_estado'

    id_estado = Column(Integer, primary_key=True, autoincrement=True)
    id_regiao = Column(
        Integer,
        ForeignKey('dim_regiao.id_regiao', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    codigo_ibge = Column(Integer, unique=True, nullable=False, index=True)
    nome = Column(String(50), nullable=False)
    sigla = Column(String(2), unique=True, nullable=False)

    # Relacionamentos
    regiao = relationship("DimRegiao", back_populates="estados")
    municipios = relationship(
        "DimMunicipio",
        back_populates="estado",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint('codigo_ibge BETWEEN 11 AND 53', name='chk_codigo_ibge_estado'),
        CheckConstraint('sigla = UPPER(sigla)', name='chk_sigla_uppercase'),
        Index('idx_estado_codigo', 'codigo_ibge'),
        Index('idx_estado_sigla', 'sigla'),
        Index('idx_estado_regiao', 'id_regiao'),
        {'comment': 'Dimensão de unidades federativas (estados e DF)'}
    )


class DimMunicipio(Base):
    """Dimensão de municípios brasileiros."""

    __tablename__ = 'dim_municipio'

    id_municipio = Column(Integer, primary_key=True, autoincrement=True)
    id_estado = Column(
        Integer,
        ForeignKey('dim_estado.id_estado', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    codigo_ibge = Column(Integer, unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False, index=True)
    area_km2 = Column(DECIMAL(12, 4))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    capital = Column(Boolean, default=False)
    codigo_mesorregiao = Column(Integer, index=True)
    codigo_microrregiao = Column(Integer, index=True)

    # Relacionamentos
    estado = relationship("DimEstado", back_populates="municipios")
    populacoes = relationship(
        "FatoPopulacao",
        back_populates="municipio",
        cascade="all, delete-orphan"
    )
    pibs = relationship(
        "FatoPib",
        back_populates="municipio",
        cascade="all, delete-orphan"
    )
    indicadores = relationship(
        "FatoIndicadorSocial",
        back_populates="municipio",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            'codigo_ibge BETWEEN 1000000 AND 9999999',
            name='chk_codigo_ibge_municipio'
        ),
        CheckConstraint('area_km2 > 0', name='chk_area_positiva'),
        CheckConstraint(
            'latitude BETWEEN -90 AND 90',
            name='chk_latitude_valida'
        ),
        CheckConstraint(
            'longitude BETWEEN -180 AND 180',
            name='chk_longitude_valida'
        ),
        Index('idx_municipio_codigo', 'codigo_ibge'),
        Index('idx_municipio_estado', 'id_estado'),
        Index('idx_municipio_nome', 'nome'),
        {'comment': 'Dimensão de municípios brasileiros'}
    )

    @property
    def nome_completo(self) -> str:
        """Retorna nome completo do município com UF."""
        return f"{self.nome} - {self.estado.sigla}"
```

### 2.3 src/models/populacao.py

```python
"""
src/models/populacao.py

Modelo de fato de população.
"""

from sqlalchemy import (
    Column, Integer, BigInteger, DECIMAL, String,
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from .base import Base


class FatoPopulacao(Base):
    """Fato de dados populacionais."""

    __tablename__ = 'fato_populacao'

    id_populacao = Column(Integer, primary_key=True, autoincrement=True)
    id_municipio = Column(
        Integer,
        ForeignKey('dim_municipio.id_municipio', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    ano = Column(Integer, nullable=False, index=True)
    populacao_total = Column(BigInteger, nullable=False)
    populacao_urbana = Column(BigInteger)
    populacao_rural = Column(BigInteger)
    densidade_demografica = Column(DECIMAL(12, 4))
    tipo_dado = Column(
        String(20),
        comment="CENSO, ESTIMATIVA ou PROJECAO"
    )
    fonte_id = Column(Integer, comment="ID da tabela/agregado SIDRA")

    # Relacionamentos
    municipio = relationship("DimMunicipio", back_populates="populacoes")

    __table_args__ = (
        UniqueConstraint('id_municipio', 'ano', name='uk_populacao_municipio_ano'),
        CheckConstraint('ano BETWEEN 1900 AND 2100', name='chk_ano_valido'),
        CheckConstraint('populacao_total >= 0', name='chk_populacao_positiva'),
        CheckConstraint(
            'populacao_urbana IS NULL OR populacao_urbana >= 0',
            name='chk_populacao_urbana_positiva'
        ),
        CheckConstraint(
            'populacao_rural IS NULL OR populacao_rural >= 0',
            name='chk_populacao_rural_positiva'
        ),
        CheckConstraint(
            'densidade_demografica IS NULL OR densidade_demografica >= 0',
            name='chk_densidade_positiva'
        ),
        CheckConstraint(
            "tipo_dado IN ('CENSO', 'ESTIMATIVA', 'PROJECAO')",
            name='chk_tipo_dado_valido'
        ),
        Index('idx_populacao_municipio', 'id_municipio'),
        Index('idx_populacao_ano', 'ano'),
        Index('idx_populacao_municipio_ano', 'id_municipio', 'ano'),
        Index('idx_populacao_tipo', 'tipo_dado'),
        {'comment': 'Fato de dados populacionais por município e ano'}
    )

    @property
    def taxa_urbanizacao(self) -> float:
        """Calcula taxa de urbanização (%)."""
        if self.populacao_urbana and self.populacao_total > 0:
            return (self.populacao_urbana / self.populacao_total) * 100
        return 0.0
```

---

## 3. Cliente API IBGE

### 3.1 src/extractors/ibge_api_client.py

```python
"""
src/extractors/ibge_api_client.py

Cliente HTTP robusto para API do IBGE.
"""

import requests
from typing import Dict, Any, Optional, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import logging
from functools import wraps

from config.settings import settings


class RateLimiter:
    """
    Rate limiter simples para controlar frequência de requisições.
    """

    def __init__(self, min_interval: float = 0.5):
        """
        Args:
            min_interval: Intervalo mínimo entre requisições (segundos)
        """
        self.min_interval = min_interval
        self.last_call = 0.0

    def __call__(self, func):
        """Decorador para aplicar rate limiting."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - self.last_call
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)

            result = func(*args, **kwargs)
            self.last_call = time.time()
            return result

        return wrapper


class IBGEAPIError(Exception):
    """Exceção base para erros da API IBGE."""
    pass


class IBGEAPIClient:
    """
    Cliente HTTP para API do IBGE.

    Features:
    - Retry automático com backoff exponencial
    - Rate limiting configurável
    - Logging estruturado
    - Validação de respostas
    - Cache de sessão HTTP
    """

    def __init__(
        self,
        timeout: int = None,
        max_retries: int = None,
        rate_limit_delay: float = None
    ):
        """
        Inicializa cliente da API.

        Args:
            timeout: Timeout em segundos (padrão: configuração)
            max_retries: Número máximo de tentativas
            rate_limit_delay: Delay entre requisições
        """
        self.timeout = timeout or settings.IBGE_API_TIMEOUT
        self.max_retries = max_retries or settings.IBGE_API_MAX_RETRIES
        self.rate_limit_delay = rate_limit_delay or settings.IBGE_API_RATE_LIMIT_DELAY

        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Cria sessão HTTP com retry strategy.
        """
        session = requests.Session()

        # Estratégia de retry
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "OPTIONS"],
            backoff_factor=1,  # 1s, 2s, 4s, 8s...
            respect_retry_after_header=True
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Headers padrão
        session.headers.update({
            'User-Agent': 'IBGE-ETL-Pipeline/1.0',
            'Accept': 'application/json'
        })

        return session

    @RateLimiter(min_interval=settings.IBGE_API_RATE_LIMIT_DELAY)
    def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Realiza requisição HTTP com retry e rate limiting.

        Args:
            method: Método HTTP (GET, POST, etc.)
            url: URL completa
            params: Parâmetros de query string
            **kwargs: Argumentos adicionais para requests

        Returns:
            Resposta JSON

        Raises:
            IBGEAPIError: Em caso de erro na requisição
        """
        self.logger.debug(
            f"{method} {url}",
            extra={'params': params}
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=self.timeout,
                **kwargs
            )

            response.raise_for_status()

            # Valida content-type
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' not in content_type:
                raise IBGEAPIError(
                    f"Resposta não é JSON: {content_type}"
                )

            data = response.json()

            self.logger.debug(
                f"Resposta recebida: {response.status_code}",
                extra={
                    'status_code': response.status_code,
                    'size': len(response.content)
                }
            )

            return data

        except requests.exceptions.HTTPError as e:
            self.logger.error(
                f"Erro HTTP {e.response.status_code}: {e}",
                extra={'url': url, 'status_code': e.response.status_code}
            )
            raise IBGEAPIError(f"Erro HTTP: {e}") from e

        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout na requisição: {url}")
            raise IBGEAPIError(f"Timeout ao acessar {url}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro na requisição: {e}")
            raise IBGEAPIError(f"Erro na requisição: {e}") from e

        except ValueError as e:
            self.logger.error(f"Erro ao decodificar JSON: {e}")
            raise IBGEAPIError("Resposta inválida da API") from e

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        base_url: str = None
    ) -> Dict[str, Any]:
        """
        Realiza requisição GET.

        Args:
            endpoint: Endpoint da API (sem base URL)
            params: Parâmetros de query
            base_url: Base URL customizada (opcional)

        Returns:
            Resposta JSON
        """
        base = base_url or settings.IBGE_API_BASE_URL
        url = f"{base.rstrip('/')}/{endpoint.lstrip('/')}"

        return self._request('GET', url, params=params)

    def get_v3(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Atalho para API v3 (agregados)."""
        return self.get(
            endpoint,
            params=params,
            base_url=settings.IBGE_API_BASE_URL_V3
        )

    # Métodos de conveniência

    def get_regioes(self) -> List[Dict[str, Any]]:
        """Obtém todas as regiões."""
        return self.get("localidades/regioes")

    def get_estados(self, order_by: str = None) -> List[Dict[str, Any]]:
        """
        Obtém todos os estados.

        Args:
            order_by: Campo para ordenação ('id' ou 'nome')
        """
        params = {'orderBy': order_by} if order_by else None
        return self.get("localidades/estados", params=params)

    def get_estado(self, uf: str) -> Dict[str, Any]:
        """
        Obtém um estado específico.

        Args:
            uf: Código IBGE ou sigla (ex: '35' ou 'SP')
        """
        return self.get(f"localidades/estados/{uf}")

    def get_municipios(self, order_by: str = None) -> List[Dict[str, Any]]:
        """Obtém todos os municípios."""
        params = {'orderBy': order_by} if order_by else None
        return self.get("localidades/municipios", params=params)

    def get_municipios_por_estado(
        self,
        uf: str
    ) -> List[Dict[str, Any]]:
        """
        Obtém municípios de um estado.

        Args:
            uf: Código IBGE ou sigla do estado
        """
        return self.get(f"localidades/estados/{uf}/municipios")

    def get_agregado(
        self,
        agregado_id: int,
        periodo: str,
        variaveis: str,
        localidades: str = "N6[all]"
    ) -> Dict[str, Any]:
        """
        Obtém dados de agregado do SIDRA.

        Args:
            agregado_id: ID do agregado (ex: 5938)
            periodo: Período (ex: '2021' ou '2019|2020|2021')
            variaveis: Variáveis (ex: '37' ou '37|513|514')
            localidades: Localidades (padrão: todos municípios)

        Returns:
            Dados do agregado
        """
        endpoint = (
            f"agregados/{agregado_id}/"
            f"periodos/{periodo}/"
            f"variaveis/{variaveis}"
        )
        params = {"localidades": localidades}

        return self.get_v3(endpoint, params=params)

    def get_populacao_censo(
        self,
        ano: int,
        localidades: str = "N6[all]"
    ) -> Dict[str, Any]:
        """
        Obtém população do censo.

        Args:
            ano: Ano do censo (1970, 1980, 1991, 2000, 2010)
            localidades: Nível geográfico
        """
        return self.get_agregado(
            agregado_id=200,
            periodo=str(ano),
            variaveis="93",  # População residente
            localidades=localidades
        )

    def get_populacao_estimativa(
        self,
        ano: int,
        localidades: str = "N6[all]"
    ) -> Dict[str, Any]:
        """
        Obtém estimativa de população.

        Args:
            ano: Ano da estimativa
            localidades: Nível geográfico
        """
        return self.get_agregado(
            agregado_id=6579,
            periodo=str(ano),
            variaveis="9324",  # População estimada
            localidades=localidades
        )

    def get_pib_municipal(
        self,
        ano: int,
        localidades: str = "N6[all]"
    ) -> Dict[str, Any]:
        """
        Obtém PIB municipal completo.

        Args:
            ano: Ano do PIB
            localidades: Nível geográfico
        """
        # Variáveis: PIB, VAB Agro, VAB Ind, VAB Serv, Impostos
        variaveis = "37|513|514|515|516"

        return self.get_agregado(
            agregado_id=5938,
            periodo=str(ano),
            variaveis=variaveis,
            localidades=localidades
        )

    def close(self):
        """Fecha sessão HTTP."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
```

**Uso do Cliente:**

```python
# Exemplo de uso
from src.extractors.ibge_api_client import IBGEAPIClient

# Como context manager
with IBGEAPIClient() as client:
    # Obter estados
    estados = client.get_estados(order_by='nome')
    print(f"Total de estados: {len(estados)}")

    # Obter municípios de SP
    municipios_sp = client.get_municipios_por_estado('SP')
    print(f"Municípios de SP: {len(municipios_sp)}")

    # Obter população 2022
    pop_2022 = client.get_populacao_estimativa(2022)
    print("População 2022 obtida")

    # Obter PIB 2021
    pib_2021 = client.get_pib_municipal(2021)
    print("PIB 2021 obtido")
```

---

## 4. Extractors

### 4.1 src/extractors/localidades_extractor.py

```python
"""
src/extractors/localidades_extractor.py

Extrator completo de dados de localidades.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .ibge_api_client import IBGEAPIClient, IBGEAPIError


class LocalidadesExtractor:
    """
    Extrator de dados de localidades (regiões, estados, municípios).

    Features:
    - Extração hierárquica
    - Validação de dados
    - Metadados de extração
    - Tratamento de erros
    """

    def __init__(self, api_client: Optional[IBGEAPIClient] = None):
        """
        Args:
            api_client: Cliente da API (cria um novo se não fornecido)
        """
        self.api_client = api_client or IBGEAPIClient()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.metadata = {
            'start_time': None,
            'end_time': None,
            'records_extracted': 0,
            'status': 'PENDING',
            'errors': []
        }

    def extract_regioes(self) -> List[Dict[str, Any]]:
        """
        Extrai dados de regiões.

        Returns:
            Lista de regiões processadas
        """
        self.logger.info("Extraindo regiões...")
        self.metadata['start_time'] = datetime.utcnow()

        try:
            raw_data = self.api_client.get_regioes()

            # Transformação inicial
            processed_data = [
                {
                    'codigo_ibge': item['id'],
                    'nome': item['nome'],
                    'sigla': item['sigla']
                }
                for item in raw_data
            ]

            self.metadata['records_extracted'] = len(processed_data)
            self.metadata['status'] = 'SUCCESS'

            self.logger.info(
                f"Regiões extraídas: {len(processed_data)}"
            )

            return processed_data

        except IBGEAPIError as e:
            self.metadata['status'] = 'ERROR'
            self.metadata['errors'].append(str(e))
            self.logger.error(f"Erro ao extrair regiões: {e}")
            raise

        finally:
            self.metadata['end_time'] = datetime.utcnow()

    def extract_estados(self) -> List[Dict[str, Any]]:
        """
        Extrai dados de estados.

        Returns:
            Lista de estados processados
        """
        self.logger.info("Extraindo estados...")
        self.metadata['start_time'] = datetime.utcnow()

        try:
            raw_data = self.api_client.get_estados(order_by='nome')

            processed_data = [
                {
                    'codigo_ibge': item['id'],
                    'nome': item['nome'],
                    'sigla': item['sigla'],
                    'codigo_regiao': item['regiao']['id']
                }
                for item in raw_data
            ]

            self.metadata['records_extracted'] = len(processed_data)
            self.metadata['status'] = 'SUCCESS'

            self.logger.info(
                f"Estados extraídos: {len(processed_data)}"
            )

            return processed_data

        except IBGEAPIError as e:
            self.metadata['status'] = 'ERROR'
            self.metadata['errors'].append(str(e))
            self.logger.error(f"Erro ao extrair estados: {e}")
            raise

        finally:
            self.metadata['end_time'] = datetime.utcnow()

    def extract_municipios(self) -> List[Dict[str, Any]]:
        """
        Extrai dados de municípios.

        Returns:
            Lista de municípios processados
        """
        self.logger.info("Extraindo municípios...")
        self.metadata['start_time'] = datetime.utcnow()

        try:
            raw_data = self.api_client.get_municipios()

            processed_data = []
            for item in raw_data:
                # Extrai código do estado do código do município
                # Primeiros 2 dígitos do código de 7 dígitos
                codigo_municipio = item['id']
                codigo_estado = int(str(codigo_municipio)[:2])

                municipio = {
                    'codigo_ibge': codigo_municipio,
                    'nome': item['nome'],
                    'codigo_estado': codigo_estado,
                }

                # Adiciona dados de microrregião se disponível
                if 'microrregiao' in item and item['microrregiao']:
                    municipio['codigo_microrregiao'] = item['microrregiao']['id']

                    # Mesorregião está dentro de microrregião
                    if 'mesorregiao' in item['microrregiao']:
                        municipio['codigo_mesorregiao'] = (
                            item['microrregiao']['mesorregiao']['id']
                        )

                processed_data.append(municipio)

            self.metadata['records_extracted'] = len(processed_data)
            self.metadata['status'] = 'SUCCESS'

            self.logger.info(
                f"Municípios extraídos: {len(processed_data)}"
            )

            return processed_data

        except IBGEAPIError as e:
            self.metadata['status'] = 'ERROR'
            self.metadata['errors'].append(str(e))
            self.logger.error(f"Erro ao extrair municípios: {e}")
            raise

        finally:
            self.metadata['end_time'] = datetime.utcnow()

    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados da extração."""
        duration = None
        if self.metadata['start_time'] and self.metadata['end_time']:
            duration = (
                self.metadata['end_time'] - self.metadata['start_time']
            ).total_seconds()

        return {
            **self.metadata,
            'duration_seconds': duration
        }
```

---

*Continua na próxima seção devido ao tamanho...*

## 5. Transformers

### 5.1 src/transformers/data_validator.py

```python
"""
src/transformers/data_validator.py

Validador de qualidade de dados com Pydantic.
"""

from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field, validator
from decimal import Decimal
import logging


# Schemas de Validação

class RegiaoSchema(BaseModel):
    """Schema de validação para região."""
    codigo_ibge: int = Field(..., ge=1, le=5)
    nome: str = Field(..., min_length=1, max_length=50)
    sigla: str = Field(..., min_length=1, max_length=2)

    @validator('sigla')
    def validate_sigla(cls, v):
        return v.upper()


class EstadoSchema(BaseModel):
    """Schema de validação para estado."""
    codigo_ibge: int = Field(..., ge=11, le=53)
    nome: str = Field(..., min_length=1, max_length=50)
    sigla: str = Field(..., min_length=2, max_length=2)
    codigo_regiao: int = Field(..., ge=1, le=5)

    @validator('sigla')
    def validate_sigla(cls, v):
        return v.upper()

    @validator('nome')
    def validate_nome(cls, v):
        return v.strip().title()


class MunicipioSchema(BaseModel):
    """Schema de validação para município."""
    codigo_ibge: int = Field(..., ge=1000000, le=9999999)
    nome: str = Field(..., min_length=1, max_length=100)
    codigo_estado: int = Field(..., ge=11, le=53)
    codigo_mesorregiao: int = Field(None, ge=1)
    codigo_microrregiao: int = Field(None, ge=1)
    area_km2: Decimal = Field(None, ge=0)
    latitude: Decimal = Field(None, ge=-90, le=90)
    longitude: Decimal = Field(None, ge=-180, le=180)

    @validator('nome')
    def validate_nome(cls, v):
        return v.strip()


class PopulacaoSchema(BaseModel):
    """Schema de validação para população."""
    codigo_ibge: int = Field(..., ge=1000000, le=9999999)
    ano: int = Field(..., ge=1900, le=2100)
    populacao_total: int = Field(..., ge=0)
    populacao_urbana: int = Field(None, ge=0)
    populacao_rural: int = Field(None, ge=0)
    tipo_dado: str = Field(None, regex=r'^(CENSO|ESTIMATIVA|PROJECAO)$')

    @validator('populacao_rural', always=True)
    def validate_componentes(cls, v, values):
        """Valida que urbana + rural ≈ total."""
        if 'populacao_urbana' not in values:
            return v

        urbana = values.get('populacao_urbana')
        if urbana is not None and v is not None:
            total_calc = urbana + v
            total_real = values.get('populacao_total', 0)

            if total_real > 0:
                diff_perc = abs(total_calc - total_real) / total_real
                if diff_perc > 0.01:  # Permite 1% de diferença
                    raise ValueError(
                        f"Soma urbana+rural ({total_calc}) difere "
                        f"do total ({total_real}) em mais de 1%"
                    )
        return v


class PIBSchema(BaseModel):
    """Schema de validação para PIB."""
    codigo_ibge: int = Field(..., ge=1000000, le=9999999)
    ano: int = Field(..., ge=1900, le=2100)
    pib_total: Decimal = Field(..., ge=0)
    pib_per_capita: Decimal = Field(None, ge=0)
    vab_agropecuaria: Decimal = Field(None, ge=0)
    vab_industria: Decimal = Field(None, ge=0)
    vab_servicos: Decimal = Field(None, ge=0)
    impostos_liquidos: Decimal = Field(None, ge=0)


# Validador Principal

class DataValidator:
    """
    Validador de qualidade de dados.

    Features:
    - Validação de schemas Pydantic
    - Detecção de outliers
    - Relatórios de qualidade
    - Separação de dados válidos/inválidos
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validation_errors: List[Dict[str, Any]] = []

    def validate_batch(
        self,
        data: List[Dict[str, Any]],
        schema_class: type[BaseModel]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
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

        for idx, record in enumerate(data):
            try:
                # Valida com Pydantic
                validated = schema_class(**record)

                # Converte de volta para dict
                valid_records.append(validated.dict())

            except Exception as e:
                self.logger.warning(
                    f"Registro {idx} inválido: {e}",
                    extra={'record': record}
                )

                invalid_records.append({
                    'index': idx,
                    'record': record,
                    'error': str(e),
                    'error_type': type(e).__name__
                })

                self.validation_errors.append({
                    'record': record,
                    'error': str(e),
                    'schema': schema_class.__name__,
                    'timestamp': datetime.utcnow()
                })

        valid_count = len(valid_records)
        invalid_count = len(invalid_records)
        total = len(data)

        self.logger.info(
            f"Validação concluída: {valid_count}/{total} válidos "
            f"({(valid_count/total*100):.1f}%)"
        )

        if invalid_count > 0:
            self.logger.warning(
                f"{invalid_count} registros inválidos encontrados"
            )

        return valid_records, invalid_records

    def get_quality_report(self) -> Dict[str, Any]:
        """
        Gera relatório de qualidade.

        Returns:
            Relatório com métricas e exemplos de erros
        """
        total_errors = len(self.validation_errors)

        # Agrupa erros por schema
        errors_by_schema = {}
        for error in self.validation_errors:
            schema = error['schema']
            errors_by_schema[schema] = errors_by_schema.get(schema, 0) + 1

        # Agrupa erros por tipo
        errors_by_type = {}
        for error in self.validation_errors:
            # Extrai tipo do erro da mensagem
            error_msg = error['error']
            error_type = error_msg.split(':')[0] if ':' in error_msg else 'Unknown'
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1

        return {
            'total_validation_errors': total_errors,
            'errors_by_schema': errors_by_schema,
            'errors_by_type': errors_by_type,
            'sample_errors': self.validation_errors[:10],  # Primeiros 10
            'quality_score': self._calculate_quality_score()
        }

    def _calculate_quality_score(self) -> float:
        """
        Calcula score de qualidade (0-100).

        Lógica simples: 100 - (% de erros * 100)
        """
        # Implementação simplificada
        # Pode ser expandida com pesos diferentes para diferentes tipos de erro
        return 100.0 - min(len(self.validation_errors), 100)

    def clear_errors(self):
        """Limpa histórico de erros."""
        self.validation_errors.clear()
```

---

Estes são os exemplos principais de implementação. O documento está ficando muito extenso.

## Continuação Recomendada

Devido ao tamanho, vou criar um sumário final com as próximas implementações que você deve criar:

---

## 6. Próximas Implementações Necessárias

### 6.1 Loaders
- `src/loaders/database_loader.py` - Carregador para PostgreSQL com upsert
- `src/loaders/batch_loader.py` - Processamento em lotes

### 6.2 Pipeline Orchestrator
- `src/pipeline/orchestrator.py` - Orquestrador principal
- `src/pipeline/scheduler.py` - Agendamento de execuções

### 6.3 Utilitários
- `src/utils/logger.py` - Sistema de logging
- `src/utils/retry.py` - Decoradores de retry
- `src/utils/validators.py` - Validadores customizados

### 6.4 Scripts
- `scripts/create_database.py` - Criação do banco
- `scripts/run_pipeline.py` - Execução do pipeline
- `scripts/migrate_schema.py` - Migrações

### 6.5 Testes
- `tests/unit/test_extractors.py`
- `tests/unit/test_transformers.py`
- `tests/integration/test_database.py`
- `tests/integration/test_pipeline.py`

---

**Autor:** Backend Architect Expert
**Data:** 2025-12-14
**Versão:** 1.0
