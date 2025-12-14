"""
Carregamento de dados para PostgreSQL.
Utiliza SQLAlchemy para operações de banco de dados.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    BigInteger,
    String,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    text
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Metadata global para definição de tabelas
metadata = MetaData()

# ========== Definição das Tabelas ==========

dim_regiao = Table(
    "dim_regiao",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("sigla", String(2), nullable=False),
    Column("nome", String(50), nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

dim_estado = Table(
    "dim_estado",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("sigla", String(2), nullable=False, unique=True),
    Column("nome", String(50), nullable=False),
    Column("regiao_id", Integer, ForeignKey("dim_regiao.id"), nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

dim_municipio = Table(
    "dim_municipio",
    metadata,
    Column("id", Integer, primary_key=True),  # Código IBGE 7 dígitos
    Column("nome", String(100), nullable=False),
    Column("estado_id", Integer, ForeignKey("dim_estado.id"), nullable=False),
    Column("microrregiao_id", Integer),
    Column("microrregiao_nome", String(100)),
    Column("mesorregiao_id", Integer),
    Column("mesorregiao_nome", String(100)),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    Index("idx_municipio_estado", "estado_id"),
    Index("idx_municipio_nome", "nome")
)

fato_populacao = Table(
    "fato_populacao",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("municipio_id", Integer, ForeignKey("dim_municipio.id")),
    Column("estado_id", Integer, ForeignKey("dim_estado.id")),
    Column("ano", Integer, nullable=False),
    Column("populacao", BigInteger, nullable=False),
    Column("fonte", String(50), default="IBGE"),
    Column("extracted_at", DateTime, default=datetime.utcnow),
    UniqueConstraint("municipio_id", "estado_id", "ano", name="uq_populacao_loc_ano"),
    Index("idx_populacao_ano", "ano"),
    Index("idx_populacao_municipio", "municipio_id")
)

fato_pib = Table(
    "fato_pib",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("municipio_id", Integer, ForeignKey("dim_municipio.id")),
    Column("estado_id", Integer, ForeignKey("dim_estado.id")),
    Column("ano", Integer, nullable=False),
    Column("pib_total", Float),  # Em milhares de reais
    Column("pib_per_capita", Float),  # Em reais
    Column("pib_agropecuaria", Float),
    Column("pib_industria", Float),
    Column("pib_servicos", Float),
    Column("pib_administracao_publica", Float),
    Column("fonte", String(50), default="IBGE"),
    Column("extracted_at", DateTime, default=datetime.utcnow),
    UniqueConstraint("municipio_id", "estado_id", "ano", name="uq_pib_loc_ano"),
    Index("idx_pib_ano", "ano"),
    Index("idx_pib_municipio", "municipio_id")
)

metadata_extracao = Table(
    "metadata_extracao",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("tabela", String(50), nullable=False),
    Column("registros_extraidos", Integer),
    Column("registros_carregados", Integer),
    Column("registros_erro", Integer),
    Column("inicio", DateTime),
    Column("fim", DateTime),
    Column("status", String(20)),  # 'SUCCESS', 'ERROR', 'PARTIAL'
    Column("mensagem", String(500))
)


def create_tables(connection_string: Optional[str] = None) -> None:
    """
    Cria todas as tabelas no banco de dados.

    Args:
        connection_string: String de conexão (usa settings se não fornecida)
    """
    conn_str = connection_string or settings.database.connection_string
    engine = create_engine(conn_str)

    logger.info("Criando tabelas no banco de dados...")

    try:
        metadata.create_all(engine)
        logger.info("Tabelas criadas com sucesso")
    except SQLAlchemyError as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
        raise
    finally:
        engine.dispose()


class DatabaseLoader:
    """
    Carregador de dados para PostgreSQL.

    Implementa operações de upsert (INSERT ... ON CONFLICT UPDATE)
    para evitar duplicatas e manter dados atualizados.
    """

    def __init__(self, connection_string: Optional[str] = None):
        """
        Inicializa o loader.

        Args:
            connection_string: String de conexão PostgreSQL
        """
        self.connection_string = connection_string or settings.database.connection_string
        self.engine = create_engine(
            self.connection_string,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

        logger.info(f"DatabaseLoader inicializado | host={settings.database.host}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        """Fecha conexões do pool."""
        self.engine.dispose()
        logger.info("DatabaseLoader fechado")

    def _upsert(
        self,
        table: Table,
        data: List[Dict],
        conflict_columns: List[str],
        update_columns: List[str]
    ) -> int:
        """
        Executa upsert (INSERT ... ON CONFLICT DO UPDATE).

        Args:
            table: Tabela SQLAlchemy
            data: Lista de dicionários com dados
            conflict_columns: Colunas para detectar conflito
            update_columns: Colunas para atualizar em caso de conflito

        Returns:
            Número de registros afetados
        """
        if not data:
            return 0

        stmt = insert(table).values(data)

        update_dict = {col: stmt.excluded[col] for col in update_columns}
        update_dict["updated_at"] = datetime.utcnow()

        stmt = stmt.on_conflict_do_update(
            index_elements=conflict_columns,
            set_=update_dict
        )

        with self.engine.begin() as conn:
            result = conn.execute(stmt)

        return result.rowcount

    def load_regioes(self, df: pd.DataFrame) -> int:
        """
        Carrega dados de regiões.

        Args:
            df: DataFrame com colunas [id, sigla, nome]

        Returns:
            Número de registros carregados
        """
        logger.info(f"Carregando {len(df)} regiões")

        data = df[["id", "sigla", "nome"]].to_dict("records")

        count = self._upsert(
            table=dim_regiao,
            data=data,
            conflict_columns=["id"],
            update_columns=["sigla", "nome"]
        )

        logger.info(f"Regiões carregadas: {count}")
        return count

    def load_estados(self, df: pd.DataFrame) -> int:
        """
        Carrega dados de estados.

        Args:
            df: DataFrame com colunas [id, sigla, nome, regiao_id]

        Returns:
            Número de registros carregados
        """
        logger.info(f"Carregando {len(df)} estados")

        data = df[["id", "sigla", "nome", "regiao_id"]].to_dict("records")

        count = self._upsert(
            table=dim_estado,
            data=data,
            conflict_columns=["id"],
            update_columns=["sigla", "nome", "regiao_id"]
        )

        logger.info(f"Estados carregados: {count}")
        return count

    def load_municipios(self, df: pd.DataFrame) -> int:
        """
        Carrega dados de municípios.

        Args:
            df: DataFrame com dados de municípios

        Returns:
            Número de registros carregados
        """
        logger.info(f"Carregando {len(df)} municípios")

        # Preparar dados
        df_load = df.rename(columns={"uf_id": "estado_id"})

        columns = [
            "id", "nome", "estado_id",
            "microrregiao_id", "microrregiao_nome",
            "mesorregiao_id", "mesorregiao_nome"
        ]
        available_cols = [c for c in columns if c in df_load.columns]
        data = df_load[available_cols].to_dict("records")

        count = self._upsert(
            table=dim_municipio,
            data=data,
            conflict_columns=["id"],
            update_columns=[c for c in available_cols if c != "id"]
        )

        logger.info(f"Municípios carregados: {count}")
        return count

    def load_populacao(
        self,
        df: pd.DataFrame,
        nivel: str = "municipio"
    ) -> int:
        """
        Carrega dados de população.

        Args:
            df: DataFrame com dados populacionais
            nivel: 'municipio' ou 'estado'

        Returns:
            Número de registros carregados
        """
        logger.info(f"Carregando {len(df)} registros de população ({nivel})")

        # Preparar dados
        records = []
        for _, row in df.iterrows():
            record = {
                "ano": int(row["ano"]),
                "populacao": int(row["valor"]),
                "fonte": "IBGE",
                "extracted_at": datetime.utcnow()
            }

            if nivel == "municipio":
                record["municipio_id"] = int(row["localidade_id"])
                record["estado_id"] = None
            else:
                record["estado_id"] = int(row["localidade_id"])
                record["municipio_id"] = None

            records.append(record)

        # Inserir em lotes
        batch_size = settings.etl.batch_size
        total_loaded = 0

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            try:
                with self.engine.begin() as conn:
                    conn.execute(insert(fato_populacao).values(batch))
                total_loaded += len(batch)
            except SQLAlchemyError as e:
                logger.error(f"Erro ao carregar lote {i}: {str(e)}")

        logger.info(f"População carregada: {total_loaded} registros")
        return total_loaded

    def log_extraction(
        self,
        tabela: str,
        extraidos: int,
        carregados: int,
        erros: int,
        inicio: datetime,
        status: str,
        mensagem: str = ""
    ) -> None:
        """
        Registra metadados da extração.

        Args:
            tabela: Nome da tabela
            extraidos: Registros extraídos
            carregados: Registros carregados
            erros: Registros com erro
            inicio: Timestamp de início
            status: 'SUCCESS', 'ERROR', 'PARTIAL'
            mensagem: Mensagem adicional
        """
        record = {
            "tabela": tabela,
            "registros_extraidos": extraidos,
            "registros_carregados": carregados,
            "registros_erro": erros,
            "inicio": inicio,
            "fim": datetime.utcnow(),
            "status": status,
            "mensagem": mensagem[:500] if mensagem else None
        }

        with self.engine.begin() as conn:
            conn.execute(insert(metadata_extracao).values(record))

        logger.info(f"Extração registrada: {tabela} | status={status}")

    def execute_query(self, query: str) -> List[Dict]:
        """
        Executa query SQL e retorna resultados.

        Args:
            query: Query SQL

        Returns:
            Lista de dicionários com resultados
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]


# Exemplo de uso
if __name__ == "__main__":
    from src.utils.logger import setup_logger

    setup_logger(log_level="INFO")

    # Criar tabelas
    create_tables()

    # Testar loader
    with DatabaseLoader() as loader:
        # Verificar conexão
        result = loader.execute_query("SELECT 1 as test")
        print(f"Conexão OK: {result}")
