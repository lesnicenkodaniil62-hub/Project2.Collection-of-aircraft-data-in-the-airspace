"""
Реализация API-клиента для OpenSky Network.
Отвечает за получение информации о воздушных судах в реальном времени.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from src.api.base import BaseAPI

logger = logging.getLogger(__name__)


class OpenSkyAPI(BaseAPI):
    """
    API-клиент для сервиса OpenSky Network.
    Предоставляет данные о воздушных судах в реальном времени.

    Документация: https://openskynetwork.github.io/opensky-api/rest.html
    """

    OPENSKY_URL: str = "https://opensky-network.org/api"

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 15,
        user_agent: str = "AeroplanesApp/1.0",
    ) -> None:
        """
        Инициализация клиента OpenSky.

        Args:
            username: Имя пользователя (для повышения лимитов запросов)
            password: Пароль
            timeout: Таймаут запроса в секундах
            user_agent: User-Agent для HTTP-заголовков
        """
        super().__init__(base_url=self.OPENSKY_URL, timeout=timeout, user_agent=user_agent)

        if username and password:
            self.session.auth = (username, password)
            logger.info("OpenSkyAPI инициализирован с аутентификацией (повышенные лимиты)")
        else:
            logger.info("OpenSkyAPI инициализирован без аутентификации (публичный доступ, ~4 запроса/мин)")

    def get_coordinates(self, country_name: str) -> Optional[Tuple[float, float]]:
        """
        Заглушка: OpenSky не предоставляет сервис геокодирования.

        Args:
            country_name: Игнорируется

        Returns:
            None
        """
        logger.warning("OpenSkyAPI не поддерживает геокодинг. " "Для получения координат используйте NominatimAPI.")
        return None

    def get_all_states(self) -> List[Dict[str, Any]]:
        """
        Получить все состояния воздушных судов без фильтрации.

        Returns:
            Список словарей с данными о каждом ВС
        """
        logger.info("Получение всех состояний воздушных судов (OpenSky)...")
        data = self._make_request("states/all")

        if data and isinstance(data, dict) and "states" in data:
            states_list: List[Dict[str, Any]] = self._parse_states(data["states"])
            logger.info(f"Получено {len(states_list)} состояний")
            return states_list
        return []

    def get_aeroplanes(self, country_name: str) -> List[Dict[str, Any]]:
        """
        Получить самолёты по стране регистрации.

        Note:
            OpenSky API фильтрует ВС по стране регистрации (origin_country),
            а не по географическому положению в воздушном пространстве.
            Для фильтрации по местоположению используйте bounding box из NominatimAPI.

        Args:
            country_name: Название или код страны (ISO 3166-1)

        Returns:
            Список словарей с данными о ВС, зарегистрированных в данной стране
        """
        if not country_name or not isinstance(country_name, str):
            logger.warning(f"Некорректное название страны: {country_name!r}")
            return []

        logger.info(f"Запрос ВС для страны: {country_name}")
        params: Dict[str, Any] = {"country": country_name.strip()}

        data = self._make_request("states/all", params=params)

        if data and isinstance(data, dict) and "states" in data:
            states_list: List[Dict[str, Any]] = self._parse_states(data["states"])
            logger.info(f"Найдено {len(states_list)} ВС для '{country_name}'")
            return states_list
        return []

    def _parse_states(self, raw_states: Optional[List[List[Any]]]) -> List[Dict[str, Any]]:
        """
        Преобразовать ответ OpenSky (список списков) в список словарей.

        OpenSky возвращает states как массив массивов:
        [icao24, callsign, origin_country, time_position, last_contact,
         longitude, latitude, baro_altitude, on_ground, velocity,
         heading, vertical_rate, sensors, geo_altitude, squawk, spi, position_source]

        Args:
            raw_states: Сырые данные от API

        Returns:
            Список словарей с именованными полями
        """
        if not raw_states:
            return []

        # Индексы полей согласно официальной документации OpenSky
        keys: List[str] = [
            "icao24",
            "callsign",
            "origin_country",
            "time_position",
            "last_contact",
            "longitude",
            "latitude",
            "baro_altitude",
            "on_ground",
            "velocity",
            "heading",
            "vertical_rate",
            "sensors",
            "geo_altitude",
            "squawk",
            "spi",
            "position_source",
        ]

        parsed: List[Dict[str, Any]] = []
        for state in raw_states:
            if isinstance(state, list) and len(state) >= len(keys):
                record: Dict[str, Any] = dict(zip(keys, state))
                parsed.append(record)
            else:
                logger.debug(f"Пропущена запись с некорректным форматом: {state}")

        return parsed

    def __repr__(self) -> str:
        return f"<OpenSkyAPI(auth={'настроен' if self.session.auth else 'нет'}, timeout={self.timeout})>"
