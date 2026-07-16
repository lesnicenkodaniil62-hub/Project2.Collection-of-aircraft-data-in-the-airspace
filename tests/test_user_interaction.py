"""
Тесты консольного интерфейса с мокированием input() и внешних зависимостей.

Важно:
1. При выходе из программы (пункт "0") с несохранёнными данными
   (has_unsaved_changes=True) программа запрашивает подтверждение
   через input("...Выйти без сохранения? (y/n): ").
   Поэтому в side_effect всегда добавляется "y" после "0", если в сценарии
   были несохранённые данные.

2. Функция print_aeroplanes преобразует заголовок в верхний регистр
   через title.upper(). Поэтому при проверке вывода используем .lower()
   для регистронезависимого сравнения.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.models.aeroplane import Aeroplane
from src.utils.user_interaction import user_interaction


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch("builtins.input", side_effect=["0"])
def test_user_interaction_exit(
    mock_input: MagicMock, mock_nominatim: MagicMock, mock_opensky: MagicMock, mock_jsonsaver: MagicMock
) -> None:
    """Тест корректного завершения работы при выборе '0' без несохранённых данных."""
    mock_jsonsaver.return_value.count.return_value = 0
    user_interaction()
    mock_input.assert_called_with("\nВаш выбор: ")


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # Последовательность:
    # 1 — получить данные по стране
    # Spain — название страны
    # 0 — выход (с несохранёнными данными → нужен "y")
    # y — подтверждение выхода
    side_effect=["1", "Spain", "0", "y"],
)
def test_user_interaction_get_by_country(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест сценария получения данных по стране."""
    # Настраиваем моки API
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

    # Запускаем функцию
    user_interaction()

    # Проверяем вывод (регистронезависимо)
    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "координаты найдены" in output_lower
    assert "успешно создано 1 объектов" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # Последовательность:
    # 1 — получить данные
    # Spain — страна
    # 2 — показать топ N
    # 1 — число N (у нас 1 самолёт, значит N=1 корректно)
    # 0 — выход (с несохранёнными данными → нужен "y")
    # y — подтверждение выхода
    side_effect=["1", "Spain", "2", "1", "0", "y"],
)
def test_user_interaction_top_n(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест показа топ N самолётов по высоте."""
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

    # Регистронезависимая проверка (в выводе будет "ТОП 1 САМОЛЁТОВ ПО ВЫСОТЕ")
    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "топ 1 самолётов по высоте" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # Последовательность:
    # 1 — получить данные
    # Spain — страна
    # 3 — фильтр по стране
    # Spain — страна для фильтрации
    # 0 — выход (с несохранёнными данными → нужен "y")
    # y — подтверждение
    side_effect=["1", "Spain", "3", "Spain", "0", "y"],
)
def test_user_interaction_filter_by_country(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест фильтрации по стране."""
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

    # Регистронезависимая проверка (в выводе будет "САМОЛЁТЫ ИЗ СТРАН")
    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "самолёты из стран" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # Последовательность:
    # 1 — получить данные
    # Spain — страна
    # 4 — фильтр по диапазону высот
    # 4000-6000 — диапазон (5000 попадает в него)
    # 0 — выход (с несохранёнными данными → нужен "y")
    # y — подтверждение
    side_effect=["1", "Spain", "4", "4000-6000", "0", "y"],
)
def test_user_interaction_filter_by_altitude(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест фильтрации по диапазону высот."""
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

    # Регистронезависимая проверка (в выводе будет "САМОЛЁТЫ НА ВЫСОТЕ")
    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "самолёты на высоте" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # Последовательность:
    # 1 — получить данные
    # Spain — страна
    # 5 — показать все
    # 0 — выход (с несохранёнными данными → нужен "y")
    # y — подтверждение
    side_effect=["1", "Spain", "5", "0", "y"],
)
def test_user_interaction_show_all(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест показа всех загруженных самолётов."""
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

    # Регистронезависимая проверка (в выводе будет "ВСЕ ЗАГРУЖЕННЫЕ САМОЛЁТЫ")
    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "все загруженные самолёты" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # Последовательность:
    # 1 — получить данные
    # Spain — страна
    # 6 — сохранить в снапшот (после этого has_unsaved_changes=False)
    # 0 — выход (без несохранённых данных, подтверждение НЕ нужно)
    side_effect=["1", "Spain", "6", "0"],
)
def test_user_interaction_save_snapshot(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест сохранения в снапшот."""
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
    mock_jsonsaver.return_value.save_snapshot.return_value = Path("data/aeroplanes_20260716_143022.json")

    user_interaction()

    # Проверяем, что save_snapshot был вызван
    mock_jsonsaver.return_value.save_snapshot.assert_called_once()
    captured = capsys.readouterr()
    assert "снапшот" in captured.out.lower()


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # Последовательность:
    # 7 — загрузить из снапшота
    # 1 — выбрать первый снапшот из списка
    # 0 — выход (без несохранённых данных после загрузки)
    side_effect=["7", "1", "0"],
)
def test_user_interaction_load_snapshot(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест загрузки из снапшота."""
    mock_jsonsaver.return_value.list_snapshots.return_value = [Path("data/aeroplanes_20260716_143022.json")]
    mock_jsonsaver.return_value.get_all_aeroplanes.return_value = [
        Aeroplane(
            callsign="IBE123",
            country="Spain",
            velocity=200.0,
            altitude=5000.0,
        )
    ]
    mock_jsonsaver.return_value.count.return_value = 1

    user_interaction()

    # Проверяем, что load_snapshot был вызван
    mock_jsonsaver.return_value.load_snapshot.assert_called_once()
    captured = capsys.readouterr()
    assert "загружено" in captured.out.lower()
