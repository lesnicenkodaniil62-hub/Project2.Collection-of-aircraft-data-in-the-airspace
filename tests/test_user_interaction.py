"""
Тесты консольного интерфейса с мокированием input() и внешних зависимостей.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.utils.user_interaction import user_interaction


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch("builtins.input", side_effect=["0"])
def test_user_interaction_exit(
    mock_input: MagicMock, mock_nominatim: MagicMock, mock_opensky: MagicMock, mock_jsonsaver: MagicMock
) -> None:
    """Тест корректного завершения работы при выборе '0'."""
    mock_jsonsaver.return_value.count.return_value = 0
    user_interaction()
    mock_input.assert_called_with("\nВаш выбор: ")


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch("builtins.input", side_effect=["1", "Spain", "0"])
def test_user_interaction_get_by_country(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест сценария получения данных по стране."""
    mock_nominatim.return_value.get_coordinates.return_value = (40.0, -3.0)
    mock_opensky.return_value.get_aeroplanes.return_value = [
        {"callsign": "IBE123", "origin_country": "Spain", "velocity": 200.0, "baro_altitude": 5000.0}
    ]
    mock_jsonsaver.return_value.count.return_value = 1

    user_interaction()

    captured = capsys.readouterr()
    assert "Координаты найдены" in captured.out
    assert "Успешно создано 1 объектов" in captured.out
