"""
Тесты модели Aeroplane. Функциональный стиль, параметризация.
"""

from typing import Any, List, Type

import pytest

from src.models.aeroplane import Aeroplane


@pytest.mark.parametrize(
    "callsign, country, velocity, altitude, expected_exception",
    [
        ("AFL123", "Russia", 250.0, 10000.0, None),
        ("", "Russia", 250.0, 10000.0, ValueError),
        ("AFL123456789", "Russia", 250.0, 10000.0, ValueError),
        ("AFL123", "Russia", -10.0, 10000.0, ValueError),
        ("AFL123", "Russia", 250.0, -100.0, ValueError),
        ("AFL123", "Russia", "fast", 10000.0, TypeError),  # type: ignore[arg-type]
    ],
)
def test_aeroplane_validation(
    callsign: str,
    country: str,
    velocity: float,
    altitude: float,
    expected_exception: Type[Exception] | None,
) -> None:
    """Тест валидации атрибутов при создании объекта."""
    if expected_exception is not None:
        with pytest.raises(expected_exception):
            Aeroplane(callsign=callsign, country=country, velocity=velocity, altitude=altitude)
    else:
        plane = Aeroplane(callsign=callsign, country=country, velocity=velocity, altitude=altitude)
        assert plane.callsign == callsign
        assert plane.velocity == velocity


def test_aeroplane_to_dict(aeroplane: Aeroplane) -> None:
    """Тест преобразования объекта в словарь."""
    result = aeroplane.to_dict()
    assert isinstance(result, dict)
    assert result["callsign"] == "AFL123"
    assert result["velocity"] == 250.5


def test_aeroplane_from_dict_success(valid_aeroplane_data: dict[str, Any]) -> None:
    """Тест создания объекта из словаря."""
    plane = Aeroplane.from_dict(valid_aeroplane_data)
    assert plane.callsign == "AFL123"
    assert isinstance(plane.on_ground, bool)


def test_aeroplane_from_dict_missing_field() -> None:
    """Тест обработки отсутствия обязательных полей."""
    with pytest.raises(ValueError, match="Отсутствует обязательное поле"):
        Aeroplane.from_dict({"callsign": "AFL123", "velocity": 100, "altitude": 5000})


def test_aeroplane_compare_by_speed(aeroplane_list: List[Aeroplane]) -> None:
    """Тест сравнения самолётов по скорости."""
    p1, p2 = aeroplane_list[0], aeroplane_list[1]
    assert p1.compare_by_speed(p2) == -1
    assert p2.compare_by_speed(p1) == 1
    assert p1.compare_by_speed(p1) == 0

    with pytest.raises(TypeError):
        p1.compare_by_speed("not_a_plane")  # type: ignore[arg-type]


def test_cast_to_object_list_success(mock_raw_opensky_state: List[List[Any]]) -> None:
    """Тест массового преобразования сырых данных API в объекты."""
    keys = [
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
    states = [dict(zip(keys, state)) for state in mock_raw_opensky_state]

    planes = Aeroplane.cast_to_object_list(states, default_country="Unknown")

    assert len(planes) == 1  # Вторая запись отброшена из-за пустого callsign
    assert planes[0].callsign == "CALL1"
    assert planes[0].velocity == 250.0
