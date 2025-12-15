"""
Anonimizador de Dados Pessoais.

Implementa técnicas de anonimização conforme LGPD:
- Mascaramento
- Pseudonimização (hash)
- Generalização
- Supressão
- Tokenização
"""

import re
import hashlib
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import pandas as pd
import numpy as np
from faker import Faker
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings


class AnonymizationMethod(str, Enum):
    """Métodos de anonimização disponíveis."""
    MASK = "mask"
    HASH = "hash"
    PSEUDONYMIZE = "pseudonymize"
    GENERALIZE = "generalize"
    SUPPRESS = "suppress"
    TOKENIZE = "tokenize"
    NOISE = "noise"


class DataAnonymizer:
    """
    Anonimizador de dados pessoais.

    Técnicas implementadas:
    - Mascaramento: Substitui caracteres por asteriscos
    - Hash: Gera hash irreversível do valor
    - Pseudonimização: Substitui por identificador artificial
    - Generalização: Reduz granularidade (ex: idade exata → faixa)
    - Supressão: Remove completamente o valor
    - Tokenização: Substitui por token único mapeável
    - Ruído: Adiciona variação aleatória (para numéricos)
    """

    def __init__(self, salt: str = None, strict_mode: bool = False):
        """
        Inicializa o anonimizador.

        Args:
            salt: Salt para funções hash (IMPORTANTE: use valor seguro em produção)
            strict_mode: Se True, raise error quando salt inseguro for detectado
        """
        self.salt = salt or settings.anonymization.hash_salt
        self.fake = Faker('pt_BR')
        self._token_map: Dict[str, str] = {}
        self._token_counter = 0
        self._strict_mode = strict_mode

        # Validar segurança do salt
        self._validate_salt()

        logger.info("DataAnonymizer inicializado")

    def _validate_salt(self) -> None:
        """Valida segurança do salt e emite avisos/erros apropriados."""
        warning = settings.anonymization.get_salt_warning()

        if warning:
            if self._strict_mode:
                raise ValueError(
                    f"Configuracao de salt insegura em modo strict: {warning}. "
                    "Defina HASH_SALT no .env ou desative strict_mode."
                )
            else:
                logger.warning(f"SEGURANCA: {warning}")

        if not settings.anonymization.is_salt_secure():
            logger.warning(
                "Salt atual NAO e seguro para producao. "
                "Recomendacao: gere um salt aleatorio de pelo menos 32 caracteres."
            )

    def anonymize_column(
        self,
        df: pd.DataFrame,
        column: str,
        method: AnonymizationMethod,
        **kwargs
    ) -> pd.DataFrame:
        """
        Anonimiza uma coluna específica.

        Args:
            df: DataFrame original
            column: Nome da coluna
            method: Método de anonimização
            **kwargs: Parâmetros específicos do método

        Returns:
            DataFrame com coluna anonimizada
        """
        df = df.copy()

        if column not in df.columns:
            raise ValueError(f"Coluna '{column}' não encontrada")

        method_map = {
            AnonymizationMethod.MASK: self._mask_column,
            AnonymizationMethod.HASH: self._hash_column,
            AnonymizationMethod.PSEUDONYMIZE: self._pseudonymize_column,
            AnonymizationMethod.GENERALIZE: self._generalize_column,
            AnonymizationMethod.SUPPRESS: self._suppress_column,
            AnonymizationMethod.TOKENIZE: self._tokenize_column,
            AnonymizationMethod.NOISE: self._add_noise_column
        }

        anonymizer = method_map.get(method)
        if not anonymizer:
            raise ValueError(f"Método '{method}' não suportado")

        df[column] = anonymizer(df[column], **kwargs)

        logger.info(f"Coluna '{column}' anonimizada com método '{method.value}'")

        return df

    def anonymize_dataframe(
        self,
        df: pd.DataFrame,
        config: Dict[str, Dict]
    ) -> pd.DataFrame:
        """
        Anonimiza múltiplas colunas com diferentes métodos.

        Args:
            df: DataFrame original
            config: Dicionário {coluna: {method: ..., **params}}

        Returns:
            DataFrame anonimizado
        """
        df = df.copy()

        for column, params in config.items():
            if column not in df.columns:
                logger.warning(f"Coluna '{column}' não encontrada, pulando...")
                continue

            method = AnonymizationMethod(params.get("method", "mask"))
            kwargs = {k: v for k, v in params.items() if k != "method"}

            df = self.anonymize_column(df, column, method, **kwargs)

        return df

    # ========== Métodos de Anonimização ==========

    def _mask_column(
        self,
        series: pd.Series,
        mask_char: str = "*",
        visible_start: int = 0,
        visible_end: int = 0,
        pattern: str = None
    ) -> pd.Series:
        """
        Mascara valores mantendo parte visível.

        Args:
            series: Série a mascarar
            mask_char: Caractere de máscara
            visible_start: Caracteres visíveis no início
            visible_end: Caracteres visíveis no fim
            pattern: Padrão específico (ex: "***.***.***-**" para CPF)
        """
        def mask_value(val):
            if pd.isna(val):
                return val

            val_str = str(val)

            if pattern:
                # Usar padrão específico
                return pattern

            if visible_start == 0 and visible_end == 0:
                return mask_char * len(val_str)

            start = val_str[:visible_start] if visible_start > 0 else ""
            end = val_str[-visible_end:] if visible_end > 0 else ""
            middle_len = max(0, len(val_str) - visible_start - visible_end)

            return start + (mask_char * middle_len) + end

        return series.apply(mask_value)

    def _hash_column(
        self,
        series: pd.Series,
        algorithm: str = "sha256",
        truncate: int = None
    ) -> pd.Series:
        """
        Aplica hash aos valores.

        Args:
            series: Série a hashear
            algorithm: Algoritmo de hash
            truncate: Truncar resultado para N caracteres
        """
        def hash_value(val):
            if pd.isna(val):
                return val

            # Adicionar salt
            salted = f"{self.salt}{val}"

            # Calcular hash
            if algorithm == "sha256":
                hashed = hashlib.sha256(salted.encode()).hexdigest()
            elif algorithm == "sha512":
                hashed = hashlib.sha512(salted.encode()).hexdigest()
            elif algorithm == "md5":
                hashed = hashlib.md5(salted.encode()).hexdigest()
            else:
                hashed = hashlib.sha256(salted.encode()).hexdigest()

            if truncate:
                hashed = hashed[:truncate]

            return hashed

        return series.apply(hash_value)

    def _pseudonymize_column(
        self,
        series: pd.Series,
        pii_type: str = "name"
    ) -> pd.Series:
        """
        Substitui por valores falsos mas realistas.

        Args:
            series: Série a pseudonimizar
            pii_type: Tipo de dado (name, email, phone, address, cpf)
        """
        fake_generators = {
            "name": lambda: self.fake.name(),
            "email": lambda: self.fake.email(),
            "phone": lambda: self.fake.phone_number(),
            "address": lambda: self.fake.address(),
            "cpf": lambda: self.fake.cpf(),
            "cnpj": lambda: self.fake.cnpj(),
            "date": lambda: self.fake.date(),
            "city": lambda: self.fake.city(),
            "text": lambda: self.fake.text(max_nb_chars=50)
        }

        generator = fake_generators.get(pii_type, lambda: self.fake.uuid4()[:8])

        # Manter consistência: mesmo valor original → mesmo valor falso
        unique_values = series.dropna().unique()
        mapping = {val: generator() for val in unique_values}

        return series.map(mapping)

    def _generalize_column(
        self,
        series: pd.Series,
        generalization_type: str = "range",
        bins: int = 5,
        labels: List[str] = None
    ) -> pd.Series:
        """
        Generaliza valores para categorias mais amplas.

        Args:
            series: Série a generalizar
            generalization_type: Tipo (range, category, truncate)
            bins: Número de faixas para numéricos
            labels: Rótulos das faixas
        """
        if generalization_type == "range" and pd.api.types.is_numeric_dtype(series):
            # Criar faixas para dados numéricos
            return pd.cut(series, bins=bins, labels=labels)

        elif generalization_type == "year" and pd.api.types.is_datetime64_any_dtype(series):
            # Manter apenas ano
            return series.dt.year

        elif generalization_type == "truncate":
            # Truncar strings (ex: CEP 5 dígitos → 3)
            return series.astype(str).str[:3] + "***"

        else:
            # Padrão: agrupar por frequência
            top_values = series.value_counts().head(bins - 1).index.tolist()
            return series.apply(lambda x: x if x in top_values else "Outros")

    def _suppress_column(
        self,
        series: pd.Series,
        replacement: Any = None
    ) -> pd.Series:
        """
        Suprime (remove) todos os valores.

        Args:
            series: Série a suprimir
            replacement: Valor de substituição (None = NaN)
        """
        return pd.Series([replacement] * len(series), index=series.index)

    def _tokenize_column(
        self,
        series: pd.Series,
        prefix: str = "TOK_"
    ) -> pd.Series:
        """
        Substitui por tokens únicos (mapeamento reversível).

        Args:
            series: Série a tokenizar
            prefix: Prefixo dos tokens
        """
        def get_token(val):
            if pd.isna(val):
                return val

            val_str = str(val)

            if val_str not in self._token_map:
                self._token_counter += 1
                self._token_map[val_str] = f"{prefix}{self._token_counter:08d}"

            return self._token_map[val_str]

        return series.apply(get_token)

    def _add_noise_column(
        self,
        series: pd.Series,
        noise_level: float = 0.1,
        method: str = "gaussian"
    ) -> pd.Series:
        """
        Adiciona ruído a valores numéricos.

        Args:
            series: Série numérica
            noise_level: Nível de ruído (proporção do desvio padrão)
            method: gaussian, uniform, laplace
        """
        if not pd.api.types.is_numeric_dtype(series):
            logger.warning("Ruído só pode ser aplicado a colunas numéricas")
            return series

        std = series.std()

        if method == "gaussian":
            noise = np.random.normal(0, std * noise_level, len(series))
        elif method == "uniform":
            noise = np.random.uniform(-std * noise_level, std * noise_level, len(series))
        elif method == "laplace":
            noise = np.random.laplace(0, std * noise_level, len(series))
        else:
            noise = np.random.normal(0, std * noise_level, len(series))

        return series + noise

    # ========== Métodos Específicos ==========

    def mask_cpf(self, cpf: str) -> str:
        """Mascara CPF mantendo primeiros e últimos dígitos."""
        cpf_clean = re.sub(r'\D', '', str(cpf))
        if len(cpf_clean) != 11:
            return "***.***.***-**"
        return f"{cpf_clean[:3]}.***.***-{cpf_clean[-2:]}"

    def mask_email(self, email: str) -> str:
        """Mascara e-mail mantendo domínio."""
        if "@" not in str(email):
            return "***@***.***"
        parts = str(email).split("@")
        user = parts[0]
        domain = parts[1]
        masked_user = user[0] + "*" * (len(user) - 1) if len(user) > 1 else "*"
        return f"{masked_user}@{domain}"

    def mask_telefone(self, telefone: str) -> str:
        """Mascara telefone mantendo DDD."""
        tel_clean = re.sub(r'\D', '', str(telefone))
        if len(tel_clean) < 10:
            return "(**) *****-****"
        ddd = tel_clean[:2]
        return f"({ddd}) *****-****"

    def get_token_mapping(self) -> Dict[str, str]:
        """Retorna mapeamento de tokens (para reversão se necessário)."""
        return self._token_map.copy()

    def clear_token_mapping(self) -> None:
        """Limpa mapeamento de tokens."""
        self._token_map.clear()
        self._token_counter = 0


# Exemplo de uso
if __name__ == "__main__":
    from faker import Faker
    fake = Faker('pt_BR')

    # Criar dados de teste
    df_test = pd.DataFrame({
        "nome": [fake.name() for _ in range(10)],
        "cpf": [fake.cpf() for _ in range(10)],
        "email": [fake.email() for _ in range(10)],
        "salario": [round(np.random.uniform(2000, 15000), 2) for _ in range(10)],
        "idade": [np.random.randint(18, 70) for _ in range(10)]
    })

    print("=== DADOS ORIGINAIS ===")
    print(df_test)

    # Configuração de anonimização
    config = {
        "nome": {"method": "pseudonymize", "pii_type": "name"},
        "cpf": {"method": "hash", "truncate": 12},
        "email": {"method": "mask", "visible_start": 1, "visible_end": 0, "pattern": "***@***.***"},
        "salario": {"method": "noise", "noise_level": 0.1},
        "idade": {"method": "generalize", "bins": 4, "labels": ["18-30", "31-45", "46-60", "60+"]}
    }

    anonymizer = DataAnonymizer()
    df_anon = anonymizer.anonymize_dataframe(df_test, config)

    print("\n=== DADOS ANONIMIZADOS ===")
    print(df_anon)
