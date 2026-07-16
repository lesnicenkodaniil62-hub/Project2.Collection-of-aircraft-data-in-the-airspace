"""
Тесты клиента OpenSkyAPI с использованием Mock и Parametrize.
"""

from typing import Any, List
from unittest.mock import MagicMock, patch

import pytest

from src.api.opensky import OpenSkyAPI


@pytest.fixture
def opensky_client() -> OpenSkyAPI:
    """Фикстура клиента OpenSky с аутентификацией."""
    return OpenSkyAPI(username="user", password="pass", timeout=10)


@pytest.fixture
def opensky_anonymous_client() -> OpenSkyAPI:
    """Фикстура анонимного клиента OpenSky."""
    return OpenSkyAPI()


def test_opensky_init_with_auth(opensky_client: OpenSkyAPI) -> None:
    """Проверка установки учётных данных."""
    assert opensky_client.session.auth == ("user", "pass")


def test_opensky_init_without_auth(opensky_anonymous_client: OpenSkyAPI) -> None:
    """Проверка отсутствия учётных данных."""
    assert opensky_anonymous_client.session.auth is None


def test_opensky_get_coordinates_stub(opensky_client: OpenSkyAPI) -> None:
    """Проверка заглушки геокодирования."""
    assert opensky_client.get_coordinates("Russia") is None


@patch.object(OpenSkyAPI, "_make_request")
def test_get_all_states_success(
    mock_request: MagicMock, opensky_client: OpenSkyAPI, mock_raw_opensky_state: List[List[Any]]
) -> None:
    """Тест получения и парсинга всех состояний."""
    mock_request.return_value = {"states": mock_raw_opensky_state}
    result = opensky_client.get_all_states()

    assert len(result) == 2
    assert result[0]["icao24"] == "abc123"


@patch.object(OpenSkyAPI, "_make_request")
def test_get_aeroplanes_success(
    mock_request: MagicMock, opensky_client: OpenSkyAPI, mock_raw_opensky_state: List[List[Any]]
) -> None:
    """Тест получения состояний с фильтрацией."""
    mock_request.return_value = {"states": mock_raw_opensky_state}
    result = opensky_client.get_aeroplanes("Russia")
    assert len(result) == 2


def test_parse_states_empty(opensky_client: OpenSkyAPI) -> None:
    """Тест парсинга пустых данных."""
    assert opensky_client._parse_states(None) == []
    assert opensky_client._parse_states([]) == []


def test_parse_states_malformed(opensky_client: OpenSkyAPI) -> None:
    """Тест устойчивости парсера к повреждённым данным."""
    result = opensky_client._parse_states([["short_list"]])
    assert result == []
