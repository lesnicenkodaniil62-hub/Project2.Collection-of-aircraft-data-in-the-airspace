"""
Реализация API-клиента для Nominatim (OpenStreetMap).
Отвечает за геокодирование — получение координат стран.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from src.api.base import BaseAPI

logger = logging.getLogger(__name__)


class NominatimAPI(BaseAPI):
    """
    API-клиент для сервиса Nominatim (OpenStreetMap).

    Предоставляет возможность геокодирования — получения координат
    географических объектов (стран, городов и т.д.) по их названию.

    Note:
        Nominatim не предоставляет данных о самолётах, поэтому методы
        get_aeroplanes() и get_all_states() возвращают пустые списки.
        Это сделано для соблюдения контракта абстрактного класса BaseAPI.
    """

    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org"

    def __init__(
            self,
            timeout: int = 10,
            user_agent: str = "AeroplanesApp/1.0 (educational-project)"
    ) -> None:
        """
        Инициализация клиента Nominatim.

        Args:
            timeout: Таймаут запроса в секундах
            user_agent: User-Agent (Nominatim строго требует валидный UA)
        """
        super().__init__(
            base_url=self.NOMINATIM_URL,
            timeout=timeout,
            user_agent=user_agent
        )
        logger.info(f"NominatimAPI инициализирован: {self.NOMINATIM_URL}")

    def get_coordinates(self, country_name: str) -> Optional[Tuple[float, float]]:
        """
        Получить географические координаты страны.

        Args:
            country_name: Название страны (например, "Spain", "Germany")

        Returns:
            Кортеж (latitude, longitude) или None, если страна не найдена

        Raises:
            Не бросает исключений — все ошибки логируются и возвращается None
        """
        if not country_name or not isinstance(country_name, str):
            logger.warning(f"Некорректное название страны: {country_name!r}")
            return None

        params: Dict[str, Any] = {
            "q": country_name.strip(),
            "format": "json",
            "limit": 1,
        }

        logger.info(f"Запрос координат для страны: {country_name}")
        data = self._make_request("search", params=params)

        if not data or not isinstance(data, list) or len(data) == 0:
            logger.warning(f"Страна не найдена: {country_name}")
            return None

        try:
            result: Dict[str, Any] = data[0]
            latitude: float = float(result["lat"])
            longitude: float = float(result["lon"])
            display_name: str = result.get("display_name", country_name)
            logger.info(
                f"Найдены координаты для '{display_name}': "
                f"({latitude}, {longitude})"
            )
            return latitude, longitude
        except (KeyError, ValueError, TypeError, IndexError) as e:
            logger.error(f"Ошибка парсинга ответа Nominatim: {e}")
            return None

    def get_bounding_box(
            self, country_name: str
    ) -> Optional[Tuple[float, float, float, float]]:
        """
        Получить ограничивающий прямоугольник страны.

        Метод используется для фильтрации самолётов по территории страны:
        если координаты самолёта попадают в bounding box — он считается
        находящимся в воздушном пространстве этой страны.

        Args:
            country_name: Название страны

        Returns:
            Кортеж (west, east, south, north) — границы longitudes и latitudes,
            или None, если страна не найдена.
        """
        if not country_name or not isinstance(country_name, str):
            logger.warning(f"Некорректное название страны: {country_name!r}")
            return None

        params: Dict[str, Any] = {
            "q": country_name.strip(),
            "format": "json",
            "limit": 1,
        }

        data = self._make_request("search", params=params)

        if not data or not isinstance(data, list) or len(data) == 0:
            logger.warning(f"Страна не найдена для bounding box: {country_name}")
            return None

        try:
            result: Dict[str, Any] = data[0]
            # Nominatim возвращает boundingbox как [south, north, west, east]
            bbox: List[str] = result["boundingbox"]
            south: float = float(bbox[0])
            north: float = float(bbox[1])
            west: float = float(bbox[2])
            east: float = float(bbox[3])
            logger.info(
                f"Bounding box для '{country_name}': "
                f"W={west}, E={east}, S={south}, N={north}"
            )
            return west, east, south, north
        except (KeyError, ValueError, TypeError, IndexError) as e:
            logger.error(f"Ошибка парсинга bounding box: {e}")
            return None

    def get_aeroplanes(self, country_name: str) -> List[Dict[str, Any]]:
        """
        Заглушка: Nominatim не предоставляет данных о самолётах.

        Метод реализован исключительно для соблюдения контракта
        абстрактного класса BaseAPI.

        Args:
            country_name: Название страны (игнорируется)

        Returns:
            Пустой список
        """
        logger.warning(
            f"NominatimAPI.get_aeroplanes('{country_name}') вызван, "
            "но Nominatim не предоставляет данных о самолётах. "
            "Используйте OpenSkyAPI."
        )
        return []

    def get_all_states(self) -> List[Dict[str, Any]]:
        """
        Заглушка: Nominatim не предоставляет данных о воздушных судах.

        Returns:
            Пустой список
        """
        logger.warning(
            "NominatimAPI.get_all_states() вызван, "
            "но Nominatim не предоставляет данных о воздушных судах. "
            "Используйте OpenSkyAPI."
        )
        return []