"""
Тесты утилит обработки данных. Функциональный стиль.
"""

from typing import Any, List

import pytest

from src.models.aeroplane import Aeroplane
from src.utils.data_processing import (filter_aeroplanes, get_aeroplanes_by_altitude_range, get_top_aeroplanes,
                                       print_aeroplanes, sort_aeroplanes)


@pytest.mark.parametrize(
    "filter_kwargs, expected_count",
    [
        ({"countries": ["Russia"]}, 2),
        ({"countries": ["Germany"]}, 1),
        ({"min_altitude": 4000.0, "max_altitude": 6000.0}, 1),
        ({"min_velocity": 240.0}, 2),
        ({"on_ground": True}, 1),
        ({"countries": ["France"]}, 0),
    ],
)
def test_filter_aeroplanes(
    aeroplane_list: List[Aeroplane], filter_kwargs: dict[str, Any], expected_count: int
) -> None:
    """Параметризованный тест фильтрации."""
    result = filter_aeroplanes(aeroplane_list, **filter_kwargs)
    assert len(result) == expected_count


@pytest.mark.parametrize(
    "sort_by, reverse, expected_first_callsign",
    [
        ("altitude", True, "SBI777"),
        ("altitude", False, "BAW500"),
        ("velocity", True, "SBI777"),
        ("callsign", False, "AFL100"),
    ],
)
def test_sort_aeroplanes(
    aeroplane_list: List[Aeroplane], sort_by: str, reverse: bool, expected_first_callsign: str
) -> None:
    """Параметризованный тест сортировки."""
    result = sort_aeroplanes(aeroplane_list, by=sort_by, reverse=reverse)
    assert result[0].callsign == expected_first_callsign


def test_get_top_aeroplanes(aeroplane_list: List[Aeroplane]) -> None:
    """Тест получения топ-N элементов."""
    top = get_top_aeroplanes(aeroplane_list, n=2, by="velocity")
    assert len(top) == 2
    assert top[0].callsign == "SBI777"


def test_get_aeroplanes_by_altitude_range(aeroplane_list: List[Aeroplane]) -> None:
    """Тест обёртки для фильтрации по высоте."""
    result = get_aeroplanes_by_altitude_range(aeroplane_list, 4000.0, 6000.0)
    assert len(result) == 1
    assert result[0].callsign == "AFL100"


def test_print_aeroplanes_empty(capsys: pytest.CaptureFixture[str]) -> None:
    """Тест вывода пустого списка в консоль."""
    print_aeroplanes([], title="Empty Test")
    captured = capsys.readouterr()
    assert "Empty Test" in captured.out
    assert "Нет данных для отображения" in captured.out
