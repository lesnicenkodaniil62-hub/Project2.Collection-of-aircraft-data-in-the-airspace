"""
Модель данных для представления воздушного судна.

Реализует принципы инкапсуляции и строгой валидации данных.
Каждый атрибут валидируется в __init__ через отдельный метод _validate_*,
что обеспечивает целостность объекта с момента создания.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

__all__ = ["Aeroplane"]


class Aeroplane:
    """
    Модель воздушного судна.

    Атрибуты:
        callsign: Позывной ВС (до 8 символов).
        country: Страна регистрации.
        velocity: Скорость полёта (м/с).
        altitude: Высота полёта (м).
        on_ground: Находится ли ВС на земле.
        icao24: ICAO24 адрес ВС (уникальный идентификатор).
        latitude: Широта.
        longitude: Долгота.
    """

    def __init__(
        self,
        callsign: str,
        country: str,
        velocity: float,
        altitude: float,
        on_ground: bool = False,
        icao24: str = "",
        latitude: float = 0.0,
        longitude: float = 0.0,
    ) -> None:
        """
        Инициализация и валидация всех атрибутов самолёта.

        Каждый атрибут проходит проверку через отдельный метод _validate_*,
        который возвращает очищенное значение или выбрасывает исключение.

        Args:
            callsign: Позывной ВС (до 8 символов).
            country: Страна регистрации.
            velocity: Скорость полёта (м/с).
            altitude: Высота полёта (м).
            on_ground: Находится ли ВС на земле.
            icao24: ICAO24 адрес ВС.
            latitude: Широта [-90, 90].
            longitude: Долгота [-180, 180].

        Raises:
            TypeError: Если тип атрибута не соответствует ожидаемому.
            ValueError: Если значение атрибута вне допустимого диапазона.
        """
        self.callsign: str = self._validate_callsign(callsign)
        self.country: str = self._validate_country(country)
        self.velocity: float = self._validate_velocity(velocity)
        self.altitude: float = self._validate_altitude(altitude)
        self.on_ground: bool = self._validate_on_ground(on_ground)
        self.icao24: str = self._validate_icao24(icao24)
        self.latitude: float = self._validate_latitude(latitude)
        self.longitude: float = self._validate_longitude(longitude)
        logger.debug(f"Создан Aeroplane: {self.callsign} ({self.country})")

    # ==================================================================
    # Методы валидации атрибутов
    # ==================================================================

    @staticmethod
    def _validate_callsign(callsign: Any) -> str:
        """Валидация позывного: тип, пустота, длина."""
        if not isinstance(callsign, str):
            raise TypeError(f"callsign должен быть str, " f"получено {type(callsign).__name__}")
        if not callsign.strip():
            raise ValueError("callsign не может быть пустой строкой")
        if len(callsign) > 8:
            raise ValueError(f"callsign не может быть длиннее 8 символов, " f"получено: {len(callsign)}")
        return callsign

    @staticmethod
    def _validate_country(country: Any) -> str:
        """Валидация страны: тип и пустота."""
        if not isinstance(country, str):
            raise TypeError(f"country должен быть str, " f"получено {type(country).__name__}")
        if not country.strip():
            raise ValueError("country не может быть пустой строкой")
        return country

    @staticmethod
    def _validate_velocity(velocity: Any) -> float:
        """Валидация скорости: тип, неотрицательность, физический предел."""
        if not isinstance(velocity, (int, float)):
            raise TypeError(f"velocity должен быть числом, " f"получено {type(velocity).__name__}")
        if velocity < 0:
            raise ValueError(f"velocity не может быть отрицательным, получено: {velocity}")
        if velocity > 1000:
            logger.warning(f"velocity={velocity} м/с превышает типичные " f"значения для гражданских ВС")
        return float(velocity)

    @staticmethod
    def _validate_altitude(altitude: Any) -> float:
        """Валидация высоты: тип, неотрицательность, физический предел."""
        if not isinstance(altitude, (int, float)):
            raise TypeError(f"altitude должен быть числом, " f"получено {type(altitude).__name__}")
        if altitude < 0:
            raise ValueError(f"altitude не может быть отрицательным, получено: {altitude}")
        if altitude > 15000:
            logger.warning(f"altitude={altitude} м превышает типичные " f"значения для гражданских ВС")
        return float(altitude)

    @staticmethod
    def _validate_on_ground(on_ground: Any) -> bool:
        """Валидация статуса 'на земле': тип."""
        if not isinstance(on_ground, bool):
            raise TypeError(f"on_ground должен быть bool, " f"получено {type(on_ground).__name__}")
        return on_ground

    @staticmethod
    def _validate_icao24(icao24: Any) -> str:
        """Валидация ICAO24: тип и длина."""
        if not isinstance(icao24, str):
            raise TypeError(f"icao24 должен быть str, " f"получено {type(icao24).__name__}")
        if icao24 and len(icao24) != 6:
            logger.warning(f"icao24 должен содержать 6 символов, " f"получено: {len(icao24)}")
        return icao24

    @staticmethod
    def _validate_latitude(latitude: Any) -> float:
        """Валидация широты: тип и диапазон [-90, 90]."""
        if not isinstance(latitude, (int, float)):
            raise TypeError(f"latitude должен быть числом, " f"получено {type(latitude).__name__}")
        if not (-90 <= latitude <= 90):
            raise ValueError(f"latitude должен быть в диапазоне [-90, 90], " f"получено: {latitude}")
        return float(latitude)

    @staticmethod
    def _validate_longitude(longitude: Any) -> float:
        """Валидация долготы: тип и диапазон [-180, 180]."""
        if not isinstance(longitude, (int, float)):
            raise TypeError(f"longitude должен быть числом, " f"получено {type(longitude).__name__}")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"longitude должен быть в диапазоне [-180, 180], " f"получено: {longitude}")
        return float(longitude)

    # ==================================================================
    # Методы сравнения
    # ==================================================================

    def compare_by_speed(self, other: "Aeroplane") -> int:
        """Сравнение двух самолётов по скорости."""
        if not isinstance(other, Aeroplane):
            raise TypeError(f"Можно сравнивать только с Aeroplane, " f"получено {type(other).__name__}")
        if self.velocity < other.velocity:
            return -1
        elif self.velocity > other.velocity:
            return 1
        return 0

    def compare_by_altitude(self, other: "Aeroplane") -> int:
        """Сравнение двух самолётов по высоте."""
        if not isinstance(other, Aeroplane):
            raise TypeError(f"Можно сравнивать только с Aeroplane, " f"получено {type(other).__name__}")
        if self.altitude < other.altitude:
            return -1
        elif self.altitude > other.altitude:
            return 1
        return 0

    # ==================================================================
    # Сериализация / Десериализация
    # ==================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать самолёт в словарь для сериализации."""
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
        """Создать самолёт из словаря."""
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
        """Преобразовать список словарей (от API) в список объектов."""
        aeroplanes: List[Aeroplane] = []

        for state in states:
            try:
                callsign: str = str(state.get("callsign", "")).strip()
                country: str = str(state.get("origin_country", default_country)).strip()

                if not callsign:
                    logger.debug(f"Пропущена запись без callsign: {state}")
                    continue

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
                logger.warning(f"Не удалось преобразовать запись в Aeroplane: " f"{e}, данные: {state}")
                continue

        logger.info(f"Успешно преобразовано {len(aeroplanes)} " f"из {len(states)} записей")
        return aeroplanes

    # ==================================================================
    # Строковые представления
    # ==================================================================

    def __str__(self) -> str:
        """Читаемое представление для вывода в консоль."""
        return f"✈ {self.callsign:8s} | {self.country:20s} | " f"V={self.velocity:7.2f} м/с | H={self.altitude:8.2f} м"

    def __repr__(self) -> str:
        """Техническое представление для отладки."""
        return (
            f"Aeroplane(callsign={self.callsign!r}, "
            f"country={self.country!r}, "
            f"velocity={self.velocity}, altitude={self.altitude})"
        )

    def __eq__(self, other: object) -> bool:
        """
        Сравнение двух самолётов по всем атрибутам.

        Реализовано через сравнение кортежей атрибутов, что делает код
        более читаемым и соответствует принципу DRY. Также устраняет
        предупреждение flake8 W503 (line break before binary operator).

        Args:
            other: Объект для сравнения.

        Returns:
            True если все атрибуты совпадают, False иначе.
            NotImplemented если other не является Aeroplane.
        """
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return (
            self.callsign,
            self.country,
            self.velocity,
            self.altitude,
            self.on_ground,
            self.icao24,
            self.latitude,
            self.longitude,
        ) == (
            other.callsign,
            other.country,
            other.velocity,
            other.altitude,
            other.on_ground,
            other.icao24,
            other.latitude,
            other.longitude,
        )
