"""
Расширенные тесты консольного интерфейса для увеличения покрытия кода.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.utils.user_interaction import user_interaction


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch("builtins.input", side_effect=["99", "0"])  # Некорректный выбор
def test_user_interaction_invalid_choice(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки некорректного выбора в меню."""
    mock_jsonsaver.return_value.count.return_value = 0
    user_interaction()

    captured = capsys.readouterr()
    assert "некорректный выбор" in captured.out.lower()


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch("builtins.input", side_effect=["1", "", "0"])  # Пустая страна
def test_user_interaction_empty_country(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки пустого названия страны."""
    mock_jsonsaver.return_value.count.return_value = 0
    user_interaction()

    captured = capsys.readouterr()
    assert "не может быть пустым" in captured.out.lower()


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch("builtins.input", side_effect=["1", "Spain", "2", "abc", "0", "y"])  # Некорректное число N
def test_user_interaction_invalid_n(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки некорректного числа N для топ-N."""
    mock_nominatim.return_value.get_coordinates.return_value = (40.0, -3.0)
    mock_opensky.return_value.get_aeroplanes.return_value = [
        {
            "callsign": "IBE123",
            "origin_country": "Spain",
            "velocity": 200.0,
            "baro_altitude": 5000.0,
        }
    ]
    mock_jsonsaver.return_value.count.return_value = 0

    user_interaction()

    captured = capsys.readouterr()
    assert "некорректное число" in captured.out.lower()


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch("builtins.input", side_effect=["1", "Spain", "4", "invalid", "0", "y"])  # Некорректный диапазон
def test_user_interaction_invalid_altitude_range(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки некорректного диапазона высот."""
    mock_nominatim.return_value.get_coordinates.return_value = (40.0, -3.0)
    mock_opensky.return_value.get_aeroplanes.return_value = [
        {
            "callsign": "IBE123",
            "origin_country": "Spain",
            "velocity": 200.0,
            "baro_altitude": 5000.0,
        }
    ]
    mock_jsonsaver.return_value.count.return_value = 0

    user_interaction()

    captured = capsys.readouterr()
    assert "некорректный формат" in captured.out.lower()


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch("builtins.input", side_effect=["2", "0"])  # Топ-N без данных
def test_user_interaction_top_n_no_data(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест показа топ-N при отсутствии данных."""
    mock_jsonsaver.return_value.count.return_value = 0
    user_interaction()

    captured = capsys.readouterr()
    assert "нет загруженных данных" in captured.out.lower()


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch("builtins.input", side_effect=["6", "0"])  # Сохранение без данных
def test_user_interaction_save_no_data(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест сохранения при отсутствии данных."""
    mock_jsonsaver.return_value.count.return_value = 0
    user_interaction()

    captured = capsys.readouterr()
    assert "нет данных для сохранения" in captured.out.lower()


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch("builtins.input", side_effect=["7", "0"])  # Загрузка без снапшотов
def test_user_interaction_load_no_snapshots(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест загрузки при отсутствии снапшотов."""
    mock_jsonsaver.return_value.list_snapshots.return_value = []
    mock_jsonsaver.return_value.count.return_value = 0
    user_interaction()

    captured = capsys.readouterr()
    assert "нет доступных снапшотов" in captured.out.lower()
