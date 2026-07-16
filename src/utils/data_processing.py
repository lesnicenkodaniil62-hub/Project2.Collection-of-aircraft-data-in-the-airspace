"""
Модуль утилит для обработки, фильтрации и отображения данных о самолётах.

Реализует принцип SRP (Single Responsibility Principle): данный модуль отвечает
исключительно за преобразование и представление коллекций объектов Aeroplane,
не занимаясь сетевыми запросами или сохранением в файлы.

Все функции являются чистыми (pure functions) или имеют минимальные побочные
эффекты (например, вывод в консоль), что делает их легко тестируемыми.

Изменения:
    - Устранена ошибка flake8 E731: lambda-выражение заменено на именованную
      внутреннюю функцию _get_sort_key.
    - Устранена ошибка flake8 E501: длинные строки разбиты на несколько частей
      с использованием неявной конкатенации строк Python.
    - Улучшен интерфейс вывода print_aeroplanes: добавлены заголовки столбцов,
      нумерация записей, разделители и итоговая информация.
"""

import logging
from typing import Any, List

from src.models.aeroplane import Aeroplane

logger = logging.getLogger(__name__)


def filter_aeroplanes(aeroplanes: List[Aeroplane], **criteria: Any) -> List[Aeroplane]:
    """
    Фильтрация списка самолётов по заданным критериям.

    Использует гибкий подход через **kwargs, что позволяет комбинировать
    любое количество условий фильтрации без изменения сигнатуры функции
    (принцип Open/Closed).

    Args:
        aeroplanes: Исходный список объектов Aeroplane для фильтрации.
        **criteria: Именованные аргументы-критерии. Поддерживаемые ключи:
            - countries (List[str]): Список допустимых стран (регистронезависимый поиск).
            - min_altitude (float): Минимальная высота полёта (включительно).
            - max_altitude (float): Максимальная высота полёта (включительно).
            - min_velocity (float): Минимальная скорость (включительно).
            - max_velocity (float): Максимальная скорость (включительно).
            - on_ground (bool): Фильтр по статусу нахождения на земле.

    Returns:
        Новый список объектов Aeroplane, удовлетворяющих всем указанным критериям.
        Если критерии не переданы, возвращает копию исходного списка.
    """
    result: List[Aeroplane] = []

    # Нормализуем список стран для быстрого и регистронезависимого поиска
    countries_lower: List[str] = [str(c).lower() for c in criteria.get("countries", [])]

    for plane in aeroplanes:
        # 1. Фильтр по стране (поддержка множественного выбора)
        if countries_lower and plane.country.lower() not in countries_lower:
            continue

        # 2. Фильтр по диапазону высот
        if "min_altitude" in criteria and plane.altitude < float(criteria["min_altitude"]):
            continue
        if "max_altitude" in criteria and plane.altitude > float(criteria["max_altitude"]):
            continue

        # 3. Фильтр по диапазону скоростей
        if "min_velocity" in criteria and plane.velocity < float(criteria["min_velocity"]):
            continue
        if "max_velocity" in criteria and plane.velocity > float(criteria["max_velocity"]):
            continue

        # 4. Фильтр по статусу "на земле"
        if "on_ground" in criteria and plane.on_ground != bool(criteria["on_ground"]):
            continue

        # Если все проверки пройдены, добавляем самолёт в результат
        result.append(plane)

    logger.debug(f"Фильтрация: из {len(aeroplanes)} отобрано {len(result)} по критериям {criteria}")
    return result


def _get_sort_key(plane: Aeroplane, attribute: str) -> Any:
    """
    Внутренняя вспомогательная функция для получения значения атрибута самолёта.

    Используется как key-функция при сортировке. Вынесена в отдельную именованную
    функцию вместо lambda-выражения для соответствия PEP 8 (правило E731),
    улучшения читаемости и упрощения отладки.

    Args:
        plane: Объект Aeroplane, из которого извлекается значение атрибута.
        attribute: Имя атрибута объекта Aeroplane (например, "altitude", "velocity").

    Returns:
        Значение указанного атрибута. Если атрибут не существует, возвращает 0
        (защита от AttributeError при использовании несуществующих ключей).
    """
    return getattr(plane, attribute, 0)


def sort_aeroplanes(aeroplanes: List[Aeroplane], by: str = "altitude", reverse: bool = False) -> List[Aeroplane]:
    """
    Сортировка списка самолётов по заданному атрибуту.

    Args:
        aeroplanes: Исходный список объектов Aeroplane.
        by: Имя атрибута объекта Aeroplane, по которому производится сортировка
            (например, "altitude", "velocity", "callsign"). По умолчанию "altitude".
        reverse: Если True, сортирует по убыванию. По умолчанию False (по возрастанию).

    Returns:
        Новый отсортированный список объектов Aeroplane. Исходный список не изменяется.
    """
    logger.debug(f"Сортировка {len(aeroplanes)} самолётов по полю '{by}', reverse={reverse}")

    # Используем именованную вспомогательную функцию вместо lambda для соответствия PEP 8.
    def key_func(plane: Aeroplane) -> Any:
        return _get_sort_key(plane, by)

    return sorted(aeroplanes, key=key_func, reverse=reverse)


def get_top_aeroplanes(aeroplanes: List[Aeroplane], n: int, by: str = "altitude") -> List[Aeroplane]:
    """
    Получение топ-N самолётов по заданному параметру.

    Args:
        aeroplanes: Исходный список объектов Aeroplane.
        n: Количество возвращаемых элементов (топ-N).
        by: Атрибут для сортировки (по умолчанию "altitude").

    Returns:
        Список из максимум N объектов Aeroplane, отсортированных по убыванию
        заданного атрибута.
    """
    # Сортируем по убыванию (reverse=True), чтобы получить максимальные значения первыми
    sorted_planes: List[Aeroplane] = sort_aeroplanes(aeroplanes, by=by, reverse=True)
    return sorted_planes[:n]


def get_aeroplanes_by_altitude_range(aeroplanes: List[Aeroplane], min_alt: float, max_alt: float) -> List[Aeroplane]:
    """
    Удобная обёртка для фильтрации самолётов строго по диапазону высот.

    Args:
        aeroplanes: Исходный список объектов Aeroplane.
        min_alt: Минимальная граница высоты (в метрах).
        max_alt: Максимальная граница высоты (в метрах).

    Returns:
        Список самолётов, летящих в заданном эшелоне.
    """
    return filter_aeroplanes(aeroplanes, min_altitude=min_alt, max_altitude=max_alt)


def print_aeroplanes(aeroplanes: List[Aeroplane], title: str = "Самолёты") -> None:
    """
    Форматированный вывод списка самолётов в стандартный поток вывода (консоль).

    Улучшенный интерфейс включает:
    - Заголовки столбцов с понятными названиями
    - Разделительные линии для визуального разделения секций
    - Нумерацию записей для удобства ссылок
    - Итоговую строку с общим количеством записей
    - Единицы измерения в заголовках

    Args:
        aeroplanes: Список объектов Aeroplane для вывода.
        title: Заголовок секции вывода. По умолчанию "Самолёты".
    """
    # Константы для форматирования таблицы
    separator = "═" * 100
    divider = "─" * 100

    # Верхняя граница таблицы
    print("\n" + separator)
    print(f"  {title.upper()}")
    print(separator)

    if not aeroplanes:
        print("  ⚠ Нет данных для отображения по заданным критериям.")
    else:
        # Заголовки столбцов с единицами измерения
        # Разбиваем на несколько строк для соответствия PEP 8 (E501)
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

        # Вывод данных с нумерацией
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

        # Нижняя граница с итоговой информацией
        print(divider)
        print(f"  Всего записей: {len(aeroplanes)}")

    print(separator + "\n")
