"""
Абстрактный базовый класс для работы с API.

Архитектура разделена на два уровня:
1. APIClientMixin — миксин-класс с реализацией HTTP-запросов и инициализации
   сессии. Содержит всю «грязную» работу с сетью.
2. BaseAPI — чистый абстрактный класс, наследующий APIClientMixin и ABC.
   Содержит ТОЛЬКО объявления абстрактных методов (@abstractmethod) без
   какой-либо реализации, что соответствует принципу контрактного
   программирования.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, cast

import requests

logger = logging.getLogger(__name__)


class APIClientMixin:
    """
    Миксин-класс, предоставляющий реализацию HTTP-запросов для API-клиентов.

    Вынесен из абстрактного класса BaseAPI, чтобы последний содержал только
    объявления методов (@abstractmethod) без реализации. Это соответствует
    принципу разделения ответственности (SRP): миксин отвечает за транспортный
    уровень, а абстрактный класс — за контракт данных.

    Атрибуты:
        base_url: Базовый URL API (без завершающего слэша).
        timeout: Таймаут HTTP-запроса в секундах.
        user_agent: Строка User-Agent для HTTP-заголовков.
        session: Экземпляр requests.Session для переиспользования соединений.
    """

    def __init__(self, base_url: str, timeout: int = 10, user_agent: str = "AeroplanesApp/1.0") -> None:
        """
        Инициализация HTTP-клиента.

        Args:
            base_url: Базовый URL API.
            timeout: Таймаут запроса в секундах.
            user_agent: User-Agent для запросов.
        """
        self.base_url: str = base_url.rstrip("/")
        self.timeout: int = timeout
        self.user_agent: str = user_agent
        self.session: requests.Session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        logger.info(f"Инициализирован API-клиент: " f"{self.__class__.__name__} ({self.base_url})")

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET"
    ) -> Optional[Dict[str, Any] | List[Any]]:
        """
        Вспомогательный метод для выполнения HTTP-запроса.

        Обрабатывает все потенциальные исключения (Timeout, HTTPError,
        RequestException, ValueError) и возвращает None при ошибке,
        предотвращая падение приложения (Defensive Programming).

        Args:
            endpoint: Эндпоинт API (добавляется к base_url).
            params: Параметры запроса.
            method: HTTP-метод (GET/POST).

        Returns:
            JSON-ответ или None при ошибке.
        """
        url: str = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            logger.debug(f"Запрос: {method} {url}, params={params}")
            response: requests.Response = self.session.request(
                method=method, url=url, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            return cast(Optional[Dict[str, Any] | List[Any]], response.json())
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

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"<{self.__class__.__name__}(base_url={self.base_url})>"


class BaseAPI(APIClientMixin, ABC):
    """
    Абстрактный базовый класс для API-клиентов.

    Содержит ТОЛЬКО объявления абстрактных методов без реализации.
    Вся логика HTTP-запросов вынесена в миксин APIClientMixin.

    Все классы-наследники обязаны реализовать методы получения данных
    из конкретных источников (Nominatim, OpenSky и т.д.).
    """

    @abstractmethod
    def get_coordinates(self, country_name: str) -> Optional[Tuple[float, float]]:
        """Получить географические координаты страны."""
        pass

    @abstractmethod
    def get_aeroplanes(self, country_name: str) -> List[Dict[str, Any]]:
        """Получить информацию о самолётах в воздушном пространстве страны."""
        pass

    @abstractmethod
    def get_all_states(self) -> List[Dict[str, Any]]:
        """Получить все состояния воздушных судов (без фильтрации)."""
        pass
