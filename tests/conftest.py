"""
Глобальные фикстуры pytest для всего проекта.
Используется функциональный стиль без классов.
"""

from typing import Any, List

import pytest

from src.models.aeroplane import Aeroplane


@pytest.fixture
def valid_aeroplane_data() -> dict[str, Any]:
    """Фикстура: эталонный словарь валидных данных для самолёта."""
    return {
        "callsign": "AFL123",
        "country": "Russia",
        "velocity": 250.5,
        "altitude": 10000.0,
        "on_ground": False,
        "icao24": "123456",
        "latitude": 55.75,
        "longitude": 37.61,
    }


@pytest.fixture
def aeroplane(valid_aeroplane_data: dict[str, Any]) -> Aeroplane:
    """Фикстура: готовый валидный объект Aeroplane."""
    return Aeroplane(**valid_aeroplane_data)


@pytest.fixture
def aeroplane_list() -> List[Aeroplane]:
    """Фикстура: разнородный список самолётов для тестов фильтрации и сортировки."""
    return [
        Aeroplane(callsign="AFL100", country="Russia", velocity=200.0, altitude=5000.0),
        Aeroplane(callsign="DLH400", country="Germany", velocity=250.0, altitude=10000.0),
        Aeroplane(callsign="BAW500", country="United Kingdom", velocity=150.0, altitude=2000.0, on_ground=True),
        Aeroplane(callsign="SBI777", country="Russia", velocity=300.0, altitude=11000.0),
    ]


@pytest.fixture
def mock_raw_opensky_state() -> List[List[Any]]:
    """Фикстура: имитация сырого ответа от OpenSky Network API (список списков)."""
    return [
        [
            "abc123",
            "CALL1 ",
            "Russia",
            1600000000,
            1600000005,
            37.61,
            55.75,
            10000.0,
            False,
            250.0,
            90.0,
            0.0,
            None,
            10000.0,
            "1234",
            False,
            0,
        ],
        [
            "def456",
            "",
            "Germany",
            1600000000,
            1600000005,
            13.40,
            52.52,
            None,
            True,
            None,
            0.0,
            0.0,
            None,
            None,
            "0000",
            False,
            0,
        ],
    ]
