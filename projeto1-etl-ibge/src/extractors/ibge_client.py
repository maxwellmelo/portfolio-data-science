"""
Cliente HTTP para as APIs do IBGE.
Implementa retry automático, rate limiting e tratamento de erros.
"""

import time
from typing import Any, Dict, List, Optional, Union
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from pydantic import BaseModel
from src.utils.logger import get_logger

logger = get_logger(__name__)


class IBGEApiError(Exception):
    """Erro personalizado para falhas na API do IBGE."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RateLimiter:
    """Controlador de taxa de requisições."""

    def __init__(self, min_interval: float = 0.5):
        """
        Args:
            min_interval: Intervalo mínimo entre requisições em segundos
        """
        self.min_interval = min_interval
        self.last_request_time = 0.0

    def wait(self) -> None:
        """Aguarda o tempo necessário antes da próxima requisição."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            logger.debug(f"Rate limiter: aguardando {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()


class IBGEClient:
    """
    Cliente para interação com as APIs do IBGE.

    APIs suportadas:
    - Localidades (v1): Estados, municípios, regiões
    - Agregados/SIDRA (v3): Dados estatísticos (população, PIB, etc.)
    """

    BASE_URL = "https://servicodados.ibge.gov.br/api"

    def __init__(
        self,
        timeout: int = 30,
        retry_attempts: int = 3,
        rate_limit_delay: float = 0.5
    ):
        """
        Inicializa o cliente IBGE.

        Args:
            timeout: Timeout para requisições em segundos
            retry_attempts: Número de tentativas em caso de falha
            rate_limit_delay: Delay entre requisições para evitar rate limiting
        """
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.rate_limiter = RateLimiter(rate_limit_delay)

        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "Accept": "application/json",
                "User-Agent": "ETL-Pipeline-IBGE/1.0"
            }
        )

        logger.info(
            f"IBGEClient inicializado | timeout={timeout}s | "
            f"retry={retry_attempts} | rate_limit={rate_limit_delay}s"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        """Fecha a conexão HTTP."""
        self._client.close()
        logger.info("IBGEClient fechado")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict, List]:
        """
        Executa uma requisição HTTP GET com retry automático.

        Args:
            endpoint: Endpoint da API (ex: '/v1/localidades/estados')
            params: Parâmetros da query string

        Returns:
            Resposta da API em formato JSON

        Raises:
            IBGEApiError: Em caso de erro na API
        """
        self.rate_limiter.wait()

        url = f"{self.BASE_URL}{endpoint}"
        logger.debug(f"Requisição: GET {url} | params={params}")

        try:
            response = self._client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Resposta: {len(str(data))} bytes")

            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e.response.text}")
            raise IBGEApiError(
                f"Erro na API do IBGE: {e.response.status_code}",
                status_code=e.response.status_code
            )

        except httpx.RequestError as e:
            logger.error(f"Erro de conexão: {str(e)}")
            raise IBGEApiError(f"Erro de conexão com a API do IBGE: {str(e)}")

    # ========== API de Localidades (v1) ==========

    def get_regioes(self) -> List[Dict]:
        """
        Obtém todas as regiões do Brasil.

        Returns:
            Lista de regiões com id, sigla e nome
        """
        logger.info("Extraindo regiões do Brasil")
        return self._make_request("/v1/localidades/regioes")

    def get_estados(self) -> List[Dict]:
        """
        Obtém todos os estados do Brasil.

        Returns:
            Lista de estados com id, sigla, nome e região
        """
        logger.info("Extraindo estados do Brasil")
        return self._make_request("/v1/localidades/estados")

    def get_municipios(self, uf: Optional[str] = None) -> List[Dict]:
        """
        Obtém municípios do Brasil ou de um estado específico.

        Args:
            uf: Sigla do estado (ex: 'SP', 'PI') ou None para todos

        Returns:
            Lista de municípios com id, nome e dados da microrregião
        """
        if uf:
            logger.info(f"Extraindo municípios do estado: {uf}")
            endpoint = f"/v1/localidades/estados/{uf}/municipios"
        else:
            logger.info("Extraindo todos os municípios do Brasil")
            endpoint = "/v1/localidades/municipios"

        return self._make_request(endpoint)

    def get_municipio_por_id(self, municipio_id: int) -> Dict:
        """
        Obtém dados de um município específico pelo ID.

        Args:
            municipio_id: Código IBGE do município (7 dígitos)

        Returns:
            Dados do município
        """
        logger.info(f"Extraindo município ID: {municipio_id}")
        return self._make_request(f"/v1/localidades/municipios/{municipio_id}")

    # ========== API de Agregados/SIDRA (v3) ==========

    def get_agregado(
        self,
        agregado_id: int,
        variaveis: str = "allxp",
        localidades: str = "N6[all]",
        periodos: str = "all",
        classificacao: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtém dados de um agregado (tabela) do SIDRA.

        Args:
            agregado_id: ID do agregado (ex: 6579 para população estimada)
            variaveis: Variáveis a extrair ('allxp' para todas exceto percentuais)
            localidades: Nível geográfico e seleção
                - N1: Brasil
                - N2: Região
                - N3: Estado
                - N6: Município
            periodos: Períodos a extrair ('all' ou específicos como '2020|2021')
            classificacao: Classificações adicionais (opcional)

        Returns:
            Lista com dados do agregado

        Exemplos de agregados importantes:
            - 200: População residente (Censos)
            - 6579: Estimativas populacionais
            - 5938: PIB Municipal
            - 37: PIB per capita
        """
        logger.info(
            f"Extraindo agregado {agregado_id} | "
            f"localidades={localidades} | periodos={periodos}"
        )

        endpoint = f"/v3/agregados/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}"

        params = {"localidades": localidades}
        if classificacao:
            params["classificacao"] = classificacao

        return self._make_request(endpoint, params)

    def get_populacao_estimada(
        self,
        nivel: str = "N6",
        localidade: str = "all",
        anos: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtém estimativas populacionais (agregado 6579).

        Args:
            nivel: Nível geográfico (N3=estados, N6=municípios)
            localidade: Código ou 'all' para todos
            anos: Anos específicos ou None para todos disponíveis

        Returns:
            Dados de população estimada
        """
        localidades = f"{nivel}[{localidade}]"
        periodos = anos if anos else "all"

        return self.get_agregado(
            agregado_id=6579,
            localidades=localidades,
            periodos=periodos
        )

    def get_pib_municipal(
        self,
        nivel: str = "N6",
        localidade: str = "all",
        anos: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtém PIB municipal (agregado 5938).

        Args:
            nivel: Nível geográfico
            localidade: Código ou 'all'
            anos: Anos específicos

        Returns:
            Dados de PIB municipal
        """
        localidades = f"{nivel}[{localidade}]"
        periodos = anos if anos else "all"

        return self.get_agregado(
            agregado_id=5938,
            localidades=localidades,
            periodos=periodos
        )

    def get_pib_per_capita(
        self,
        nivel: str = "N6",
        localidade: str = "all",
        anos: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtém PIB per capita (agregado 5938, variável 513).

        Args:
            nivel: Nível geográfico
            localidade: Código ou 'all'
            anos: Anos específicos

        Returns:
            Dados de PIB per capita
        """
        localidades = f"{nivel}[{localidade}]"
        periodos = anos if anos else "all"

        # PIB per capita está no agregado 5938, variável 513
        return self.get_agregado(
            agregado_id=5938,
            variaveis="513",
            localidades=localidades,
            periodos=periodos
        )


# Exemplo de uso
if __name__ == "__main__":
    from src.utils.logger import setup_logger

    setup_logger(log_level="DEBUG")

    with IBGEClient() as client:
        # Testar API de localidades
        regioes = client.get_regioes()
        print(f"Regiões: {len(regioes)}")

        estados = client.get_estados()
        print(f"Estados: {len(estados)}")

        # Municípios do Piauí
        municipios_pi = client.get_municipios("PI")
        print(f"Municípios PI: {len(municipios_pi)}")
