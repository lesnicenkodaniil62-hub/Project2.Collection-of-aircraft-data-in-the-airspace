"""
Тесты абстрактного базового класса BaseAPI.
Используется минимальная конкретная реализация для тестирования защищённых методов.
"""

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.api.base import BaseAPI


class _ConcreteAPIForTest(BaseAPI):
    """Минимальная реализация для тестирования BaseAPI."""

    def get_coordinates(self, country_name: str) -> Optional[tuple[float, float]]:
        return self._make_request("coords", {"q": country_name})  # type: ignore[return-value]

    def get_aeroplanes(self, country_name: str) -> List[Dict[str, Any]]:
        return self._make_request("planes", {"country": country_name}) or []  # type: ignore[return-value]

    def get_all_states(self) -> List[Dict[str, Any]]:
        return self._make_request("states") or []  # type: ignore[return-value]


@pytest.fixture
def api_client() -> _ConcreteAPIForTest:
    """Фикстура тестового API-клиента."""
    return _ConcreteAPIForTest(base_url="https://api.test.com", timeout=5)


@patch("requests.Session.request")
def test_make_request_success(mock_request: MagicMock, api_client: _ConcreteAPIForTest) -> None:
    """Тест успешного HTTP-запроса."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    mock_request.return_value = mock_response

    result = api_client._make_request("test", {"key": "value"}, "POST")

    assert result == {"status": "ok"}
    mock_request.assert_called_once_with(
        method="POST", url="https://api.test.com/test", params={"key": "value"}, timeout=5
    )


@pytest.mark.parametrize(
    "exception",
    [
        requests.exceptions.Timeout,
        requests.exceptions.HTTPError("404"),
        requests.exceptions.RequestException("Network"),
    ],
)
@patch("requests.Session.request")
def test_make_request_errors(mock_request: MagicMock, api_client: _ConcreteAPIForTest, exception: Exception) -> None:
    """Тест обработки различных сетевых исключений."""
    mock_request.side_effect = exception
    result = api_client._make_request("test")
    assert result is None


@patch("requests.Session.request")
def test_make_request_json_error(mock_request: MagicMock, api_client: _ConcreteAPIForTest) -> None:
    """Тест обработки ошибки парсинга JSON."""
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_request.return_value = mock_response

    result = api_client._make_request("test")
    assert result is None


def test_api_repr(api_client: _ConcreteAPIForTest) -> None:
    """Тест строкового представления."""
    assert repr(api_client) == "<_ConcreteAPIForTest(base_url=https://api.test.com)>"
