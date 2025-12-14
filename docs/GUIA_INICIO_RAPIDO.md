# Guia de Início Rápido - Pipeline ETL IBGE

## Introdução

Este guia fornece um passo a passo completo para começar a implementar o pipeline ETL de dados do IBGE, desde a configuração do ambiente até a primeira execução bem-sucedida.

**Tempo Estimado:** 4-6 horas
**Nível:** Intermediário a Avançado
**Pré-requisitos:** Python 3.11+, PostgreSQL 15+

---

## Sumário

1. [Setup do Ambiente](#1-setup-do-ambiente)
2. [Configuração do Banco de Dados](#2-configuração-do-banco-de-dados)
3. [Estrutura do Projeto](#3-estrutura-do-projeto)
4. [Implementação Mínima Viável](#4-implementação-mínima-viável)
5. [Primeira Execução](#5-primeira-execução)
6. [Validação e Testes](#6-validação-e-testes)
7. [Próximos Passos](#7-próximos-passos)

---

## 1. Setup do Ambiente

### 1.1 Pré-requisitos

**Software Necessário:**
```bash
# Verificar versões
python --version  # Deve ser 3.11+
psql --version    # Deve ser PostgreSQL 15+
git --version
```

**Instalar PostgreSQL (Windows):**
1. Baixar de: https://www.postgresql.org/download/windows/
2. Executar instalador
3. Anotar senha do usuário `postgres`
4. Adicionar ao PATH: `C:\Program Files\PostgreSQL\15\bin`

### 1.2 Criar Ambiente Virtual

```bash
# Navegar para diretório do projeto
cd E:\Portifolio-cienciadedados

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
# source venv/bin/activate

# Confirmar ativação (deve mostrar (venv) no prompt)
```

### 1.3 Instalar Dependências

```bash
# Criar requirements.txt
cat > requirements.txt << EOF
# Core
python>=3.11
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.12.0

# API e HTTP
requests>=2.31.0
urllib3>=2.0.0

# Validação
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Logging
python-json-logger>=2.0.0

# Utilitários
python-dotenv>=1.0.0
tenacity>=8.2.0

# Testes
pytest>=7.4.0
pytest-cov>=4.1.0
faker>=21.0.0

# Qualidade
black>=23.12.0
flake8>=7.0.0
EOF

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.4 Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ibge_socioeconomico
DB_USER=ibge_user
DB_PASSWORD=ibge_pass_123

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

# Environment
ENVIRONMENT=development
EOF

# Adicionar .env ao .gitignore
echo ".env" >> .gitignore
```

---

## 2. Configuração do Banco de Dados

### 2.1 Criar Usuário e Banco de Dados

```sql
-- Conectar como postgres
psql -U postgres

-- Criar usuário
CREATE USER ibge_user WITH PASSWORD 'ibge_pass_123';

-- Criar banco de dados
CREATE DATABASE ibge_socioeconomico OWNER ibge_user;

-- Conectar ao novo banco
\c ibge_socioeconomico

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE ibge_socioeconomico TO ibge_user;
GRANT ALL ON SCHEMA public TO ibge_user;

-- Sair
\q
```

### 2.2 Criar Script de Inicialização do Schema

Criar arquivo `scripts/init_database.sql`:

```sql
-- scripts/init_database.sql
-- Script de inicialização do schema do banco de dados

-- Criar função de atualização de timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- DIMENSÕES

-- Tabela dim_regiao
CREATE TABLE IF NOT EXISTS dim_regiao (
    id_regiao SERIAL PRIMARY KEY,
    codigo_ibge INTEGER UNIQUE NOT NULL,
    nome VARCHAR(50) NOT NULL,
    sigla VARCHAR(2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_regiao_codigo ON dim_regiao(codigo_ibge);

CREATE TRIGGER update_dim_regiao_updated_at
    BEFORE UPDATE ON dim_regiao
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Tabela dim_estado
CREATE TABLE IF NOT EXISTS dim_estado (
    id_estado SERIAL PRIMARY KEY,
    id_regiao INTEGER NOT NULL REFERENCES dim_regiao(id_regiao) ON DELETE RESTRICT,
    codigo_ibge INTEGER UNIQUE NOT NULL,
    nome VARCHAR(50) NOT NULL,
    sigla VARCHAR(2) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_codigo_ibge_estado CHECK (codigo_ibge BETWEEN 11 AND 53),
    CONSTRAINT chk_sigla_uppercase CHECK (sigla = UPPER(sigla))
);

CREATE INDEX IF NOT EXISTS idx_estado_codigo ON dim_estado(codigo_ibge);
CREATE INDEX IF NOT EXISTS idx_estado_regiao ON dim_estado(id_regiao);

CREATE TRIGGER update_dim_estado_updated_at
    BEFORE UPDATE ON dim_estado
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Tabela dim_municipio
CREATE TABLE IF NOT EXISTS dim_municipio (
    id_municipio SERIAL PRIMARY KEY,
    id_estado INTEGER NOT NULL REFERENCES dim_estado(id_estado) ON DELETE RESTRICT,
    codigo_ibge INTEGER UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    area_km2 DECIMAL(12,4),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    capital BOOLEAN DEFAULT FALSE,
    codigo_mesorregiao INTEGER,
    codigo_microrregiao INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_codigo_ibge_municipio CHECK (codigo_ibge BETWEEN 1000000 AND 9999999),
    CONSTRAINT chk_area_positiva CHECK (area_km2 IS NULL OR area_km2 > 0),
    CONSTRAINT chk_latitude_valida CHECK (latitude IS NULL OR (latitude BETWEEN -90 AND 90)),
    CONSTRAINT chk_longitude_valida CHECK (longitude IS NULL OR (longitude BETWEEN -180 AND 180))
);

CREATE INDEX IF NOT EXISTS idx_municipio_codigo ON dim_municipio(codigo_ibge);
CREATE INDEX IF NOT EXISTS idx_municipio_estado ON dim_municipio(id_estado);
CREATE INDEX IF NOT EXISTS idx_municipio_nome ON dim_municipio(nome);

CREATE TRIGGER update_dim_municipio_updated_at
    BEFORE UPDATE ON dim_municipio
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- FATOS

-- Tabela fato_populacao
CREATE TABLE IF NOT EXISTS fato_populacao (
    id_populacao SERIAL PRIMARY KEY,
    id_municipio INTEGER NOT NULL REFERENCES dim_municipio(id_municipio) ON DELETE CASCADE,
    ano INTEGER NOT NULL,
    populacao_total BIGINT NOT NULL,
    populacao_urbana BIGINT,
    populacao_rural BIGINT,
    densidade_demografica DECIMAL(12,4),
    tipo_dado VARCHAR(20) CHECK (tipo_dado IN ('CENSO', 'ESTIMATIVA', 'PROJECAO')),
    fonte_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_populacao_municipio_ano UNIQUE(id_municipio, ano),
    CONSTRAINT chk_ano_valido CHECK (ano BETWEEN 1900 AND 2100),
    CONSTRAINT chk_populacao_positiva CHECK (populacao_total >= 0)
);

CREATE INDEX IF NOT EXISTS idx_populacao_municipio ON fato_populacao(id_municipio);
CREATE INDEX IF NOT EXISTS idx_populacao_ano ON fato_populacao(ano);

CREATE TRIGGER update_fato_populacao_updated_at
    BEFORE UPDATE ON fato_populacao
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Tabela fato_pib
CREATE TABLE IF NOT EXISTS fato_pib (
    id_pib SERIAL PRIMARY KEY,
    id_municipio INTEGER NOT NULL REFERENCES dim_municipio(id_municipio) ON DELETE CASCADE,
    ano INTEGER NOT NULL,
    pib_total DECIMAL(18,2) NOT NULL,
    pib_per_capita DECIMAL(12,2),
    vab_agropecuaria DECIMAL(18,2),
    vab_industria DECIMAL(18,2),
    vab_servicos DECIMAL(18,2),
    impostos_liquidos DECIMAL(18,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_pib_municipio_ano UNIQUE(id_municipio, ano),
    CONSTRAINT chk_pib_ano_valido CHECK (ano BETWEEN 1900 AND 2100),
    CONSTRAINT chk_pib_total_positivo CHECK (pib_total >= 0)
);

CREATE INDEX IF NOT EXISTS idx_pib_municipio ON fato_pib(id_municipio);
CREATE INDEX IF NOT EXISTS idx_pib_ano ON fato_pib(ano);

CREATE TRIGGER update_fato_pib_updated_at
    BEFORE UPDATE ON fato_pib
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Tabela metadata_extracao
CREATE TABLE IF NOT EXISTS metadata_extracao (
    id_extracao SERIAL PRIMARY KEY,
    tipo_dados VARCHAR(50) NOT NULL,
    pipeline_id VARCHAR(100),
    data_inicio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_fim TIMESTAMP,
    data_extracao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('SUCESSO', 'ERRO', 'PARCIAL', 'EM_PROGRESSO')),
    registros_extraidos INTEGER,
    registros_carregados INTEGER,
    tempo_execucao_segundos DECIMAL(10,2),
    mensagem_erro TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metadata_tipo ON metadata_extracao(tipo_dados);
CREATE INDEX IF NOT EXISTS idx_metadata_data ON metadata_extracao(data_extracao);
CREATE INDEX IF NOT EXISTS idx_metadata_status ON metadata_extracao(status);

-- Inserir dados iniciais (regiões)
INSERT INTO dim_regiao (codigo_ibge, nome, sigla) VALUES
(1, 'Norte', 'N'),
(2, 'Nordeste', 'NE'),
(3, 'Sudeste', 'SE'),
(4, 'Sul', 'S'),
(5, 'Centro-Oeste', 'CO')
ON CONFLICT (codigo_ibge) DO NOTHING;
```

### 2.3 Executar Script de Inicialização

```bash
# Executar script SQL
psql -U ibge_user -d ibge_socioeconomico -f scripts/init_database.sql

# Verificar tabelas criadas
psql -U ibge_user -d ibge_socioeconomico -c "\dt"
```

---

## 3. Estrutura do Projeto

### 3.1 Criar Estrutura de Diretórios

```bash
# Criar estrutura completa
mkdir -p ibge-etl-pipeline/{config,src/{extractors,transformers,loaders,models,utils,pipeline},tests/{unit,integration,fixtures},scripts,logs,data/{raw,processed,backups},docs,migrations}

# Criar arquivos __init__.py
touch ibge-etl-pipeline/config/__init__.py
touch ibge-etl-pipeline/src/__init__.py
touch ibge-etl-pipeline/src/extractors/__init__.py
touch ibge-etl-pipeline/src/transformers/__init__.py
touch ibge-etl-pipeline/src/loaders/__init__.py
touch ibge-etl-pipeline/src/models/__init__.py
touch ibge-etl-pipeline/src/utils/__init__.py
touch ibge-etl-pipeline/src/pipeline/__init__.py
touch ibge-etl-pipeline/tests/__init__.py

# Criar .gitkeep para diretórios vazios
touch ibge-etl-pipeline/logs/.gitkeep
touch ibge-etl-pipeline/data/raw/.gitkeep
touch ibge-etl-pipeline/data/processed/.gitkeep
touch ibge-etl-pipeline/data/backups/.gitkeep
```

### 3.2 Verificar Estrutura

```bash
# Windows
tree ibge-etl-pipeline /F

# Linux/Mac
tree ibge-etl-pipeline
```

Resultado esperado:
```
ibge-etl-pipeline/
├── config/
│   └── __init__.py
├── src/
│   ├── __init__.py
│   ├── extractors/
│   ├── transformers/
│   ├── loaders/
│   ├── models/
│   ├── utils/
│   └── pipeline/
├── tests/
├── scripts/
├── logs/
├── data/
├── docs/
├── .env
└── requirements.txt
```

---

## 4. Implementação Mínima Viável

### 4.1 Criar Arquivos de Configuração

Copiar os arquivos de exemplo da documentação:

1. `config/settings.py` - Do EXEMPLOS_IMPLEMENTACAO.md seção 1.1
2. `config/database.py` - Do EXEMPLOS_IMPLEMENTACAO.md seção 1.2
3. `config/logging_config.py` - Do EXEMPLOS_IMPLEMENTACAO.md seção 1.3

### 4.2 Criar Modelos Básicos

Copiar os modelos:

1. `src/models/base.py` - Do EXEMPLOS_IMPLEMENTACAO.md seção 2.1
2. `src/models/municipio.py` - Do EXEMPLOS_IMPLEMENTACAO.md seção 2.2

### 4.3 Criar Cliente API

Copiar:

1. `src/extractors/ibge_api_client.py` - Do EXEMPLOS_IMPLEMENTACAO.md seção 3.1

### 4.4 Criar Extrator Simples

Copiar:

1. `src/extractors/localidades_extractor.py` - Do EXEMPLOS_IMPLEMENTACAO.md seção 4.1

---

## 5. Primeira Execução

### 5.1 Criar Script de Teste

Criar `scripts/test_extraction.py`:

```python
"""
scripts/test_extraction.py

Script simples para testar extração de dados.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from config.logging_config import setup_logging
from config.database import get_db_session
from src.extractors.ibge_api_client import IBGEAPIClient
from src.extractors.localidades_extractor import LocalidadesExtractor
from src.models.municipio import DimRegiao, DimEstado
from sqlalchemy.dialects.postgresql import insert
import logging


def main():
    """Função principal."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("TESTE DE EXTRAÇÃO E CARGA - IBGE ETL")
    logger.info("=" * 60)

    try:
        # 1. Testar conexão com API
        logger.info("Testando conexão com API IBGE...")
        with IBGEAPIClient() as api_client:
            # Testar endpoint simples
            regioes = api_client.get_regioes()
            logger.info(f"✓ API acessível. {len(regioes)} regiões obtidas.")

            # 2. Extrair dados
            logger.info("\nExtraindo dados de localidades...")
            extractor = LocalidadesExtractor(api_client)

            # Extrair regiões
            regioes_data = extractor.extract_regioes()
            logger.info(f"✓ {len(regioes_data)} regiões extraídas")

            # Extrair estados
            estados_data = extractor.extract_estados()
            logger.info(f"✓ {len(estados_data)} estados extraídos")

            # 3. Carregar no banco
            logger.info("\nCarregando dados no banco de dados...")

            with get_db_session() as session:
                # Carregar regiões
                stmt = insert(DimRegiao).values(regioes_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['codigo_ibge'],
                    set_={'nome': stmt.excluded.nome}
                )
                session.execute(stmt)
                logger.info(f"✓ Regiões carregadas")

                # Carregar estados
                # Mapear codigo_regiao para id_regiao
                for estado in estados_data:
                    regiao = session.query(DimRegiao).filter_by(
                        codigo_ibge=estado['codigo_regiao']
                    ).first()

                    if regiao:
                        estado['id_regiao'] = regiao.id_regiao
                        del estado['codigo_regiao']

                stmt = insert(DimEstado).values(estados_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['codigo_ibge'],
                    set_={'nome': stmt.excluded.nome}
                )
                session.execute(stmt)
                logger.info(f"✓ Estados carregados")

                session.commit()

            # 4. Verificar dados no banco
            logger.info("\nVerificando dados no banco...")
            with get_db_session() as session:
                count_regioes = session.query(DimRegiao).count()
                count_estados = session.query(DimEstado).count()

                logger.info(f"Regiões no banco: {count_regioes}")
                logger.info(f"Estados no banco: {count_estados}")

                # Listar alguns estados
                logger.info("\nPrimeiros 5 estados:")
                estados = session.query(DimEstado).limit(5).all()
                for estado in estados:
                    logger.info(
                        f"  - {estado.nome} ({estado.sigla}) - "
                        f"Região: {estado.regiao.nome}"
                    )

        logger.info("\n" + "=" * 60)
        logger.info("✓ TESTE CONCLUÍDO COM SUCESSO!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n✗ ERRO: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### 5.2 Executar Teste

```bash
# Executar script de teste
python scripts/test_extraction.py
```

**Saída Esperada:**
```
============================================================
TESTE DE EXTRAÇÃO E CARGA - IBGE ETL
============================================================
Testando conexão com API IBGE...
✓ API acessível. 5 regiões obtidas.

Extraindo dados de localidades...
✓ 5 regiões extraídas
✓ 27 estados extraídos

Carregando dados no banco de dados...
✓ Regiões carregadas
✓ Estados carregadas

Verificando dados no banco...
Regiões no banco: 5
Estados no banco: 27

Primeiros 5 estados:
  - Acre (AC) - Região: Norte
  - Alagoas (AL) - Região: Nordeste
  - Amapá (AP) - Região: Norte
  - Amazonas (AM) - Região: Norte
  - Bahia (BA) - Região: Nordeste

============================================================
✓ TESTE CONCLUÍDO COM SUCESSO!
============================================================
```

---

## 6. Validação e Testes

### 6.1 Verificar Dados no Banco

```sql
-- Conectar ao banco
psql -U ibge_user -d ibge_socioeconomico

-- Consultar regiões
SELECT * FROM dim_regiao;

-- Consultar estados
SELECT
    e.codigo_ibge,
    e.sigla,
    e.nome,
    r.nome AS regiao
FROM dim_estado e
INNER JOIN dim_regiao r ON e.id_regiao = r.id_regiao
ORDER BY e.nome;

-- Contar registros
SELECT
    'dim_regiao' AS tabela,
    COUNT(*) AS total
FROM dim_regiao
UNION ALL
SELECT
    'dim_estado' AS tabela,
    COUNT(*) AS total
FROM dim_estado;
```

### 6.2 Criar Teste Unitário Simples

Criar `tests/unit/test_api_client.py`:

```python
"""
tests/unit/test_api_client.py

Testes unitários do cliente API.
"""

import pytest
from src.extractors.ibge_api_client import IBGEAPIClient


class TestIBGEAPIClient:
    """Testes do cliente API IBGE."""

    @pytest.fixture
    def client(self):
        """Fixture de cliente API."""
        return IBGEAPIClient()

    def test_get_regioes(self, client):
        """Testa busca de regiões."""
        regioes = client.get_regioes()

        assert isinstance(regioes, list)
        assert len(regioes) == 5

        # Verifica estrutura
        for regiao in regioes:
            assert 'id' in regiao
            assert 'nome' in regiao
            assert 'sigla' in regiao

    def test_get_estados(self, client):
        """Testa busca de estados."""
        estados = client.get_estados()

        assert isinstance(estados, list)
        assert len(estados) == 27

        # Verifica estrutura
        for estado in estados:
            assert 'id' in estado
            assert 'nome' in estado
            assert 'sigla' in estado
            assert 'regiao' in estado

    def test_get_estado_especifico(self, client):
        """Testa busca de estado específico."""
        estado = client.get_estado('SP')

        assert estado['id'] == 35
        assert estado['sigla'] == 'SP'
        assert estado['nome'] == 'São Paulo'
        assert estado['regiao']['id'] == 3  # Sudeste
```

### 6.3 Executar Testes

```bash
# Executar testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=src --cov-report=html

# Ver relatório de cobertura
# Abrir htmlcov/index.html no navegador
```

---

## 7. Próximos Passos

### 7.1 Roadmap de Implementação

**Semana 1-2: Módulos Básicos**
- [x] Configuração do ambiente
- [x] Setup do banco de dados
- [x] Modelos de dados básicos
- [x] Cliente API
- [x] Extrator de localidades
- [ ] Extrator de população
- [ ] Extrator de PIB

**Semana 3-4: Transformação e Validação**
- [ ] Implementar validadores Pydantic
- [ ] Implementar transformers
- [ ] Testes de qualidade de dados
- [ ] Detecção de outliers

**Semana 5-6: Carga e Otimização**
- [ ] Implementar loaders
- [ ] Otimizar processamento em lote
- [ ] Implementar upsert eficiente
- [ ] Adicionar índices otimizados

**Semana 7-8: Orquestração e Testes**
- [ ] Implementar orchestrator
- [ ] Adicionar logging estruturado
- [ ] Testes de integração
- [ ] Testes end-to-end

**Semana 9-10: Produção e Monitoramento**
- [ ] Configurar CI/CD
- [ ] Adicionar monitoramento
- [ ] Documentar deployment
- [ ] Preparar para produção

### 7.2 Funcionalidades Avançadas

**Performance:**
- Processamento paralelo de municípios
- Cache de dados estáticos
- Otimização de queries

**Monitoramento:**
- Integração com Sentry (erros)
- Métricas Prometheus
- Dashboards Grafana

**Automação:**
- Agendamento com Airflow ou Prefect
- Notificações por email/Slack
- Backup automático

### 7.3 Recursos de Aprendizado

**Documentação Oficial:**
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [API IBGE](https://servicodados.ibge.gov.br/api/docs/)

**Tutoriais Recomendados:**
- [Real Python - SQLAlchemy](https://realpython.com/python-sqlalchemy/)
- [Full Stack Python - ETL](https://www.fullstackpython.com/etl.html)
- [Towards Data Science - ETL Best Practices](https://towardsdatascience.com/tagged/etl)

---

## 8. Troubleshooting

### 8.1 Problemas Comuns

**Erro: "ModuleNotFoundError: No module named 'config'"**
```bash
# Solução: Adicionar diretório raiz ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou no script Python:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Erro: "connection refused" ao conectar PostgreSQL**
```bash
# Verificar se PostgreSQL está rodando
# Windows:
sc query postgresql-x64-15

# Iniciar serviço:
net start postgresql-x64-15

# Linux:
sudo systemctl status postgresql
sudo systemctl start postgresql
```

**Erro: "peer authentication failed"**
```bash
# Editar pg_hba.conf
# Trocar 'peer' por 'md5' ou 'trust'

# Localização (Linux):
# /etc/postgresql/15/main/pg_hba.conf

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

**Erro de timeout na API IBGE**
```python
# Aumentar timeout nas configurações
# .env
IBGE_API_TIMEOUT=60
IBGE_API_MAX_RETRIES=5
```

### 8.2 Comandos Úteis

```bash
# Ver logs em tempo real
tail -f logs/etl_pipeline.log

# Limpar cache Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Resetar banco de dados
psql -U postgres -c "DROP DATABASE ibge_socioeconomico;"
psql -U postgres -c "CREATE DATABASE ibge_socioeconomico OWNER ibge_user;"
psql -U ibge_user -d ibge_socioeconomico -f scripts/init_database.sql

# Verificar espaço usado pelo banco
psql -U ibge_user -d ibge_socioeconomico -c "SELECT pg_size_pretty(pg_database_size('ibge_socioeconomico'));"
```

---

## Conclusão

Você agora tem uma base sólida para construir o pipeline ETL completo. Os próximos passos envolvem expandir gradualmente a funcionalidade, sempre mantendo a qualidade do código e a cobertura de testes.

**Dicas Finais:**
1. Commit frequente no Git
2. Escrever testes antes de implementar features
3. Documentar decisões arquiteturais
4. Revisar logs regularmente
5. Otimizar apenas quando necessário (premature optimization is evil)

**Boa sorte com a implementação!**

---

**Autor:** Backend Architect Expert
**Data:** 2025-12-14
**Versão:** 1.0
