"""
Тесты клиента NominatimAPI с использованием Mock и Parametrize.
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.api.nominatim import NominatimAPI


@pytest.fixture
def nominatim_client() -> NominatimAPI:
    """Фикстура клиента Nominatim."""
    return NominatimAPI(timeout=5)


@patch.object(NominatimAPI, "_make_request")
def test_get_coordinates_success(mock_request: MagicMock, nominatim_client: NominatimAPI) -> None:
    """Тест успешного получения координат."""
    mock_request.return_value = [{"lat": "55.75", "lon": "37.61", "display_name": "Moscow"}]
    result = nominatim_client.get_coordinates("Russia")
    assert result == (55.75, 37.61)
    assert isinstance(result[0], float)


@pytest.mark.parametrize("input_val", ["", None, 123])  # type: ignore[arg-type]
def test_get_coordinates_invalid_input(nominatim_client: NominatimAPI, input_val: Any) -> None:
    """Тест устойчивости к некорректным входным данным."""
    result = nominatim_client.get_coordinates(input_val)
    assert result is None


@patch.object(NominatimAPI, "_make_request")
def test_get_coordinates_empty_response(mock_request: MagicMock, nominatim_client: NominatimAPI) -> None:
    """Тест обработки ситуации, когда страна не найдена."""
    mock_request.return_value = []
    assert nominatim_client.get_coordinates("UnknownLand") is None


@patch.object(NominatimAPI, "_make_request")
def test_get_bounding_box_success(mock_request: MagicMock, nominatim_client: NominatimAPI) -> None:
    """Тест получения ограничивающего прямоугольника."""
    mock_request.return_value = [{"boundingbox": ["50.0", "60.0", "30.0", "40.0"]}]
    result = nominatim_client.get_bounding_box("Russia")
    assert result == (30.0, 40.0, 50.0, 60.0)  # W, E, S, N


def test_nominatim_stub_methods(nominatim_client: NominatimAPI) -> None:
    """Тест методов-заглушек."""
    assert nominatim_client.get_aeroplanes("Russia") == []
    assert nominatim_client.get_all_states() == []
