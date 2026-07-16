"""
Тесты хранилища JSONSaver с изоляцией файловой системы через tmp_path.
Включая тесты для новой функциональности снапшотов.
"""

import json
import time
from pathlib import Path
from typing import List

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


def test_add_and_exists(json_saver: JSONSaver, aeroplane: Aeroplane) -> None:
    """Тест добавления и проверки существования."""
    assert not json_saver.exists("AFL123")
    json_saver.add_aeroplane(aeroplane)
    assert json_saver.exists("AFL123")
    assert json_saver.count() == 1


def test_add_aeroplanes_with_duplicates(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест пакетного добавления и обработки дубликатов."""
    json_saver.add_aeroplanes(aeroplane_list)
    assert json_saver.count() == 4

    json_saver.add_aeroplane(aeroplane_list[0])
    assert json_saver.count() == 4


def test_get_aeroplanes_with_criteria(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест фильтрации внутри хранилища."""
    json_saver.add_aeroplanes(aeroplane_list)

    result = json_saver.get_aeroplanes(country="Russia")
    assert len(result) == 2

    result_alt = json_saver.get_aeroplanes(min_altitude=6000.0, max_altitude=10500.0)
    assert len(result_alt) == 1
    assert result_alt[0].callsign == "DLH400"


def test_delete_aeroplane(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест удаления по позывному."""
    json_saver.add_aeroplanes(aeroplane_list)
    assert json_saver.delete_aeroplane("AFL100") is True
    assert json_saver.count() == 3
    assert json_saver.delete_aeroplane("NONEXISTENT") is False


def test_delete_aeroplanes_by_criteria(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест массового удаления по критериям."""
    json_saver.add_aeroplanes(aeroplane_list)
    deleted_count = json_saver.delete_aeroplanes(on_ground=True)
    assert deleted_count == 1
    assert json_saver.count() == 3


def test_clear(json_saver: JSONSaver, aeroplane: Aeroplane) -> None:
    """Тест полной очистки хранилища."""
    json_saver.add_aeroplane(aeroplane)
    json_saver.clear()
    assert json_saver.count() == 0

    with open(json_saver.filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["aeroplanes"] == []


def test_load_corrupted_file(tmp_path: Path) -> None:
    """Тест устойчивости к повреждённому JSON-файлу."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{ not valid json }")

    saver = JSONSaver()
    saver.filepath = bad_file
    saver._load_from_file()

    assert saver._data == {"aeroplanes": []}


def test_save_snapshot(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест сохранения снапшота."""
    snapshot_path = json_saver.save_snapshot(aeroplane_list)

    assert snapshot_path.exists()
    assert snapshot_path.name.startswith("aeroplanes_")
    assert snapshot_path.name.endswith(".json")
    assert snapshot_path.parent == json_saver.filepath.parent

    # Проверяем содержимое снапшота
    with open(snapshot_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert len(data["aeroplanes"]) == len(aeroplane_list)


def test_list_snapshots(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест получения списка снапшотов."""
    # Создаём несколько снапшотов с задержкой >1 секунды,
    # чтобы timestamp (точность до секунды) гарантированно отличался
    json_saver.save_snapshot(aeroplane_list)
    time.sleep(1.1)  # Было 0.01, стало 1.1
    json_saver.save_snapshot(aeroplane_list[:2])

    snapshots = json_saver.list_snapshots()
    assert len(snapshots) == 2
    # Сортировка по убыванию (новые первые)
    assert snapshots[0].name > snapshots[1].name


def test_load_snapshot(json_saver: JSONSaver, aeroplane_list: List[Aeroplane]) -> None:
    """Тест загрузки снапшота в рабочий файл."""
    snapshot_path = json_saver.save_snapshot(aeroplane_list)

    # Очищаем json_saver
    json_saver.clear()
    assert json_saver.count() == 0

    # Загружаем снапшот
    json_saver.load_snapshot(snapshot_path)
    assert json_saver.count() == len(aeroplane_list)

    # Проверяем, что данные скопировались в рабочий файл
    assert json_saver.filepath.exists()
    with open(json_saver.filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert len(data["aeroplanes"]) == len(aeroplane_list)


def test_load_snapshot_not_found(json_saver: JSONSaver, tmp_path: Path) -> None:
    """Тест загрузки несуществующего снапшота."""
    fake_path = tmp_path / "nonexistent.json"
    with pytest.raises(FileNotFoundError):
        json_saver.load_snapshot(fake_path)
