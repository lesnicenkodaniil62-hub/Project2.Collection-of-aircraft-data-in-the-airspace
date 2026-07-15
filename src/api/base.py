"""
Абстрактный базовый класс для работы с API.
Реализует принцип SRP (SOLID) — один класс отвечает за контракт API-клиента.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


class BaseAPI(ABC):
    """
    Абстрактный базовый класс для API-клиентов.

    Все классы-наследники обязаны реализовать методы получения данных
    из конкретных источников (Nominatim, OpenSky и т.д.).
    """

    def __init__(self, base_url: str, timeout: int = 10, user_agent: str = "AeroplanesApp/1.0") -> None:
        """
        Инициализация API-клиента.

        Args:
            base_url: Базовый URL API
            timeout: Таймаут запроса в секундах
            user_agent: User-Agent для запросов
        """
        self.base_url: str = base_url.rstrip("/")
        self.timeout: int = timeout
        self.user_agent: str = user_agent
        self.session: requests.Session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        logger.info(f"Инициализирован API-клиент: {self.__class__.__name__} ({self.base_url})")

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET"
    ) -> Optional[Dict[str, Any] | List[Any]]:
        """
        Вспомогательный метод для выполнения HTTP-запроса.

        Args:
            endpoint: Эндпоинт API (добавляется к base_url)
            params: Параметры запроса
            method: HTTP-метод (GET/POST)

        Returns:
            JSON-ответ или None при ошибке
        """
        url: str = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            logger.debug(f"Запрос: {method} {url}, params={params}")
            response: requests.Response = self.session.request(
                method=method, url=url, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Таймаут запроса к {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP ошибка при запросе к {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к {url}: {e}")
            return None
        except ValueError as e:
            logger.error(f"Ошибка парсинга JSON от {url}: {e}")
            return None

    @abstractmethod
    def get_coordinates(self, country_name: str) -> Optional[Tuple[float, float]]:
        """
        Получить географические координаты страны.

        Args:
            country_name: Название страны

        Returns:
            Кортеж (latitude, longitude) или None
        """
        pass

    @abstractmethod
    def get_aeroplanes(self, country_name: str) -> List[Dict[str, Any]]:
        """
        Получить информацию о самолётах в воздушном пространстве страны.

        Args:
            country_name: Название страны

        Returns:
            Список словарей с данными о самолётах
        """
        pass

    @abstractmethod
    def get_all_states(self) -> List[Dict[str, Any]]:
        """
        Получить все состояния воздушных судов (без фильтрации).

        Returns:
            Список словарей с данными
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(base_url={self.base_url})>"
