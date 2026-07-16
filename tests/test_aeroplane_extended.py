"""
Расширенные тесты модели Aeroplane для увеличения покрытия кода.
"""

from typing import Any, List

import pytest

from src.models.aeroplane import Aeroplane


def test_aeroplane_validation_warnings(caplog: pytest.LogCaptureFixture) -> None:
    """Тест генерации предупреждений при экстремальных значениях."""
    with caplog.at_level("WARNING"):
        Aeroplane(
            callsign="HIGH",
            country="USA",
            velocity=1100.0,  # Превышает типичные значения
            altitude=16000.0,  # Превышает типичные значения
        )
    assert "превышает типичные значения" in caplog.text


def test_aeroplane_compare_by_speed(aeroplane_list: List[Aeroplane]) -> None:
    """Тест сравнения самолётов по скорости."""
    p1, p2 = aeroplane_list[0], aeroplane_list[1]  # 200.0 и 250.0
    assert p1.compare_by_speed(p2) == -1
    assert p2.compare_by_speed(p1) == 1
    assert p1.compare_by_speed(p1) == 0

    with pytest.raises(TypeError):
        p1.compare_by_speed("not_a_plane")  # type: ignore[arg-type]


def test_aeroplane_compare_by_altitude(aeroplane_list: List[Aeroplane]) -> None:
    """Тест сравнения самолётов по высоте."""
    p1, p2 = aeroplane_list[0], aeroplane_list[1]  # 5000.0 и 10000.0
    assert p1.compare_by_altitude(p2) == -1
    assert p2.compare_by_altitude(p1) == 1

    with pytest.raises(TypeError):
        p1.compare_by_altitude(None)  # type: ignore[arg-type]


def test_aeroplane_from_dict_success(valid_aeroplane_data: dict[str, Any]) -> None:
    """Тест создания объекта из словаря."""
    plane = Aeroplane.from_dict(valid_aeroplane_data)
    assert plane.callsign == "AFL123"
    assert isinstance(plane.on_ground, bool)


def test_aeroplane_from_dict_missing_field() -> None:
    """Тест обработки отсутствия обязательных полей."""
    with pytest.raises(ValueError, match="Отсутствует обязательное поле"):
        Aeroplane.from_dict({"callsign": "AFL123", "velocity": 100, "altitude": 5000})


def test_aeroplane_from_dict_with_optional_fields() -> None:
    """Тест создания объекта из словаря с опциональными полями."""
    data = {
        "callsign": "TEST1",
        "country": "USA",
        "velocity": 200.0,
        "altitude": 10000.0,
        "on_ground": True,
        "icao24": "abc123",
        "latitude": 40.0,
        "longitude": -74.0,
    }
    plane = Aeroplane.from_dict(data)
    assert plane.on_ground is True
    assert plane.icao24 == "abc123"
    assert plane.latitude == 40.0
    assert plane.longitude == -74.0


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


def test_cast_to_object_list_handles_none() -> None:
    """Тест обработки отсутствующих числовых значений (None) при конвертации."""
    states = [{"callsign": "TEST1", "origin_country": "USA", "velocity": None, "baro_altitude": None}]
    planes = Aeroplane.cast_to_object_list(states)

    assert len(planes) == 1
    assert planes[0].velocity == 0.0  # Fallback значение
    assert planes[0].altitude == 0.0  # Fallback значение


def test_cast_to_object_list_uses_geo_altitude() -> None:
    """Тест использования geo_altitude, если baro_altitude отсутствует."""
    states = [
        {
            "callsign": "TEST1",
            "origin_country": "USA",
            "velocity": 200.0,
            "baro_altitude": None,
            "geo_altitude": 10000.0,
        }
    ]
    planes = Aeroplane.cast_to_object_list(states)

    assert len(planes) == 1
    assert planes[0].altitude == 10000.0


def test_cast_to_object_list_skips_invalid_records() -> None:
    """Тест пропуска некорректных записей при массовом преобразовании."""
    states = [
        {"callsign": "VALID1", "origin_country": "USA", "velocity": 200.0, "altitude": 10000.0},
        {"callsign": "", "origin_country": "USA", "velocity": 200.0, "altitude": 10000.0},  # Пустой callsign
        {
            "callsign": "VALID2",
            "origin_country": "USA",
            "velocity": "invalid",
            "altitude": 10000.0,
        },  # Некорректный velocity
    ]
    planes = Aeroplane.cast_to_object_list(states)

    assert len(planes) == 1  # Только первая запись валидна
    assert planes[0].callsign == "VALID1"


def test_aeroplane_str_representation(aeroplane: Aeroplane) -> None:
    """Тест строкового представления объекта."""
    result = str(aeroplane)
    assert "AFL123" in result
    assert "Russia" in result
    assert "250.50" in result
    assert "10000.00" in result


def test_aeroplane_repr_representation(aeroplane: Aeroplane) -> None:
    """Тест технического представления объекта."""
    result = repr(aeroplane)
    assert "Aeroplane" in result
    assert "callsign='AFL123'" in result
    assert "country='Russia'" in result


def test_aeroplane_to_dict_roundtrip(valid_aeroplane_data: dict[str, Any]) -> None:
    """Тест сериализации и десериализации (roundtrip)."""
    plane = Aeroplane.from_dict(valid_aeroplane_data)
    serialized = plane.to_dict()
    restored = Aeroplane.from_dict(serialized)

    assert restored.callsign == plane.callsign
    assert restored.country == plane.country
    assert restored.velocity == plane.velocity
    assert restored.altitude == plane.altitude


@pytest.mark.parametrize(
    "callsign, expected_exception",
    [
        ("", ValueError),  # Пустая строка
        ("A" * 9, ValueError),  # Слишком длинный (>8 символов)
        (123, TypeError),  # Не строка
    ],
)
def test_aeroplane_callsign_validation(callsign: Any, expected_exception: type[Exception]) -> None:
    """Параметризованный тест валидации callsign."""
    with pytest.raises(expected_exception):
        Aeroplane(callsign=callsign, country="USA", velocity=200.0, altitude=10000.0)


@pytest.mark.parametrize(
    "velocity, expected_exception",
    [
        (-10.0, ValueError),  # Отрицательная скорость
        ("fast", TypeError),  # Не число
    ],
)
def test_aeroplane_velocity_validation(velocity: Any, expected_exception: type[Exception]) -> None:
    """Параметризованный тест валидации velocity."""
    with pytest.raises(expected_exception):
        Aeroplane(callsign="TEST1", country="USA", velocity=velocity, altitude=10000.0)


@pytest.mark.parametrize(
    "latitude, longitude, expected_exception",
    [
        (91.0, 0.0, ValueError),  # Широта > 90
        (-91.0, 0.0, ValueError),  # Широта < -90
        (0.0, 181.0, ValueError),  # Долгота > 180
        (0.0, -181.0, ValueError),  # Долгота < -180
    ],
)
def test_aeroplane_coordinates_validation(
    latitude: float, longitude: float, expected_exception: type[Exception]
) -> None:
    """Параметризованный тест валидации координат."""
    with pytest.raises(expected_exception):
        Aeroplane(
            callsign="TEST1", country="USA", velocity=200.0, altitude=10000.0, latitude=latitude, longitude=longitude
        )
