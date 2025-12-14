# Schema do Banco de Dados - Pipeline ETL IBGE

## Visão Geral

Este documento detalha o schema do banco de dados PostgreSQL para armazenamento de dados socioeconômicos do IBGE.

**Database:** `ibge_socioeconomico`
**Schema:** `public`
**Modelo:** Star Schema (dimensional)

---

## Modelo Dimensional

### Padrão Escolhido: Star Schema

**Justificativa:**
- Consultas mais rápidas (menos JOINs)
- Facilita análises OLAP
- Melhor performance para agregações
- Mais intuitivo para usuários finais

```
            ┌──────────────────┐
            │   dim_regiao     │
            └────────┬─────────┘
                     │
                     │ 1:N
                     ▼
            ┌──────────────────┐
            │   dim_estado     │
            └────────┬─────────┘
                     │
                     │ 1:N
                     ▼
            ┌──────────────────┐
            │  dim_municipio   │◄──────┐
            └────────┬─────────┘       │
                     │                 │
         ┌───────────┼───────────┐     │
         │           │           │     │
         ▼           ▼           ▼     │
┌─────────────┐ ┌─────────┐ ┌──────────────────┐
│fato_populacao│ │fato_pib │ │fato_indicador    │
└─────────────┘ └─────────┘ └──────────────────┘
```

---

## Tabelas Dimensões

### 1. dim_regiao

**Descrição:** Dimensão de regiões geográficas do Brasil (Norte, Nordeste, Sul, Sudeste, Centro-Oeste).

**DDL:**
```sql
CREATE TABLE dim_regiao (
    -- Chave primária
    id_regiao SERIAL PRIMARY KEY,

    -- Atributos
    codigo_ibge INTEGER UNIQUE NOT NULL,
    nome VARCHAR(50) NOT NULL,
    sigla VARCHAR(2) NOT NULL,

    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comentários
COMMENT ON TABLE dim_regiao IS 'Dimensão de regiões geográficas do Brasil';
COMMENT ON COLUMN dim_regiao.codigo_ibge IS 'Código oficial IBGE da região (1-5)';
COMMENT ON COLUMN dim_regiao.nome IS 'Nome completo da região';
COMMENT ON COLUMN dim_regiao.sigla IS 'Sigla da região (N, NE, S, SE, CO)';

-- Índices
CREATE UNIQUE INDEX idx_regiao_codigo ON dim_regiao(codigo_ibge);
CREATE INDEX idx_regiao_nome ON dim_regiao(nome);

-- Trigger de atualização
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_dim_regiao_updated_at
    BEFORE UPDATE ON dim_regiao
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Dados Esperados:**
```sql
INSERT INTO dim_regiao (codigo_ibge, nome, sigla) VALUES
(1, 'Norte', 'N'),
(2, 'Nordeste', 'NE'),
(3, 'Sudeste', 'SE'),
(4, 'Sul', 'S'),
(5, 'Centro-Oeste', 'CO');
```

**Volume:** 5 registros

---

### 2. dim_estado

**Descrição:** Dimensão de unidades federativas (estados e Distrito Federal).

**DDL:**
```sql
CREATE TABLE dim_estado (
    -- Chave primária
    id_estado SERIAL PRIMARY KEY,

    -- Chave estrangeira
    id_regiao INTEGER NOT NULL REFERENCES dim_regiao(id_regiao) ON DELETE RESTRICT,

    -- Atributos
    codigo_ibge INTEGER UNIQUE NOT NULL,
    nome VARCHAR(50) NOT NULL,
    sigla VARCHAR(2) UNIQUE NOT NULL,

    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_sigla_uppercase CHECK (sigla = UPPER(sigla)),
    CONSTRAINT chk_codigo_ibge_estado CHECK (codigo_ibge BETWEEN 11 AND 53)
);

-- Comentários
COMMENT ON TABLE dim_estado IS 'Dimensão de unidades federativas (estados e DF)';
COMMENT ON COLUMN dim_estado.codigo_ibge IS 'Código oficial IBGE do estado (2 dígitos)';
COMMENT ON COLUMN dim_estado.id_regiao IS 'FK para região à qual o estado pertence';

-- Índices
CREATE UNIQUE INDEX idx_estado_codigo ON dim_estado(codigo_ibge);
CREATE UNIQUE INDEX idx_estado_sigla ON dim_estado(sigla);
CREATE INDEX idx_estado_regiao ON dim_estado(id_regiao);
CREATE INDEX idx_estado_nome ON dim_estado(nome);

-- Trigger de atualização
CREATE TRIGGER update_dim_estado_updated_at
    BEFORE UPDATE ON dim_estado
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Volume:** 27 registros (26 estados + 1 DF)

---

### 3. dim_municipio

**Descrição:** Dimensão de municípios brasileiros.

**DDL:**
```sql
CREATE TABLE dim_municipio (
    -- Chave primária
    id_municipio SERIAL PRIMARY KEY,

    -- Chave estrangeira
    id_estado INTEGER NOT NULL REFERENCES dim_estado(id_estado) ON DELETE RESTRICT,

    -- Atributos
    codigo_ibge INTEGER UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    area_km2 DECIMAL(12,4),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),

    -- Dados adicionais
    capital BOOLEAN DEFAULT FALSE,
    codigo_mesorregiao INTEGER,
    codigo_microrregiao INTEGER,

    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_codigo_ibge_municipio CHECK (codigo_ibge BETWEEN 1000000 AND 9999999),
    CONSTRAINT chk_area_positiva CHECK (area_km2 > 0),
    CONSTRAINT chk_latitude_valida CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT chk_longitude_valida CHECK (longitude BETWEEN -180 AND 180)
);

-- Comentários
COMMENT ON TABLE dim_municipio IS 'Dimensão de municípios brasileiros';
COMMENT ON COLUMN dim_municipio.codigo_ibge IS 'Código oficial IBGE do município (7 dígitos)';
COMMENT ON COLUMN dim_municipio.area_km2 IS 'Área territorial em km²';
COMMENT ON COLUMN dim_municipio.capital IS 'Indica se é capital estadual';
COMMENT ON COLUMN dim_municipio.codigo_mesorregiao IS 'Código da mesorregião';
COMMENT ON COLUMN dim_municipio.codigo_microrregiao IS 'Código da microrregião';

-- Índices
CREATE UNIQUE INDEX idx_municipio_codigo ON dim_municipio(codigo_ibge);
CREATE INDEX idx_municipio_estado ON dim_municipio(id_estado);
CREATE INDEX idx_municipio_nome ON dim_municipio USING gin(to_tsvector('portuguese', nome));
CREATE INDEX idx_municipio_capital ON dim_municipio(capital) WHERE capital = TRUE;
CREATE INDEX idx_municipio_mesorregiao ON dim_municipio(codigo_mesorregiao);
CREATE INDEX idx_municipio_microrregiao ON dim_municipio(codigo_microrregiao);

-- Índice espacial (se usar PostGIS)
-- CREATE INDEX idx_municipio_location ON dim_municipio USING gist(
--     ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
-- );

-- Trigger de atualização
CREATE TRIGGER update_dim_municipio_updated_at
    BEFORE UPDATE ON dim_municipio
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Volume:** ~5.570 registros

---

## Tabelas Fato

### 4. fato_populacao

**Descrição:** Fato de dados populacionais por município e ano.

**DDL:**
```sql
CREATE TABLE fato_populacao (
    -- Chave primária
    id_populacao SERIAL PRIMARY KEY,

    -- Chave estrangeira
    id_municipio INTEGER NOT NULL REFERENCES dim_municipio(id_municipio) ON DELETE CASCADE,

    -- Dimensões
    ano INTEGER NOT NULL,

    -- Medidas
    populacao_total BIGINT NOT NULL,
    populacao_urbana BIGINT,
    populacao_rural BIGINT,
    densidade_demografica DECIMAL(12,4),

    -- Metadados
    tipo_dado VARCHAR(20) CHECK (tipo_dado IN ('CENSO', 'ESTIMATIVA', 'PROJECAO')),
    fonte_id INTEGER,

    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT uk_populacao_municipio_ano UNIQUE(id_municipio, ano),
    CONSTRAINT chk_ano_valido CHECK (ano BETWEEN 1900 AND 2100),
    CONSTRAINT chk_populacao_positiva CHECK (populacao_total >= 0),
    CONSTRAINT chk_populacao_urbana_positiva CHECK (populacao_urbana IS NULL OR populacao_urbana >= 0),
    CONSTRAINT chk_populacao_rural_positiva CHECK (populacao_rural IS NULL OR populacao_rural >= 0),
    CONSTRAINT chk_densidade_positiva CHECK (densidade_demografica IS NULL OR densidade_demografica >= 0),

    -- Validação de consistência: urbana + rural = total (com margem de 1%)
    CONSTRAINT chk_populacao_consistente CHECK (
        populacao_urbana IS NULL OR
        populacao_rural IS NULL OR
        ABS((populacao_urbana + populacao_rural) - populacao_total) <= populacao_total * 0.01
    )
);

-- Comentários
COMMENT ON TABLE fato_populacao IS 'Fato de dados populacionais por município e ano';
COMMENT ON COLUMN fato_populacao.tipo_dado IS 'Tipo de dado populacional: CENSO (oficial), ESTIMATIVA ou PROJECAO';
COMMENT ON COLUMN fato_populacao.densidade_demografica IS 'Densidade demográfica (hab/km²)';
COMMENT ON COLUMN fato_populacao.fonte_id IS 'ID da agregação/tabela SIDRA fonte';

-- Índices
CREATE INDEX idx_populacao_municipio ON fato_populacao(id_municipio);
CREATE INDEX idx_populacao_ano ON fato_populacao(ano DESC);
CREATE INDEX idx_populacao_municipio_ano ON fato_populacao(id_municipio, ano DESC);
CREATE INDEX idx_populacao_tipo ON fato_populacao(tipo_dado);
CREATE INDEX idx_populacao_total ON fato_populacao(populacao_total DESC);

-- Particionamento por ano (opcional para grandes volumes)
-- CREATE TABLE fato_populacao_2020 PARTITION OF fato_populacao
--     FOR VALUES FROM (2020) TO (2021);

-- Trigger de atualização
CREATE TRIGGER update_fato_populacao_updated_at
    BEFORE UPDATE ON fato_populacao
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para calcular densidade automaticamente
CREATE OR REPLACE FUNCTION calcular_densidade_demografica()
RETURNS TRIGGER AS $$
DECLARE
    area_municipio DECIMAL(12,4);
BEGIN
    -- Busca área do município
    SELECT area_km2 INTO area_municipio
    FROM dim_municipio
    WHERE id_municipio = NEW.id_municipio;

    -- Calcula densidade se área disponível
    IF area_municipio IS NOT NULL AND area_municipio > 0 THEN
        NEW.densidade_demografica := NEW.populacao_total / area_municipio;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calcular_densidade
    BEFORE INSERT OR UPDATE ON fato_populacao
    FOR EACH ROW
    WHEN (NEW.densidade_demografica IS NULL)
    EXECUTE FUNCTION calcular_densidade_demografica();
```

**Volume Estimado:** ~100.000 registros (5.570 municípios x ~20 anos)

---

### 5. fato_pib

**Descrição:** Fato de dados de PIB municipal.

**DDL:**
```sql
CREATE TABLE fato_pib (
    -- Chave primária
    id_pib SERIAL PRIMARY KEY,

    -- Chave estrangeira
    id_municipio INTEGER NOT NULL REFERENCES dim_municipio(id_municipio) ON DELETE CASCADE,

    -- Dimensões
    ano INTEGER NOT NULL,

    -- Medidas principais (em milhares de Reais)
    pib_total DECIMAL(18,2) NOT NULL,
    pib_per_capita DECIMAL(12,2),

    -- Valor Adicionado Bruto por setor (em milhares de Reais)
    vab_agropecuaria DECIMAL(18,2),
    vab_industria DECIMAL(18,2),
    vab_servicos DECIMAL(18,2),
    vab_administracao_publica DECIMAL(18,2),

    -- Impostos
    impostos_liquidos DECIMAL(18,2),

    -- Percentuais setoriais
    perc_agropecuaria DECIMAL(5,2),
    perc_industria DECIMAL(5,2),
    perc_servicos DECIMAL(5,2),

    -- Metadados
    fonte_id INTEGER,

    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT uk_pib_municipio_ano UNIQUE(id_municipio, ano),
    CONSTRAINT chk_pib_ano_valido CHECK (ano BETWEEN 1900 AND 2100),
    CONSTRAINT chk_pib_total_positivo CHECK (pib_total >= 0),
    CONSTRAINT chk_pib_per_capita_positivo CHECK (pib_per_capita IS NULL OR pib_per_capita >= 0),
    CONSTRAINT chk_vab_positivo CHECK (
        (vab_agropecuaria IS NULL OR vab_agropecuaria >= 0) AND
        (vab_industria IS NULL OR vab_industria >= 0) AND
        (vab_servicos IS NULL OR vab_servicos >= 0)
    ),
    CONSTRAINT chk_percentuais_validos CHECK (
        (perc_agropecuaria IS NULL OR perc_agropecuaria BETWEEN 0 AND 100) AND
        (perc_industria IS NULL OR perc_industria BETWEEN 0 AND 100) AND
        (perc_servicos IS NULL OR perc_servicos BETWEEN 0 AND 100)
    )
);

-- Comentários
COMMENT ON TABLE fato_pib IS 'Fato de PIB municipal por ano';
COMMENT ON COLUMN fato_pib.pib_total IS 'PIB total em milhares de Reais correntes';
COMMENT ON COLUMN fato_pib.pib_per_capita IS 'PIB per capita em Reais correntes';
COMMENT ON COLUMN fato_pib.vab_agropecuaria IS 'Valor Adicionado Bruto da Agropecuária';
COMMENT ON COLUMN fato_pib.impostos_liquidos IS 'Impostos sobre produtos líquidos de subsídios';

-- Índices
CREATE INDEX idx_pib_municipio ON fato_pib(id_municipio);
CREATE INDEX idx_pib_ano ON fato_pib(ano DESC);
CREATE INDEX idx_pib_municipio_ano ON fato_pib(id_municipio, ano DESC);
CREATE INDEX idx_pib_total ON fato_pib(pib_total DESC);
CREATE INDEX idx_pib_per_capita ON fato_pib(pib_per_capita DESC);

-- Trigger de atualização
CREATE TRIGGER update_fato_pib_updated_at
    BEFORE UPDATE ON fato_pib
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para calcular PIB per capita automaticamente
CREATE OR REPLACE FUNCTION calcular_pib_per_capita()
RETURNS TRIGGER AS $$
DECLARE
    pop_municipio BIGINT;
BEGIN
    -- Busca população do município no mesmo ano
    SELECT populacao_total INTO pop_municipio
    FROM fato_populacao
    WHERE id_municipio = NEW.id_municipio
      AND ano = NEW.ano
    LIMIT 1;

    -- Calcula PIB per capita se população disponível
    IF pop_municipio IS NOT NULL AND pop_municipio > 0 THEN
        NEW.pib_per_capita := (NEW.pib_total * 1000) / pop_municipio;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calcular_pib_per_capita
    BEFORE INSERT OR UPDATE ON fato_pib
    FOR EACH ROW
    WHEN (NEW.pib_per_capita IS NULL)
    EXECUTE FUNCTION calcular_pib_per_capita();

-- Trigger para calcular percentuais setoriais
CREATE OR REPLACE FUNCTION calcular_percentuais_setoriais()
RETURNS TRIGGER AS $$
DECLARE
    total_vab DECIMAL(18,2);
BEGIN
    -- Calcula total VAB
    IF NEW.vab_agropecuaria IS NOT NULL AND
       NEW.vab_industria IS NOT NULL AND
       NEW.vab_servicos IS NOT NULL THEN

        total_vab := NEW.vab_agropecuaria + NEW.vab_industria + NEW.vab_servicos;

        IF total_vab > 0 THEN
            NEW.perc_agropecuaria := (NEW.vab_agropecuaria / total_vab) * 100;
            NEW.perc_industria := (NEW.vab_industria / total_vab) * 100;
            NEW.perc_servicos := (NEW.vab_servicos / total_vab) * 100;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calcular_percentuais
    BEFORE INSERT OR UPDATE ON fato_pib
    FOR EACH ROW
    EXECUTE FUNCTION calcular_percentuais_setoriais();
```

**Volume Estimado:** ~80.000 registros (5.570 municípios x ~15 anos disponíveis)

---

### 6. fato_indicador_social

**Descrição:** Fato de indicadores sociais diversos.

**DDL:**
```sql
CREATE TABLE fato_indicador_social (
    -- Chave primária
    id_indicador SERIAL PRIMARY KEY,

    -- Chave estrangeira
    id_municipio INTEGER NOT NULL REFERENCES dim_municipio(id_municipio) ON DELETE CASCADE,

    -- Dimensões
    ano INTEGER NOT NULL,
    tipo_indicador VARCHAR(100) NOT NULL,

    -- Medidas
    valor DECIMAL(18,6) NOT NULL,
    unidade_medida VARCHAR(50),

    -- Metadados
    fonte VARCHAR(100),
    fonte_id INTEGER,
    observacao TEXT,

    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT uk_indicador_municipio_ano_tipo UNIQUE(id_municipio, ano, tipo_indicador),
    CONSTRAINT chk_indicador_ano_valido CHECK (ano BETWEEN 1900 AND 2100)
);

-- Comentários
COMMENT ON TABLE fato_indicador_social IS 'Fato de indicadores sociais diversos';
COMMENT ON COLUMN fato_indicador_social.tipo_indicador IS 'Tipo do indicador (IDH, taxa_alfabetizacao, etc.)';
COMMENT ON COLUMN fato_indicador_social.valor IS 'Valor numérico do indicador';
COMMENT ON COLUMN fato_indicador_social.unidade_medida IS 'Unidade de medida (%, índice, etc.)';

-- Índices
CREATE INDEX idx_indicador_municipio ON fato_indicador_social(id_municipio);
CREATE INDEX idx_indicador_ano ON fato_indicador_social(ano DESC);
CREATE INDEX idx_indicador_tipo ON fato_indicador_social(tipo_indicador);
CREATE INDEX idx_indicador_municipio_ano ON fato_indicador_social(id_municipio, ano DESC);
CREATE INDEX idx_indicador_fonte ON fato_indicador_social(fonte);

-- Índice para busca full-text
CREATE INDEX idx_indicador_tipo_fulltext ON fato_indicador_social
    USING gin(to_tsvector('portuguese', tipo_indicador));

-- Trigger de atualização
CREATE TRIGGER update_fato_indicador_updated_at
    BEFORE UPDATE ON fato_indicador_social
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Tipos de Indicadores Esperados:**
- `IDH` - Índice de Desenvolvimento Humano
- `IDH_EDUCACAO` - IDH Educação
- `IDH_LONGEVIDADE` - IDH Longevidade
- `IDH_RENDA` - IDH Renda
- `TAXA_ALFABETIZACAO` - Taxa de alfabetização
- `TAXA_MORTALIDADE_INFANTIL` - Taxa de mortalidade infantil
- `EXPECTATIVA_VIDA` - Expectativa de vida ao nascer
- `RENDA_PER_CAPITA` - Renda per capita média
- `GINI` - Índice de Gini (desigualdade)

**Volume Estimado:** ~200.000 registros (variável conforme disponibilidade)

---

## Tabela de Metadados

### 7. metadata_extracao

**Descrição:** Registro de execuções do pipeline ETL.

**DDL:**
```sql
CREATE TABLE metadata_extracao (
    -- Chave primária
    id_extracao SERIAL PRIMARY KEY,

    -- Identificação
    tipo_dados VARCHAR(50) NOT NULL,
    pipeline_id VARCHAR(100),

    -- Timestamps
    data_inicio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_fim TIMESTAMP,
    data_extracao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Status
    status VARCHAR(20) NOT NULL CHECK (status IN ('SUCESSO', 'ERRO', 'PARCIAL', 'EM_PROGRESSO')),

    -- Métricas
    registros_extraidos INTEGER,
    registros_transformados INTEGER,
    registros_validos INTEGER,
    registros_invalidos INTEGER,
    registros_carregados INTEGER,
    tempo_execucao_segundos DECIMAL(10,2),

    -- Detalhes
    mensagem_erro TEXT,
    stack_trace TEXT,
    parametros_execucao JSONB,
    estatisticas JSONB,

    -- Ambiente
    hostname VARCHAR(255),
    usuario VARCHAR(100),
    versao_pipeline VARCHAR(20),

    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comentários
COMMENT ON TABLE metadata_extracao IS 'Registro de execuções do pipeline ETL';
COMMENT ON COLUMN metadata_extracao.tipo_dados IS 'Tipo de dados extraídos (MUNICIPIOS, POPULACAO, PIB, etc.)';
COMMENT ON COLUMN metadata_extracao.pipeline_id IS 'ID único da execução do pipeline';
COMMENT ON COLUMN metadata_extracao.parametros_execucao IS 'Parâmetros JSON da execução';
COMMENT ON COLUMN metadata_extracao.estatisticas IS 'Estatísticas JSON da execução';

-- Índices
CREATE INDEX idx_metadata_tipo ON metadata_extracao(tipo_dados);
CREATE INDEX idx_metadata_data ON metadata_extracao(data_extracao DESC);
CREATE INDEX idx_metadata_status ON metadata_extracao(status);
CREATE INDEX idx_metadata_pipeline ON metadata_extracao(pipeline_id);
CREATE INDEX idx_metadata_data_inicio ON metadata_extracao(data_inicio DESC);

-- Índice GIN para busca em JSON
CREATE INDEX idx_metadata_parametros ON metadata_extracao USING gin(parametros_execucao);
CREATE INDEX idx_metadata_estatisticas ON metadata_extracao USING gin(estatisticas);

-- Particionamento por data (opcional)
-- ALTER TABLE metadata_extracao PARTITION BY RANGE (data_extracao);
```

**Volume Estimado:** Crescimento contínuo (1 registro por execução)

---

## Views Materializadas

### 1. mv_populacao_recente

**Descrição:** População mais recente de cada município.

```sql
CREATE MATERIALIZED VIEW mv_populacao_recente AS
SELECT DISTINCT ON (fp.id_municipio)
    fp.id_municipio,
    dm.codigo_ibge,
    dm.nome AS nome_municipio,
    de.sigla AS uf,
    fp.ano,
    fp.populacao_total,
    fp.populacao_urbana,
    fp.populacao_rural,
    fp.densidade_demografica,
    fp.tipo_dado
FROM fato_populacao fp
INNER JOIN dim_municipio dm ON fp.id_municipio = dm.id_municipio
INNER JOIN dim_estado de ON dm.id_estado = de.id_estado
ORDER BY fp.id_municipio, fp.ano DESC;

CREATE UNIQUE INDEX idx_mv_populacao_recente_municipio
    ON mv_populacao_recente(id_municipio);

CREATE INDEX idx_mv_populacao_recente_uf
    ON mv_populacao_recente(uf);

COMMENT ON MATERIALIZED VIEW mv_populacao_recente IS
    'População mais recente disponível de cada município';
```

### 2. mv_pib_recente

**Descrição:** PIB mais recente de cada município.

```sql
CREATE MATERIALIZED VIEW mv_pib_recente AS
SELECT DISTINCT ON (fp.id_municipio)
    fp.id_municipio,
    dm.codigo_ibge,
    dm.nome AS nome_municipio,
    de.sigla AS uf,
    fp.ano,
    fp.pib_total,
    fp.pib_per_capita,
    fp.vab_agropecuaria,
    fp.vab_industria,
    fp.vab_servicos,
    fp.perc_agropecuaria,
    fp.perc_industria,
    fp.perc_servicos
FROM fato_pib fp
INNER JOIN dim_municipio dm ON fp.id_municipio = dm.id_municipio
INNER JOIN dim_estado de ON dm.id_estado = de.id_estado
ORDER BY fp.id_municipio, fp.ano DESC;

CREATE UNIQUE INDEX idx_mv_pib_recente_municipio
    ON mv_pib_recente(id_municipio);

CREATE INDEX idx_mv_pib_recente_uf
    ON mv_pib_recente(uf);

COMMENT ON MATERIALIZED VIEW mv_pib_recente IS
    'PIB mais recente disponível de cada município';
```

### 3. mv_ranking_municipios

**Descrição:** Ranking de municípios por população e PIB.

```sql
CREATE MATERIALIZED VIEW mv_ranking_municipios AS
SELECT
    dm.id_municipio,
    dm.codigo_ibge,
    dm.nome,
    de.sigla AS uf,
    dr.nome AS regiao,

    -- População
    pop.ano AS ano_populacao,
    pop.populacao_total,
    RANK() OVER (ORDER BY pop.populacao_total DESC) AS rank_populacao_brasil,
    RANK() OVER (PARTITION BY de.id_estado ORDER BY pop.populacao_total DESC) AS rank_populacao_estado,

    -- PIB
    pib.ano AS ano_pib,
    pib.pib_total,
    pib.pib_per_capita,
    RANK() OVER (ORDER BY pib.pib_total DESC) AS rank_pib_brasil,
    RANK() OVER (PARTITION BY de.id_estado ORDER BY pib.pib_total DESC) AS rank_pib_estado,
    RANK() OVER (ORDER BY pib.pib_per_capita DESC) AS rank_pib_per_capita_brasil

FROM dim_municipio dm
INNER JOIN dim_estado de ON dm.id_estado = de.id_estado
INNER JOIN dim_regiao dr ON de.id_regiao = dr.id_regiao
LEFT JOIN mv_populacao_recente pop ON dm.id_municipio = pop.id_municipio
LEFT JOIN mv_pib_recente pib ON dm.id_municipio = pib.id_municipio;

CREATE UNIQUE INDEX idx_mv_ranking_municipio
    ON mv_ranking_municipios(id_municipio);

COMMENT ON MATERIALIZED VIEW mv_ranking_municipios IS
    'Rankings de municípios por população e PIB';
```

**Refresh das Materialized Views:**
```sql
-- Refresh manual
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_populacao_recente;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_pib_recente;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ranking_municipios;

-- Ou criar job automático (usando pg_cron ou similar)
```

---

## Queries de Exemplo

### 1. Top 10 Municípios por População

```sql
SELECT
    dm.nome,
    de.sigla AS uf,
    fp.ano,
    fp.populacao_total,
    RANK() OVER (ORDER BY fp.populacao_total DESC) AS ranking
FROM fato_populacao fp
INNER JOIN dim_municipio dm ON fp.id_municipio = dm.id_municipio
INNER JOIN dim_estado de ON dm.id_estado = de.id_estado
WHERE fp.ano = (SELECT MAX(ano) FROM fato_populacao)
ORDER BY fp.populacao_total DESC
LIMIT 10;
```

### 2. Evolução Populacional de um Município

```sql
SELECT
    fp.ano,
    fp.populacao_total,
    fp.populacao_urbana,
    fp.populacao_rural,
    LAG(fp.populacao_total) OVER (ORDER BY fp.ano) AS pop_ano_anterior,
    ROUND(
        ((fp.populacao_total - LAG(fp.populacao_total) OVER (ORDER BY fp.ano))
        / NULLIF(LAG(fp.populacao_total) OVER (ORDER BY fp.ano), 0) * 100),
        2
    ) AS crescimento_percentual
FROM fato_populacao fp
INNER JOIN dim_municipio dm ON fp.id_municipio = dm.id_municipio
WHERE dm.codigo_ibge = 3550308 -- São Paulo
ORDER BY fp.ano;
```

### 3. PIB Total por Estado

```sql
SELECT
    de.sigla AS uf,
    de.nome AS estado,
    SUM(pib.pib_total) AS pib_total_estado,
    AVG(pib.pib_per_capita) AS pib_per_capita_medio,
    COUNT(*) AS num_municipios
FROM fato_pib pib
INNER JOIN dim_municipio dm ON pib.id_municipio = dm.id_municipio
INNER JOIN dim_estado de ON dm.id_estado = de.id_estado
WHERE pib.ano = 2021
GROUP BY de.id_estado, de.sigla, de.nome
ORDER BY pib_total_estado DESC;
```

### 4. Municípios com Maior Participação da Agropecuária

```sql
SELECT
    dm.nome,
    de.sigla AS uf,
    pib.perc_agropecuaria,
    pib.vab_agropecuaria,
    pib.pib_total
FROM fato_pib pib
INNER JOIN dim_municipio dm ON pib.id_municipio = dm.id_municipio
INNER JOIN dim_estado de ON dm.id_estado = de.id_estado
WHERE pib.ano = 2021
  AND pib.perc_agropecuaria IS NOT NULL
ORDER BY pib.perc_agropecuaria DESC
LIMIT 20;
```

### 5. Densidade Demográfica por Região

```sql
SELECT
    dr.nome AS regiao,
    ROUND(AVG(fp.densidade_demografica), 2) AS densidade_media,
    ROUND(MIN(fp.densidade_demografica), 2) AS densidade_minima,
    ROUND(MAX(fp.densidade_demografica), 2) AS densidade_maxima
FROM fato_populacao fp
INNER JOIN dim_municipio dm ON fp.id_municipio = dm.id_municipio
INNER JOIN dim_estado de ON dm.id_estado = de.id_estado
INNER JOIN dim_regiao dr ON de.id_regiao = dr.id_regiao
WHERE fp.ano = 2022
  AND fp.densidade_demografica IS NOT NULL
GROUP BY dr.id_regiao, dr.nome
ORDER BY densidade_media DESC;
```

---

## Manutenção e Performance

### Vacuum e Analyze

```sql
-- Vacuum completo
VACUUM FULL ANALYZE;

-- Vacuum por tabela
VACUUM ANALYZE fato_populacao;
VACUUM ANALYZE fato_pib;
VACUUM ANALYZE fato_indicador_social;

-- Reindex
REINDEX TABLE fato_populacao;
REINDEX TABLE fato_pib;
```

### Estatísticas

```sql
-- Atualizar estatísticas
ANALYZE;

-- Ver estatísticas de uma tabela
SELECT * FROM pg_stats WHERE tablename = 'fato_populacao';
```

### Tamanho das Tabelas

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Backup e Restore

### Backup

```bash
# Backup completo
pg_dump -h localhost -U ibge_user -d ibge_socioeconomico > backup.sql

# Backup schema only
pg_dump -h localhost -U ibge_user -d ibge_socioeconomico --schema-only > schema.sql

# Backup data only
pg_dump -h localhost -U ibge_user -d ibge_socioeconomico --data-only > data.sql

# Backup de uma tabela específica
pg_dump -h localhost -U ibge_user -d ibge_socioeconomico -t fato_populacao > populacao.sql
```

### Restore

```bash
# Restore completo
psql -h localhost -U ibge_user -d ibge_socioeconomico < backup.sql

# Restore schema
psql -h localhost -U ibge_user -d ibge_socioeconomico < schema.sql

# Restore data
psql -h localhost -U ibge_user -d ibge_socioeconomico < data.sql
```

---

## Conclusão

Este schema fornece uma base sólida e escalável para armazenar e consultar dados socioeconômicos do IBGE. As otimizações de índices, triggers e materialized views garantem performance adequada mesmo com grandes volumes de dados.

**Próximos Passos:**
1. Implementar modelos SQLAlchemy correspondentes
2. Criar migrations com Alembic
3. Implementar testes de integridade
4. Configurar monitoramento de performance
