"""
Тесты хранилища JSONSaver с изоляцией файловой системы через tmp_path.
"""

import json
from pathlib import Path
from typing import List

import pytest

from src.models.aeroplane import Aeroplane
from src.storage.json_saver import JSONSaver


@pytest.fixture
def json_saver(tmp_path: Path, aeroplane: Aeroplane) -> JSONSaver:
    """Фикстура инициализации JSONSaver во временной директории."""
    test_file = tmp_path / "test_aeroplanes.json"
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
