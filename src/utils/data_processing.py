"""
Модуль утилит для обработки, фильтрации и отображения данных о самолётах.

Реализует принцип SRP (Single Responsibility Principle): данный модуль отвечает
исключительно за преобразование и представление коллекций объектов Aeroplane,
не занимаясь сетевыми запросами или сохранением в файлы.

Все функции являются чистыми (pure functions) или имеют минимальные побочные
эффекты (например, вывод в консоль), что делает их легко тестируемыми.
"""

import logging
from typing import Any, List

from src.models.aeroplane import Aeroplane

logger = logging.getLogger(__name__)


def filter_aeroplanes(aeroplanes: List[Aeroplane], **criteria: Any) -> List[Aeroplane]:
    """
    Фильтрация списка самолётов по заданным критериям.

    Args:
        aeroplanes: Исходный список объектов Aeroplane для фильтрации.
        **criteria: Именованные аргументы-критерии. Поддерживаемые ключи:
            - countries (List[str]): Список допустимых стран.
            - min_altitude (float): Минимальная высота полёта.
            - max_altitude (float): Максимальная высота полёта.
            - min_velocity (float): Минимальная скорость.
            - max_velocity (float): Максимальная скорость.
            - on_ground (bool): Фильтр по статусу нахождения на земле.

    Returns:
        Новый список объектов Aeroplane, удовлетворяющих всем критериям.
    """
    result: List[Aeroplane] = []
    countries_lower: List[str] = [str(c).lower() for c in criteria.get("countries", [])]

    for plane in aeroplanes:
        if countries_lower and plane.country.lower() not in countries_lower:
            continue
        if "min_altitude" in criteria and plane.altitude < float(criteria["min_altitude"]):
            continue
        if "max_altitude" in criteria and plane.altitude > float(criteria["max_altitude"]):
            continue
        if "min_velocity" in criteria and plane.velocity < float(criteria["min_velocity"]):
            continue
        if "max_velocity" in criteria and plane.velocity > float(criteria["max_velocity"]):
            continue
        if "on_ground" in criteria and plane.on_ground != bool(criteria["on_ground"]):
            continue
        result.append(plane)

    logger.debug(f"Фильтрация: из {len(aeroplanes)} отобрано {len(result)} " f"по критериям {criteria}")
    return result


def _get_sort_key(plane: Aeroplane, attribute: str) -> Any:
    """
    Внутренняя вспомогательная функция для получения значения атрибута.

    Args:
        plane: Объект Aeroplane.
        attribute: Имя атрибута для извлечения.

    Returns:
        Значение атрибута или 0, если атрибут не существует.
    """
    return getattr(plane, attribute, 0)


def sort_aeroplanes(aeroplanes: List[Aeroplane], by: str = "altitude", reverse: bool = False) -> List[Aeroplane]:
    """
    Сортировка списка самолётов по заданному атрибуту.

    Args:
        aeroplanes: Исходный список объектов Aeroplane.
        by: Имя атрибута для сортировки. По умолчанию "altitude".
        reverse: Если True, сортирует по убыванию.

    Returns:
        Новый отсортированный список объектов Aeroplane.
    """
    logger.debug(f"Сортировка {len(aeroplanes)} самолётов по полю '{by}', " f"reverse={reverse}")

    def key_func(plane: Aeroplane) -> Any:
        return _get_sort_key(plane, by)

    return sorted(aeroplanes, key=key_func, reverse=reverse)


def get_top_aeroplanes(aeroplanes: List[Aeroplane], n: int, by: str = "altitude") -> List[Aeroplane]:
    """
    Получение топ-N самолётов по заданному параметру.

    Args:
        aeroplanes: Исходный список объектов Aeroplane.
        n: Количество возвращаемых элементов.
        by: Атрибут для сортировки.

    Returns:
        Список из максимум N объектов, отсортированных по убыванию.
    """
    sorted_planes: List[Aeroplane] = sort_aeroplanes(aeroplanes, by=by, reverse=True)
    return sorted_planes[:n]


def get_aeroplanes_by_altitude_range(aeroplanes: List[Aeroplane], min_alt: float, max_alt: float) -> List[Aeroplane]:
    """
    Удобная обёртка для фильтрации самолётов по диапазону высот.

    Args:
        aeroplanes: Исходный список объектов Aeroplane.
        min_alt: Минимальная граница высоты (в метрах).
        max_alt: Максимальная граница высоты (в метрах).

    Returns:
        Список самолётов в заданном диапазоне высот.
    """
    return filter_aeroplanes(aeroplanes, min_altitude=min_alt, max_altitude=max_alt)


def print_aeroplanes(aeroplanes: List[Aeroplane], title: str = "Самолёты") -> None:
    """
    Форматированный вывод списка самолётов в консоль.

    Args:
        aeroplanes: Список объектов Aeroplane для вывода.
        title: Заголовок секции вывода.
    """
    separator = "═" * 100
    divider = "─" * 100

    print("\n" + separator)
    print(f"  {title.upper()}")
    print(separator)

    if not aeroplanes:
        print("  ⚠ Нет данных для отображения по заданным критериям.")
    else:
        header = (
            f"  {'№':<4} │ "
            f"{'Позывной':<10} │ "
            f"{'Страна':<20} │ "
            f"{'Скорость (м/с)':<15} │ "
            f"{'Высота (м)':<12} │ "
            f"{'Статус':<10}"
        )
        print(header)
        print(divider)

        for idx, plane in enumerate(aeroplanes, start=1):
            status = "На земле" if plane.on_ground else "В воздухе"
            row = (
                f"  {idx:<4} │ "
                f"{plane.callsign:<10} │ "
                f"{plane.country:<20} │ "
                f"{plane.velocity:<15.2f} │ "
                f"{plane.altitude:<12.2f} │ "
                f"{status:<10}"
            )
            print(row)

        print(divider)
        print(f"  Всего записей: {len(aeroplanes)}")

    print(separator + "\n")


def show_status_bar(memory_count: int, file_count: int) -> None:
    """
    Вывод статус-бара с информацией о количестве самолётов.

    Отображает текущее состояние системы: сколько самолётов загружено
    в оперативную память и сколько сохранено в рабочем файле. Это помогает
    пользователю понимать, какие данные будут использованы при операциях
    фильтрации, сортировки и сохранения.

    Args:
        memory_count: Количество самолётов в оперативной памяти.
        file_count: Количество самолётов в рабочем файле.
    """
    print(f"\n  📊 Статус: В памяти: {memory_count} | В файле: {file_count}")
