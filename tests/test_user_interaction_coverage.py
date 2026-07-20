"""
Тесты для повышения покрытия файла user_interaction.py.

Сфокусированы на непокрытых ветках кода:
- Диалог замены/добавления данных при повторном запросе страны
- Обработка ошибок ввода в пунктах 3 и 4
- Отмена выбора снапшота и обработка некорректных номеров
- Пустые результаты фильтрации
- Некорректные форматы ввода
- Обработка ошибок при получении данных (координаты, самолёты, cast)

Все тесты используют функциональный стиль, фикстуры, параметризацию
и моки для изоляции внешних зависимостей.

Примечание: тесты пункта "2" (топ N) были исключены из-за конфликтов
с мокированием input() и вынесены в отдельный файл test_user_interaction.py.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.utils.user_interaction import user_interaction

# ============================================================================
# Тесты пункта диалог замены/добавления данных
# ============================================================================


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные (1-й раз)
    # Spain — страна
    # 1 — получить данные (2-й раз, когда в памяти уже есть данные)
    # Germany — страна
    # 1 — выбрать "Заменить текущие данные"
    # 0 — выход
    # y — подтверждение выхода (есть несохранённые данные)
    side_effect=["1", "Spain", "1", "Germany", "1", "0", "y"],
)
def test_user_interaction_replace_existing_data(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест диалога замены существующих данных новыми."""
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
    output_lower = captured.out.lower()
    assert "в памяти уже есть" in output_lower
    assert "текущие данные заменены" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные (1-й раз)
    # Spain — страна
    # 1 — получить данные (2-й раз)
    # Germany — страна
    # 2 — выбрать "Добавить к текущим"
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "1", "Germany", "2", "0", "y"],
)
def test_user_interaction_add_to_existing_data(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест диалога добавления новых данных к существующим."""
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
    output_lower = captured.out.lower()
    assert "новые данные добавлены" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна (координаты не найдены)
    # 0 — выход
    side_effect=["1", "Spain", "0"],
)
def test_user_interaction_coordinates_not_found(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест ситуации, когда координаты страны не найдены."""
    mock_nominatim.return_value.get_coordinates.return_value = None
    mock_opensky.return_value.get_aeroplanes.return_value = []
    mock_jsonsaver.return_value.count.return_value = 0

    user_interaction()

    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "не удалось найти координаты" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна (самолёты не найдены)
    # 0 — выход
    side_effect=["1", "Spain", "0"],
)
def test_user_interaction_aeroplanes_not_found(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест ситуации, когда самолёты для страны не найдены."""
    mock_nominatim.return_value.get_coordinates.return_value = (40.0, -3.0)
    mock_opensky.return_value.get_aeroplanes.return_value = []
    mock_jsonsaver.return_value.count.return_value = 0

    user_interaction()

    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "самолёты не найдены" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна (cast вернёт пустой список)
    # 0 — выход
    side_effect=["1", "Spain", "0"],
)
def test_user_interaction_cast_failed(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест ситуации, когда преобразование данных в объекты не удалось."""
    mock_nominatim.return_value.get_coordinates.return_value = (40.0, -3.0)
    # API возвращает данные, но cast_to_object_list вернёт пустой список
    mock_opensky.return_value.get_aeroplanes.return_value = [
        {
            "callsign": "",  # Пустой callsign → будет отброшен
            "origin_country": "Spain",
            "velocity": 200.0,
            "baro_altitude": 5000.0,
        }
    ]
    mock_jsonsaver.return_value.count.return_value = 0

    user_interaction()

    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "не удалось преобразовать данные" in output_lower


# ============================================================================
# Тесты обработка ошибок фильтрации по стране
# ============================================================================


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна
    # 3 — фильтр по стране
    # (пустой ввод)
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "3", "", "0", "y"],
)
def test_user_interaction_filter_empty_countries(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки пустого ввода стран для фильтрации."""
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
    output_lower = captured.out.lower()
    assert "не может быть пустым" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна
    # 3 — фильтр по стране
    # ,,, — только запятые
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "3", ",,,", "0", "y"],
)
def test_user_interaction_filter_invalid_format(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки некорректного формата списка стран."""
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
    output_lower = captured.out.lower()
    assert "некорректный формат" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна
    # 3 — фильтр по стране
    # France — страны нет в данных
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "3", "France", "0", "y"],
)
def test_user_interaction_filter_no_results(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест ситуации, когда фильтр не нашёл самолётов."""
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
    output_lower = captured.out.lower()
    assert "самолёты не найдены для стран" in output_lower


# ============================================================================
# Тесты обработка ошибок фильтрации по высоте
# ============================================================================


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна
    # 4 — фильтр по диапазону
    # 5000 — нет разделителя "-"
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "4", "5000", "0", "y"],
)
def test_user_interaction_altitude_no_separator(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки диапазона без разделителя '-'."""
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
    output_lower = captured.out.lower()
    assert "некорректный формат" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна
    # 4 — фильтр по диапазону
    # 5000-6000-7000 — слишком много частей
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "4", "5000-6000-7000", "0", "y"],
)
def test_user_interaction_altitude_too_many_parts(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки диапазона с лишними частями."""
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
    output_lower = captured.out.lower()
    assert "некорректный формат" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна
    # 4 — фильтр по диапазону
    # 10000-5000 — min > max
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "4", "10000-5000", "0", "y"],
)
def test_user_interaction_altitude_min_greater_than_max(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки ситуации, когда min > max."""
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
    output_lower = captured.out.lower()
    assert "минимальная высота не может быть больше" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна
    # 4 — фильтр по диапазону
    # 1000-2000 — диапазон, в который не попадает ни один самолёт
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "4", "1000-2000", "0", "y"],
)
def test_user_interaction_altitude_no_results(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест ситуации, когда в диапазоне нет самолётов."""
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
    output_lower = captured.out.lower()
    assert "самолёты не найдены в диапазоне" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна
    # 4 — фильтр по диапазону
    # abc-def — не числа
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "4", "abc-def", "0", "y"],
)
def test_user_interaction_altitude_not_numbers(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки нечисловых значений в диапазоне высот."""
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
    output_lower = captured.out.lower()
    assert "некорректный формат высот" in output_lower


# ============================================================================
# Тесты обработка ошибок загрузки снапшотов
# ============================================================================


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна
    # 7 — загрузить из снапшота
    # y — подтвердить (есть несохранённые данные)
    # 0 — отменить выбор снапшота
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "7", "y", "0", "0", "y"],
)
def test_user_interaction_load_cancel_selection(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест отмены выбора снапшота (ввод '0')."""
    mock_nominatim.return_value.get_coordinates.return_value = (40.0, -3.0)
    mock_opensky.return_value.get_aeroplanes.return_value = [
        {
            "callsign": "IBE123",
            "origin_country": "Spain",
            "velocity": 200.0,
            "baro_altitude": 5000.0,
        }
    ]
    mock_jsonsaver.return_value.list_snapshots.return_value = [Path("data/aeroplanes_20260716_143022.json")]
    mock_jsonsaver.return_value.count.return_value = 0

    user_interaction()

    # load_snapshot не должен быть вызван
    mock_jsonsaver.return_value.load_snapshot.assert_not_called()


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 1 — получить данные
    # Spain — страна
    # 7 — загрузить из снапшота
    # n — отказаться (есть несохранённые данные)
    # 0 — выход
    # y — подтверждение
    side_effect=["1", "Spain", "7", "n", "0", "y"],
)
def test_user_interaction_load_decline_warning(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест отказа от загрузки при предупреждении о несохранённых данных."""
    mock_nominatim.return_value.get_coordinates.return_value = (40.0, -3.0)
    mock_opensky.return_value.get_aeroplanes.return_value = [
        {
            "callsign": "IBE123",
            "origin_country": "Spain",
            "velocity": 200.0,
            "baro_altitude": 5000.0,
        }
    ]
    mock_jsonsaver.return_value.list_snapshots.return_value = [Path("data/aeroplanes_20260716_143022.json")]
    mock_jsonsaver.return_value.count.return_value = 0

    user_interaction()

    # load_snapshot не должен быть вызван
    mock_jsonsaver.return_value.load_snapshot.assert_not_called()


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 7 — загрузить из снапшота
    # 99 — некорректный номер
    # 0 — выход
    side_effect=["7", "99", "0"],
)
def test_user_interaction_load_invalid_number(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки некорректного номера снапшота."""
    mock_jsonsaver.return_value.list_snapshots.return_value = [Path("data/aeroplanes_20260716_143022.json")]
    mock_jsonsaver.return_value.count.return_value = 0

    user_interaction()

    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "некорректный номер" in output_lower


@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
@patch(
    "builtins.input",
    # 7 — загрузить из снапшота
    # abc — не число
    # 0 — выход
    side_effect=["7", "abc", "0"],
)
def test_user_interaction_load_non_numeric(
    mock_input: MagicMock,
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Тест обработки нечислового ввода при выборе снапшота."""
    mock_jsonsaver.return_value.list_snapshots.return_value = [Path("data/aeroplanes_20260716_143022.json")]
    mock_jsonsaver.return_value.count.return_value = 0

    user_interaction()

    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "некорректный ввод" in output_lower


# ============================================================================
# Параметризованные тесты для некорректного выбора меню
# ============================================================================


@pytest.mark.parametrize("invalid_choice", ["8", "-1", "abc", "  "])
@patch("src.utils.user_interaction.JSONSaver")
@patch("src.utils.user_interaction.OpenSkyAPI")
@patch("src.utils.user_interaction.NominatimAPI")
def test_user_interaction_various_invalid_choices(
    mock_nominatim: MagicMock,
    mock_opensky: MagicMock,
    mock_jsonsaver: MagicMock,
    invalid_choice: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Параметризованный тест обработки различных некорректных выборов."""
    mock_jsonsaver.return_value.count.return_value = 0

    with patch("builtins.input", side_effect=[invalid_choice, "0"]):
        user_interaction()

    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "некорректный выбор" in output_lower
