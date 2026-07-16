"""
Расширенные тесты клиента NominatimAPI для увеличения покрытия кода.

Важно: при использовании декоратора @patch.object вместе с фикстурами pytest,
параметры моков должны идти ПЕРВЫМИ в сигнатуре функции, а фикстуры — после них.
Иначе pytest передаст мок в параметр фикстуры, что приведёт к ошибкам.
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
def test_get_coordinates_malformed_response(mock_request: MagicMock, nominatim_client: NominatimAPI) -> None:
    """Тест обработки некорректного формата ответа."""
    mock_request.return_value = [{"invalid_key": "value"}]  # Нет lat/lon
    result = nominatim_client.get_coordinates("Russia")
    assert result is None


@patch.object(NominatimAPI, "_make_request")
def test_get_coordinates_invalid_lat_lon(mock_request: MagicMock, nominatim_client: NominatimAPI) -> None:
    """Тест обработки некорректных значений lat/lon."""
    mock_request.return_value = [{"lat": "invalid", "lon": "invalid"}]
    result = nominatim_client.get_coordinates("Russia")
    assert result is None


@patch.object(NominatimAPI, "_make_request")
def test_get_bounding_box_success(mock_request: MagicMock, nominatim_client: NominatimAPI) -> None:
    """Тест получения ограничивающего прямоугольника."""
    mock_request.return_value = [{"boundingbox": ["50.0", "60.0", "30.0", "40.0"]}]
    result = nominatim_client.get_bounding_box("Russia")
    assert result == (30.0, 40.0, 50.0, 60.0)  # W, E, S, N


@patch.object(NominatimAPI, "_make_request")
def test_get_bounding_box_invalid_input(
    mock_request: MagicMock, nominatim_client: NominatimAPI  # ← ДОБАВЛЕН параметр для мока
) -> None:
    """
    Тест обработки некорректного ввода для bounding box.

    Важно: декоратор @patch.object создаёт мок, который должен быть принят
    первым параметром функции (mock_request). Без этого параметра pytest
    передаст мок в nominatim_client, что сломает тест.
    """
    # Мок не будет вызван, так как метод вернёт None до обращения к API
    # из-за проверки: if not country_name or not isinstance(country_name, str)
    result = nominatim_client.get_bounding_box("")
    assert result is None

    # Проверяем, что _make_request действительно не был вызван
    mock_request.assert_not_called()


@pytest.mark.parametrize("input_val", ["", None, 123])  # type: ignore[arg-type]
@patch.object(NominatimAPI, "_make_request")
def test_get_bounding_box_invalid_input_parametrized(
    mock_request: MagicMock, nominatim_client: NominatimAPI, input_val: Any
) -> None:
    """Параметризованный тест обработки некорректного ввода для bounding box."""
    result = nominatim_client.get_bounding_box(input_val)
    assert result is None
    mock_request.assert_not_called()


@patch.object(NominatimAPI, "_make_request")
def test_get_bounding_box_empty_response(mock_request: MagicMock, nominatim_client: NominatimAPI) -> None:
    """Тест обработки пустого ответа для bounding box."""
    mock_request.return_value = []
    result = nominatim_client.get_bounding_box("UnknownLand")
    assert result is None


@patch.object(NominatimAPI, "_make_request")
def test_get_bounding_box_malformed_response(mock_request: MagicMock, nominatim_client: NominatimAPI) -> None:
    """Тест обработки некорректного формата bounding box."""
    mock_request.return_value = [{"boundingbox": ["invalid"]}]
    result = nominatim_client.get_bounding_box("Russia")
    assert result is None


def test_nominatim_stub_methods(nominatim_client: NominatimAPI) -> None:
    """Тест методов-заглушек."""
    assert nominatim_client.get_aeroplanes("Russia") == []
    assert nominatim_client.get_all_states() == []


@patch.object(NominatimAPI, "_make_request")
def test_get_coordinates_with_display_name(
    mock_request: MagicMock, nominatim_client: NominatimAPI, caplog: pytest.LogCaptureFixture
) -> None:
    """Тест логирования с display_name."""
    mock_request.return_value = [{"lat": "55.75", "lon": "37.61", "display_name": "Moscow, Russia"}]
    with caplog.at_level("INFO"):
        result = nominatim_client.get_coordinates("Russia")
    assert result == (55.75, 37.61)
    assert "Moscow, Russia" in caplog.text
