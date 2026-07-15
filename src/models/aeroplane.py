"""
Модель данных для представления воздушного судна.
Реализует принципы инкапсуляции и валидации данных.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class Aeroplane:
    """
    Модель воздушного судна.

    Атрибуты:
        callsign: Позывной ВС (до 8 символов)
        country: Страна регистрации
        velocity: Скорость полёта (м/с)
        altitude: Высота полёта (м)
        on_ground: Находится ли ВС на земле
        icao24: ICAO24 адрес ВС (уникальный идентификатор)
        latitude: Широта
        longitude: Долгота

    Пример:
        >>> aeroplane = Aeroplane("UAL1621", "United States", 268.79, 10203.18)
        >>> print(aeroplane.callsign)
        UAL1621
    """

    callsign: str
    country: str
    velocity: float
    altitude: float
    on_ground: bool = False
    icao24: str = ""
    latitude: float = 0.0
    longitude: float = 0.0

    def __post_init__(self) -> None:
        """
        Вызывается автоматически после инициализации.
        Выполняет валидацию всех атрибутов.
        """
        self.validate()
        logger.debug(f"Создан Aeroplane: {self.callsign} ({self.country})")

    def validate(self) -> None:
        """
        Валидация всех атрибутов самолёта.

        Raises:
            ValueError: Если какой-либо атрибут некорректен
            TypeError: Если тип атрибута не соответствует ожидаемому
        """
        # Валидация callsign
        if not isinstance(self.callsign, str):
            raise TypeError(f"callsign должен быть str, получено {type(self.callsign).__name__}")
        if not self.callsign.strip():
            raise ValueError("callsign не может быть пустой строкой")
        if len(self.callsign) > 8:
            raise ValueError(f"callsign не может быть длиннее 8 символов, получено: {len(self.callsign)}")

        # Валидация country
        if not isinstance(self.country, str):
            raise TypeError(f"country должен быть str, получено {type(self.country).__name__}")
        if not self.country.strip():
            raise ValueError("country не может быть пустой строкой")

        # Валидация velocity
        if not isinstance(self.velocity, (int, float)):
            raise TypeError(f"velocity должен быть числом, получено {type(self.velocity).__name__}")
        if self.velocity < 0:
            raise ValueError(f"velocity не может быть отрицательным, получено: {self.velocity}")
        if self.velocity > 1000:  # Физический предел для гражданских ВС
            logger.warning(f"velocity={self.velocity} м/с превышает типичные значения для гражданских ВС")

        # Валидация altitude
        if not isinstance(self.altitude, (int, float)):
            raise TypeError(f"altitude должен быть числом, получено {type(self.altitude).__name__}")
        if self.altitude < 0:
            raise ValueError(f"altitude не может быть отрицательным, получено: {self.altitude}")
        if self.altitude > 15000:  # Физический предел для гражданских ВС
            logger.warning(f"altitude={self.altitude} м превышает типичные значения для гражданских ВС")

        # Валидация on_ground
        if not isinstance(self.on_ground, bool):
            raise TypeError(f"on_ground должен быть bool, получено {type(self.on_ground).__name__}")

        # Валидация icao24
        if not isinstance(self.icao24, str):
            raise TypeError(f"icao24 должен быть str, получено {type(self.icao24).__name__}")
        if self.icao24 and len(self.icao24) != 6:
            logger.warning(f"icao24 должен содержать 6 символов, получено: {len(self.icao24)}")

        # Валидация координат
        if not isinstance(self.latitude, (int, float)):
            raise TypeError(f"latitude должен быть числом, получено {type(self.latitude).__name__}")
        if not isinstance(self.longitude, (int, float)):
            raise TypeError(f"longitude должен быть числом, получено {type(self.longitude).__name__}")
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"latitude должен быть в диапазоне [-90, 90], получено: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"longitude должен быть в диапазоне [-180, 180], получено: {self.longitude}")

    def compare_by_speed(self, other: "Aeroplane") -> int:
        """
        Сравнение двух самолётов по скорости.

        Args:
            other: Другой самолёт для сравнения

        Returns:
            -1 если self < other по скорости
             0 если self == other по скорости
             1 если self > other по скорости
        """
        if not isinstance(other, Aeroplane):
            raise TypeError(f"Можно сравнивать только с Aeroplane, получено {type(other).__name__}")

        if self.velocity < other.velocity:
            return -1
        elif self.velocity > other.velocity:
            return 1
        return 0

    def compare_by_altitude(self, other: "Aeroplane") -> int:
        """
        Сравнение двух самолётов по высоте.

        Args:
            other: Другой самолёт для сравнения

        Returns:
            -1 если self < other по высоте
             0 если self == other по высоте
             1 если self > other по высоте
        """
        if not isinstance(other, Aeroplane):
            raise TypeError(f"Можно сравнивать только с Aeroplane, получено {type(other).__name__}")

        if self.altitude < other.altitude:
            return -1
        elif self.altitude > other.altitude:
            return 1
        return 0

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать самолёт в словарь для сериализации.

        Returns:
            Словарь с данными о самолёте
        """
        return {
            "callsign": self.callsign.strip(),
            "country": self.country.strip(),
            "velocity": round(self.velocity, 2),
            "altitude": round(self.altitude, 2),
            "on_ground": self.on_ground,
            "icao24": self.icao24,
            "latitude": round(self.latitude, 6),
            "longitude": round(self.longitude, 6),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Aeroplane":
        """
        Создать самолёт из словаря.

        Args:
            data: Словарь с данными о самолёте

        Returns:
            Экземпляр Aeroplane

        Raises:
            ValueError: Если обязательные поля отсутствуют
        """
        required_fields = ["callsign", "country", "velocity", "altitude"]
        for field_name in required_fields:
            if field_name not in data:
                raise ValueError(f"Отсутствует обязательное поле: {field_name}")

        return cls(
            callsign=data["callsign"],
            country=data["country"],
            velocity=float(data["velocity"]),
            altitude=float(data["altitude"]),
            on_ground=bool(data.get("on_ground", False)),
            icao24=str(data.get("icao24", "")),
            latitude=float(data.get("latitude", 0.0)),
            longitude=float(data.get("longitude", 0.0)),
        )

    @classmethod
    def cast_to_object_list(cls, states: List[Dict[str, Any]], default_country: str = "") -> List["Aeroplane"]:
        """
        Преобразовать список словарей (от API) в список объектов Aeroplane.

        Args:
            states: Список словарей с данными от API
            default_country: Страна по умолчанию, если не указана в данных

        Returns:
            Список объектов Aeroplane
        """
        aeroplanes: List[Aeroplane] = []

        for state in states:
            try:
                # Извлекаем данные с учётом разных форматов
                callsign: str = str(state.get("callsign", "")).strip()
                country: str = str(state.get("origin_country", default_country)).strip()

                # Пропускаем записи без позывного
                if not callsign:
                    logger.debug(f"Пропущена запись без callsign: {state}")
                    continue

                # Обрабатываем None значения для числовых полей
                velocity_raw = state.get("velocity")
                altitude_raw = state.get("baro_altitude") or state.get("geo_altitude")

                velocity: float = float(velocity_raw) if velocity_raw is not None else 0.0
                altitude: float = float(altitude_raw) if altitude_raw is not None else 0.0

                aeroplane = cls(
                    callsign=callsign,
                    country=country if country else default_country,
                    velocity=velocity,
                    altitude=altitude,
                    on_ground=bool(state.get("on_ground", False)),
                    icao24=str(state.get("icao24", "")),
                    latitude=float(state.get("latitude", 0.0) or 0.0),
                    longitude=float(state.get("longitude", 0.0) or 0.0),
                )
                aeroplanes.append(aeroplane)

            except (ValueError, TypeError, KeyError) as e:
                logger.warning(f"Не удалось преобразовать запись в Aeroplane: {e}, данные: {state}")
                continue

        logger.info(f"Успешно преобразовано {len(aeroplanes)} из {len(states)} записей")
        return aeroplanes

    def __str__(self) -> str:
        """Читаемое представление для вывода в консоль."""
        return f"✈ {self.callsign:8s} | {self.country:20s} | " f"V={self.velocity:7.2f} м/с | H={self.altitude:8.2f} м"

    def __repr__(self) -> str:
        """Техническое представление для отладки."""
        return (
            f"Aeroplane(callsign={self.callsign!r}, country={self.country!r}, "
            f"velocity={self.velocity}, altitude={self.altitude})"
        )
