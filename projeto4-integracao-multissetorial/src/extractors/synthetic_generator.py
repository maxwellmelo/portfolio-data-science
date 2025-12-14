"""
Gerador de Dados Sintéticos para Simulação.

Gera dados realistas baseados em estruturas governamentais reais
para demonstração do sistema de integração multissetorial.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
import pandas as pd
import numpy as np
from faker import Faker
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import MUNICIPIOS_PIAUI

# Configurar Faker para português brasileiro
fake = Faker('pt_BR')
Faker.seed(42)
np.random.seed(42)


class SyntheticDataGenerator:
    """
    Gerador de dados sintéticos multissetoriais.

    Gera dados simulados para:
    - Saúde (DATASUS): Mortalidade, nascimentos, internações
    - Educação (INEP): Censo escolar, IDEB, matrículas
    - Economia (IBGE): PIB, empresas, emprego
    - Assistência Social (MDS): Cadastro Único, benefícios
    """

    def __init__(self, seed: int = 42):
        """
        Inicializa o gerador.

        Args:
            seed: Semente para reprodutibilidade
        """
        self.seed = seed
        Faker.seed(seed)
        np.random.seed(seed)
        random.seed(seed)

        self.municipios = MUNICIPIOS_PIAUI
        self.anos = list(range(2018, 2024))

        logger.info(f"SyntheticDataGenerator inicializado | seed={seed}")

    def generate_saude_mortalidade(self, n_records: int = 5000) -> pd.DataFrame:
        """
        Gera dados sintéticos de mortalidade (similar ao SIM/DATASUS).

        Args:
            n_records: Número de registros

        Returns:
            DataFrame com dados de óbitos
        """
        logger.info(f"Gerando dados de mortalidade: {n_records} registros")

        cids_principais = [
            ("I21", "Infarto agudo do miocárdio"),
            ("J18", "Pneumonia"),
            ("C34", "Neoplasia maligna dos brônquios e pulmões"),
            ("E14", "Diabetes mellitus não especificado"),
            ("I64", "Acidente vascular cerebral"),
            ("J44", "Doença pulmonar obstrutiva crônica"),
            ("C50", "Neoplasia maligna da mama"),
            ("I10", "Hipertensão essencial"),
            ("B34", "Infecção viral"),
            ("V89", "Acidente de trânsito")
        ]

        records = []
        for _ in range(n_records):
            municipio_id = random.choice(list(self.municipios.keys()))
            ano = random.choice(self.anos)
            mes = random.randint(1, 12)
            cid_code, cid_desc = random.choice(cids_principais)

            idade = max(0, int(np.random.normal(65, 20)))
            sexo = random.choice(["M", "F"])

            records.append({
                "id_obito": fake.uuid4()[:8],
                "data_obito": datetime(ano, mes, random.randint(1, 28)),
                "municipio_id": municipio_id,
                "municipio_nome": self.municipios[municipio_id],
                "uf": "PI",
                "idade": min(idade, 110),
                "sexo": sexo,
                "raca_cor": random.choice(["Branca", "Preta", "Parda", "Amarela", "Indígena"]),
                "escolaridade": random.choice(["Sem escolaridade", "Fundamental", "Médio", "Superior"]),
                "cid_principal": cid_code,
                "causa_basica": cid_desc,
                "local_obito": random.choice(["Hospital", "Domicílio", "Via pública", "Outros"]),
                "ano": ano
            })

        df = pd.DataFrame(records)
        logger.info(f"Dados de mortalidade gerados: {len(df)} registros")
        return df

    def generate_saude_nascimentos(self, n_records: int = 3000) -> pd.DataFrame:
        """
        Gera dados sintéticos de nascidos vivos (similar ao SINASC).

        Args:
            n_records: Número de registros

        Returns:
            DataFrame com dados de nascimentos
        """
        logger.info(f"Gerando dados de nascimentos: {n_records} registros")

        records = []
        for _ in range(n_records):
            municipio_id = random.choice(list(self.municipios.keys()))
            ano = random.choice(self.anos)
            mes = random.randint(1, 12)

            idade_mae = max(14, min(50, int(np.random.normal(26, 6))))
            peso = max(500, min(5500, int(np.random.normal(3200, 500))))
            semanas = max(22, min(42, int(np.random.normal(38, 2))))

            records.append({
                "id_nascimento": fake.uuid4()[:8],
                "data_nascimento": datetime(ano, mes, random.randint(1, 28)),
                "municipio_id": municipio_id,
                "municipio_nome": self.municipios[municipio_id],
                "uf": "PI",
                "sexo": random.choice(["M", "F"]),
                "peso_nascer": peso,
                "semanas_gestacao": semanas,
                "tipo_parto": random.choice(["Vaginal", "Cesáreo"]),
                "idade_mae": idade_mae,
                "escolaridade_mae": random.choice(["Fundamental", "Médio", "Superior"]),
                "estado_civil_mae": random.choice(["Solteira", "Casada", "União estável", "Divorciada"]),
                "consultas_prenatal": random.randint(0, 12),
                "apgar_1min": random.randint(5, 10),
                "apgar_5min": random.randint(7, 10),
                "anomalia_congenita": random.choice(["Não", "Não", "Não", "Não", "Sim"]),
                "ano": ano
            })

        df = pd.DataFrame(records)
        logger.info(f"Dados de nascimentos gerados: {len(df)} registros")
        return df

    def generate_educacao_escolas(self, n_records: int = 500) -> pd.DataFrame:
        """
        Gera dados sintéticos de escolas (similar ao Censo Escolar).

        Args:
            n_records: Número de registros

        Returns:
            DataFrame com dados de escolas
        """
        logger.info(f"Gerando dados de escolas: {n_records} registros")

        records = []
        for i in range(n_records):
            municipio_id = random.choice(list(self.municipios.keys()))
            ano = random.choice(self.anos)

            dependencia = random.choices(
                ["Estadual", "Municipal", "Privada", "Federal"],
                weights=[30, 50, 18, 2]
            )[0]

            total_alunos = int(np.random.lognormal(5, 1))
            total_alunos = max(20, min(2000, total_alunos))

            records.append({
                "id_escola": f"22{random.randint(100000, 999999)}",
                "nome_escola": f"Escola {fake.company_suffix()} {fake.last_name()}",
                "municipio_id": municipio_id,
                "municipio_nome": self.municipios[municipio_id],
                "uf": "PI",
                "dependencia_administrativa": dependencia,
                "localizacao": random.choice(["Urbana", "Rural"]),
                "total_alunos": total_alunos,
                "total_docentes": max(5, total_alunos // 20),
                "total_funcionarios": max(3, total_alunos // 30),
                "educacao_infantil": random.choice([True, False]),
                "ensino_fundamental": random.choice([True, True, True, False]),
                "ensino_medio": random.choice([True, False, False]),
                "eja": random.choice([True, False, False, False]),
                "agua_potavel": random.choice([True, True, True, False]),
                "energia_eletrica": random.choice([True, True, True, True, False]),
                "internet": random.choice([True, True, False]),
                "biblioteca": random.choice([True, False]),
                "quadra_esportes": random.choice([True, False]),
                "ano": ano
            })

        df = pd.DataFrame(records)
        logger.info(f"Dados de escolas gerados: {len(df)} registros")
        return df

    def generate_educacao_ideb(self, n_records: int = 200) -> pd.DataFrame:
        """
        Gera dados sintéticos de IDEB.

        Args:
            n_records: Número de registros

        Returns:
            DataFrame com dados de IDEB
        """
        logger.info(f"Gerando dados de IDEB: {n_records} registros")

        records = []
        anos_ideb = [2017, 2019, 2021, 2023]

        for municipio_id, municipio_nome in self.municipios.items():
            for ano in anos_ideb:
                for etapa in ["Anos Iniciais", "Anos Finais", "Ensino Médio"]:
                    for rede in ["Estadual", "Municipal"]:
                        if etapa == "Ensino Médio" and rede == "Municipal":
                            continue

                        ideb_base = 4.5 if etapa == "Anos Iniciais" else 4.0
                        ideb = round(ideb_base + np.random.normal(0, 0.8) + (ano - 2017) * 0.1, 1)
                        ideb = max(2.0, min(8.0, ideb))

                        records.append({
                            "municipio_id": municipio_id,
                            "municipio_nome": municipio_nome,
                            "uf": "PI",
                            "ano": ano,
                            "etapa_ensino": etapa,
                            "rede": rede,
                            "ideb": ideb,
                            "meta_projetada": round(ideb - np.random.uniform(-0.3, 0.5), 1),
                            "taxa_aprovacao": round(np.random.uniform(0.75, 0.98), 2),
                            "nota_matematica": round(np.random.uniform(180, 280), 1),
                            "nota_portugues": round(np.random.uniform(180, 280), 1)
                        })

        df = pd.DataFrame(records)
        logger.info(f"Dados de IDEB gerados: {len(df)} registros")
        return df

    def generate_economia_pib(self) -> pd.DataFrame:
        """
        Gera dados sintéticos de PIB municipal.

        Returns:
            DataFrame com dados de PIB
        """
        logger.info("Gerando dados de PIB municipal")

        records = []
        for municipio_id, municipio_nome in self.municipios.items():
            for ano in self.anos:
                # PIB base proporcional à capital
                if municipio_id == 2211001:  # Teresina
                    pib_base = 25000000  # 25 bilhões
                else:
                    pib_base = np.random.uniform(500000, 5000000)

                # Crescimento anual
                crescimento = 1 + (ano - 2018) * np.random.uniform(0.02, 0.05)
                pib_total = pib_base * crescimento * np.random.uniform(0.9, 1.1)

                # Composição setorial
                agro = np.random.uniform(0.05, 0.25)
                industria = np.random.uniform(0.10, 0.25)
                servicos = np.random.uniform(0.40, 0.60)
                adm_publica = 1 - agro - industria - servicos

                # População estimada
                pop_base = 864000 if municipio_id == 2211001 else np.random.uniform(10000, 150000)
                populacao = int(pop_base * (1 + (ano - 2018) * 0.01))

                records.append({
                    "municipio_id": municipio_id,
                    "municipio_nome": municipio_nome,
                    "uf": "PI",
                    "ano": ano,
                    "pib_total_mil_reais": round(pib_total, 2),
                    "pib_agropecuaria_mil_reais": round(pib_total * agro, 2),
                    "pib_industria_mil_reais": round(pib_total * industria, 2),
                    "pib_servicos_mil_reais": round(pib_total * servicos, 2),
                    "pib_adm_publica_mil_reais": round(pib_total * adm_publica, 2),
                    "populacao_estimada": populacao,
                    "pib_per_capita": round((pib_total * 1000) / populacao, 2)
                })

        df = pd.DataFrame(records)
        logger.info(f"Dados de PIB gerados: {len(df)} registros")
        return df

    def generate_assistencia_cadunico(self, n_records: int = 10000) -> pd.DataFrame:
        """
        Gera dados sintéticos do Cadastro Único (estrutura similar).

        Args:
            n_records: Número de registros

        Returns:
            DataFrame com dados do CadÚnico
        """
        logger.info(f"Gerando dados do CadÚnico: {n_records} registros")

        records = []
        for _ in range(n_records):
            municipio_id = random.choice(list(self.municipios.keys()))
            ano = random.choice(self.anos)
            mes = random.randint(1, 12)

            renda_per_capita = max(0, np.random.exponential(200))
            qtd_membros = random.choices([1, 2, 3, 4, 5, 6], weights=[10, 15, 25, 30, 15, 5])[0]

            records.append({
                "id_familia": fake.uuid4()[:12],
                "data_cadastro": datetime(ano, mes, random.randint(1, 28)),
                "data_atualizacao": datetime(ano, mes, random.randint(1, 28)) + timedelta(days=random.randint(0, 365)),
                "municipio_id": municipio_id,
                "municipio_nome": self.municipios[municipio_id],
                "uf": "PI",
                "qtd_membros_familia": qtd_membros,
                "renda_per_capita": round(renda_per_capita, 2),
                "faixa_renda": self._classificar_renda(renda_per_capita),
                "situacao_domicilio": random.choice(["Próprio", "Alugado", "Cedido"]),
                "tipo_domicilio": random.choice(["Casa", "Apartamento", "Cômodo"]),
                "agua_canalizada": random.choice([True, True, True, False]),
                "energia_eletrica": random.choice([True, True, True, True, False]),
                "esgoto_sanitario": random.choice([True, True, False, False]),
                "coleta_lixo": random.choice([True, True, True, False]),
                "recebe_bolsa_familia": random.choice([True, True, False]),
                "recebe_bpc": random.choice([True, False, False, False, False]),
                "ano": ano
            })

        df = pd.DataFrame(records)
        logger.info(f"Dados do CadÚnico gerados: {len(df)} registros")
        return df

    def _classificar_renda(self, renda: float) -> str:
        """Classifica faixa de renda."""
        if renda <= 89:
            return "Extrema pobreza"
        elif renda <= 178:
            return "Pobreza"
        elif renda <= 600:
            return "Baixa renda"
        else:
            return "Acima de meio SM"

    def generate_all(self) -> Dict[str, pd.DataFrame]:
        """
        Gera todos os conjuntos de dados sintéticos.

        Returns:
            Dicionário com todos os DataFrames
        """
        logger.info("Gerando todos os dados sintéticos...")

        datasets = {
            "saude_mortalidade": self.generate_saude_mortalidade(),
            "saude_nascimentos": self.generate_saude_nascimentos(),
            "educacao_escolas": self.generate_educacao_escolas(),
            "educacao_ideb": self.generate_educacao_ideb(),
            "economia_pib": self.generate_economia_pib(),
            "assistencia_cadunico": self.generate_assistencia_cadunico()
        }

        total = sum(len(df) for df in datasets.values())
        logger.info(f"Total de registros gerados: {total}")

        return datasets


# Exemplo de uso
if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    datasets = generator.generate_all()

    for name, df in datasets.items():
        print(f"\n{name}: {len(df)} registros")
        print(df.head(3))
