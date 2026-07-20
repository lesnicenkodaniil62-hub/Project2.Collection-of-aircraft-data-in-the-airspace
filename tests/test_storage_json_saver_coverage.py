"""
Тесты для повышения покрытия файла json_saver.py.

Сфокусированы на непокрытых ветках кода:
- Обработка IOError при сохранении снапшотов
- Все ветки критериев фильтрации (min_velocity, max_velocity, callsign)
- Обработка ошибок при десериализации записей
- Обновление существующих записей
- Обработка ошибок при загрузке снапшотов

Все тесты используют функциональный стиль, фикстуры и tmp_path для
изоляции файловой системы.
"""

import json
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from src.models.aeroplane import Aeroplane
from src.storage.json_saver import JSONSaver


@pytest.fixture
def json_saver(tmp_path: Path, aeroplane: Aeroplane) -> JSONSaver:
    """Фикстура инициализации JSONSaver во временной директории."""
    test_file = tmp_path / "aeroplanes.json"
    saver = JSONSaver()
    saver.filepath = test_file
    saver._save_to_file()
    return saver


# ============================================================================
# Тесты обработки ошибок ввода-вывода
# ============================================================================


def test_save_snapshot_io_error(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """
    Тест обработки IOError при сохранении снапшота.

    Используется patch("builtins.open") для прямого вызова IOError
    при попытке открытия файла для записи. Это надёжнее, чем создание
    директории с тем же именем, так как не зависит от timestamp.
    """
    with patch("builtins.open", side_effect=IOError("Permission denied")):
        with pytest.raises(IOError):
            json_saver.save_snapshot(aeroplane_list)


def test_save_to_file_io_error(json_saver: JSONSaver) -> None:
    """
    Тест обработки IOError при сохранении в рабочий файл.

    Используется patch("builtins.open") для прямого вызова IOError
    при попытке открытия файла для записи.
    """
    with patch("builtins.open", side_effect=IOError("Permission denied")):
        with pytest.raises(IOError):
            json_saver._save_to_file()


def test_load_snapshot_io_error(json_saver: JSONSaver, tmp_path: Path) -> None:
    """
    Тест обработки IOError при загрузке снапшота.

    Используется patch("builtins.open") для прямого вызова IOError
    при попытке открытия файла для чтения.
    """
    bad_snapshot = tmp_path / "bad_snapshot.json"
    bad_snapshot.write_text('{"aeroplanes": []}')

    with patch("builtins.open", side_effect=IOError("Permission denied")):
        with pytest.raises(IOError):
            json_saver.load_snapshot(bad_snapshot)


# ============================================================================
# Тесты всех веток критериев фильтрации
# ============================================================================


def test_matches_criteria_min_velocity(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест фильтрации по min_velocity."""
    json_saver.add_aeroplanes(aeroplane_list)

    result = json_saver.get_aeroplanes(min_velocity=240.0)
    assert len(result) == 2  # DLH400 (250.0) и SBI777 (300.0)


def test_matches_criteria_max_velocity(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест фильтрации по max_velocity."""
    json_saver.add_aeroplanes(aeroplane_list)

    result = json_saver.get_aeroplanes(max_velocity=200.0)
    assert len(result) == 2  # AFL100 (200.0) и BAW500 (150.0)


def test_matches_criteria_callsign(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест фильтрации по callsign."""
    json_saver.add_aeroplanes(aeroplane_list)

    result = json_saver.get_aeroplanes(callsign="AFL100")
    assert len(result) == 1
    assert result[0].callsign == "AFL100"


def test_matches_criteria_combined(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест фильтрации по нескольким критериям одновременно."""
    json_saver.add_aeroplanes(aeroplane_list)

    result = json_saver.get_aeroplanes(country="Russia", min_velocity=250.0, max_altitude=12000.0)
    assert len(result) == 1  # Только SBI777
    assert result[0].callsign == "SBI777"


# ============================================================================
# Тесты обработки ошибок при десериализации
# ============================================================================


def test_get_aeroplanes_handles_corrupted_records(json_saver: JSONSaver, tmp_path: Path) -> None:
    """Тест обработки повреждённых записей при получении самолётов."""
    # Записываем данные с одной некорректной записью
    corrupted_data = {
        "aeroplanes": [
            {
                "callsign": "VALID1",
                "country": "USA",
                "velocity": 200.0,
                "altitude": 10000.0,
            },
            {
                # Отсутствует обязательное поле "country"
                "callsign": "INVALID",
                "velocity": 200.0,
                "altitude": 10000.0,
            },
            {
                "callsign": "VALID2",
                "country": "Germany",
                "velocity": 250.0,
                "altitude": 11000.0,
            },
        ]
    }

    with open(json_saver.filepath, "w", encoding="utf-8") as f:
        json.dump(corrupted_data, f)

    json_saver._load_from_file()

    # Должны вернуться только валидные записи
    result = json_saver.get_all_aeroplanes()
    assert len(result) == 2
    callsigns = {p.callsign for p in result}
    assert callsigns == {"VALID1", "VALID2"}


def test_get_aeroplanes_with_criteria_handles_corrupted(json_saver: JSONSaver) -> None:
    """Тест обработки повреждённых записей при фильтрации."""
    corrupted_data = {
        "aeroplanes": [
            {
                "callsign": "VALID1",
                "country": "USA",
                "velocity": 200.0,
                "altitude": 10000.0,
            },
            {
                # Некорректный тип velocity
                "callsign": "INVALID",
                "country": "USA",
                "velocity": "fast",
                "altitude": 10000.0,
            },
        ]
    }

    with open(json_saver.filepath, "w", encoding="utf-8") as f:
        json.dump(corrupted_data, f)

    json_saver._load_from_file()

    result = json_saver.get_aeroplanes(country="USA")
    assert len(result) == 1
    assert result[0].callsign == "VALID1"


# ============================================================================
# Тесты обновления существующих записей
# ============================================================================


def test_add_aeroplane_updates_existing(json_saver: JSONSaver, aeroplane: Aeroplane) -> None:
    """Тест обновления существующего самолёта."""
    json_saver.add_aeroplane(aeroplane)
    assert json_saver.count() == 1

    # Обновляем данные
    updated = Aeroplane(callsign="AFL123", country="Russia", velocity=300.0, altitude=12000.0)  # Изменённая скорость
    json_saver.add_aeroplane(updated)
    assert json_saver.count() == 1  # Количество не изменилось

    # Проверяем, что данные обновились
    planes = json_saver.get_all_aeroplanes()
    assert len(planes) == 1
    assert planes[0].velocity == 300.0
    assert planes[0].altitude == 12000.0


def test_add_aeroplanes_skips_duplicates(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест пропуска дубликатов при пакетном добавлении."""
    json_saver.add_aeroplanes(aeroplane_list)
    assert json_saver.count() == 4

    # Пытаемся добавить те же самые самолёты
    json_saver.add_aeroplanes(aeroplane_list)
    assert json_saver.count() == 4  # Количество не изменилось


# ============================================================================
# Тесты удаления с обработкой ошибок
# ============================================================================


def test_delete_aeroplanes_no_matches(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест удаления, когда нет совпадений по критериям."""
    json_saver.add_aeroplanes(aeroplane_list)

    deleted_count = json_saver.delete_aeroplanes(country="France")
    assert deleted_count == 0
    assert json_saver.count() == 4


def test_delete_aeroplanes_handles_corrupted(json_saver: JSONSaver) -> None:
    """Тест удаления с обработкой повреждённых записей."""
    corrupted_data = {
        "aeroplanes": [
            {
                "callsign": "VALID1",
                "country": "USA",
                "velocity": 200.0,
                "altitude": 10000.0,
                "on_ground": True,
            },
            {
                # Отсутствует обязательное поле
                "callsign": "INVALID",
                "velocity": 200.0,
                "altitude": 10000.0,
            },
            {
                "callsign": "VALID2",
                "country": "Germany",
                "velocity": 250.0,
                "altitude": 11000.0,
                "on_ground": True,
            },
        ]
    }

    with open(json_saver.filepath, "w", encoding="utf-8") as f:
        json.dump(corrupted_data, f)

    json_saver._load_from_file()

    # Удаляем самолёты на земле
    deleted_count = json_saver.delete_aeroplanes(on_ground=True)
    assert deleted_count == 2  # VALID1 и VALID2
    assert json_saver.count() == 1  # Осталась только повреждённая запись


# ============================================================================
# Тесты загрузки файлов с различными форматами
# ============================================================================


def test_load_file_with_wrong_key(json_saver: JSONSaver, tmp_path: Path) -> None:
    """Тест загрузки файла с неправильным ключом верхнего уровня."""
    wrong_file = tmp_path / "wrong.json"
    wrong_file.write_text('{"wrong_key": []}')

    json_saver.filepath = wrong_file
    json_saver._load_from_file()

    assert json_saver._data == {"aeroplanes": []}


def test_load_file_with_non_dict(json_saver: JSONSaver, tmp_path: Path) -> None:
    """Тест загрузки файла, содержащего не словарь."""
    list_file = tmp_path / "list.json"
    list_file.write_text("[1, 2, 3]")

    json_saver.filepath = list_file
    json_saver._load_from_file()

    assert json_saver._data == {"aeroplanes": []}


def test_load_snapshot_with_wrong_key(json_saver: JSONSaver, tmp_path: Path) -> None:
    """Тест загрузки снапшота с неправильным ключом."""
    bad_snapshot = tmp_path / "bad_snapshot.json"
    bad_snapshot.write_text('{"wrong_key": []}')

    json_saver.load_snapshot(bad_snapshot)
    assert json_saver.count() == 0


def test_load_snapshot_with_non_dict(json_saver: JSONSaver, tmp_path: Path) -> None:
    """Тест загрузки снапшота, содержащего не словарь."""
    list_snapshot = tmp_path / "list_snapshot.json"
    list_snapshot.write_text("[1, 2, 3]")

    json_saver.load_snapshot(list_snapshot)
    assert json_saver.count() == 0


# ============================================================================
# Тесты логирования и пограничных случаев
# ============================================================================


def test_delete_aeroplane_not_found(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест удаления несуществующего самолёта."""
    json_saver.add_aeroplanes(aeroplane_list)

    result = json_saver.delete_aeroplane("NONEXISTENT")
    assert result is False
    assert json_saver.count() == 4


def test_exists_empty_storage(json_saver: JSONSaver) -> None:
    """Тест проверки существования в пустом хранилище."""
    assert json_saver.exists("AFL123") is False


def test_count_empty_storage(json_saver: JSONSaver) -> None:
    """Тест подсчёта в пустом хранилище."""
    assert json_saver.count() == 0


def test_clear_empty_storage(json_saver: JSONSaver) -> None:
    """Тест очистки пустого хранилища."""
    json_saver.clear()
    assert json_saver.count() == 0

    with open(json_saver.filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == {"aeroplanes": []}
