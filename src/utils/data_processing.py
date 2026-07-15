"""
Утилиты для обработки данных о воздушных судах.
Фильтрация, сортировка, топ N, вывод в консоль.
"""

import logging
from typing import List, Optional

from src.models.aeroplane import Aeroplane

logger = logging.getLogger(__name__)


def filter_aeroplanes(
    aeroplanes: List[Aeroplane],
    countries: Optional[List[str]] = None,
    min_altitude: Optional[float] = None,
    max_altitude: Optional[float] = None,
    min_velocity: Optional[float] = None,
    max_velocity: Optional[float] = None,
    on_ground: Optional[bool] = None,
) -> List[Aeroplane]:
    """
    Фильтрация самолётов по указанным критериям.

    Args:
        aeroplanes: Список самолётов для фильтрации
        countries: Список стран для фильтрации (регистронезависимо)
        min_altitude: Минимальная высота (м)
        max_altitude: Максимальная высота (м)
        min_velocity: Минимальная скорость (м/с)
        max_velocity: Максимальная скорость (м/с)
        on_ground: Фильтр по статусу "на земле"

    Returns:
        Отфильтрованный список самолётов
    """
    if not aeroplanes:
        logger.warning("Пустой список самолётов для фильтрации")
        return []

    result: List[Aeroplane] = []

    for aeroplane in aeroplanes:
        # Фильтр по странам
        if countries:
            country_match = any(aeroplane.country.lower() == country.lower() for country in countries)
            if not country_match:
                continue

        # Фильтр по высоте
        if min_altitude is not None and aeroplane.altitude < min_altitude:
            continue
        if max_altitude is not None and aeroplane.altitude > max_altitude:
            continue

        # Фильтр по скорости
        if min_velocity is not None and aeroplane.velocity < min_velocity:
            continue
        if max_velocity is not None and aeroplane.velocity > max_velocity:
            continue

        # Фильтр по статусу "на земле"
        if on_ground is not None and aeroplane.on_ground != on_ground:
            continue

        result.append(aeroplane)

    logger.info(f"Фильтрация: из {len(aeroplanes)} осталось {len(result)} самолётов")
    return result


def sort_aeroplanes(aeroplanes: List[Aeroplane], by: str = "altitude", reverse: bool = True) -> List[Aeroplane]:
    """
    Сортировка самолётов по указанному полю.

    Args:
        aeroplanes: Список самолётов для сортировки
        by: Поле для сортировки ("altitude", "velocity", "callsign", "country")
        reverse: True для сортировки по убыванию (DESC), False для возрастания (ASC)

    Returns:
        Отсортированный список самолётов
    """
    if not aeroplanes:
        logger.warning("Пустой список самолётов для сортировки")
        return []

    valid_fields = {"altitude", "velocity", "callsign", "country"}
    if by not in valid_fields:
        logger.error(f"Некорректное поле для сортировки: {by}. Допустимые: {valid_fields}")
        raise ValueError(f"Некорректное поле для сортировки: {by}")

    sorted_list = sorted(aeroplanes, key=lambda a: getattr(a, by), reverse=reverse)

    order = "DESC" if reverse else "ASC"
    logger.info(f"Сортировка по {by} ({order}): {len(sorted_list)} самолётов")
    return sorted_list


def get_top_aeroplanes(aeroplanes: List[Aeroplane], n: int, by: str = "altitude") -> List[Aeroplane]:
    """
    Получить топ N самолётов по указанному полю.

    Args:
        aeroplanes: Список самолётов
        n: Количество самолётов для вывода
        by: Поле для сортировки (по умолчанию "altitude")

    Returns:
        Топ N самолётов
    """
    if not aeroplanes:
        logger.warning("Пустой список самолётов для получения топа")
        return []

    if n <= 0:
        logger.error(f"Некорректное значение N: {n}")
        raise ValueError(f"N должно быть положительным числом, получено: {n}")

    # Сортируем по убыванию (DESC) для получения топа
    sorted_list = sort_aeroplanes(aeroplanes, by=by, reverse=True)
    top_n = sorted_list[:n]

    logger.info(f"Топ {n} по {by}: получено {len(top_n)} самолётов")
    return top_n


def get_aeroplanes_by_altitude_range(
    aeroplanes: List[Aeroplane], min_altitude: float, max_altitude: float
) -> List[Aeroplane]:
    """
    Получить самолёты в указанном диапазоне высот.

    Args:
        aeroplanes: Список самолётов
        min_altitude: Минимальная высота (м)
        max_altitude: Максимальная высота (м)

    Returns:
        Список самолётов в диапазоне высот
    """
    if min_altitude > max_altitude:
        logger.error(f"Некорректный диапазон высот: {min_altitude} > {max_altitude}")
        raise ValueError(f"min_altitude ({min_altitude}) не может быть больше max_altitude ({max_altitude})")

    return filter_aeroplanes(aeroplanes, min_altitude=min_altitude, max_altitude=max_altitude)


def print_aeroplanes(aeroplanes: List[Aeroplane], title: str = "Самолёты", show_index: bool = True) -> None:
    """
    Вывести список самолётов в консоль в читаемом формате.

    Args:
        aeroplanes: Список самолётов для вывода
        title: Заголовок таблицы
        show_index: Показывать ли порядковые номера
    """
    if not aeroplanes:
        print(f"\n{title}: нет данных для отображения\n")
        return

    print(f"\n{'=' * 80}")
    print(f" {title} (всего: {len(aeroplanes)})")
    print(f"{'=' * 80}")

    # Заголовок таблицы
    if show_index:
        print(
            f"{'№':>3} | {'Позывной':<8} | {'Страна':<20} | {'Скорость (м/с)':>14} | {'Высота (м)':>12} | {'На земле':>8}"
        )
        print(f"{'-' * 3}-+-{'-' * 8}-+-{'-' * 20}-+-{'-' * 14}-+-{'-' * 12}-+-{'-' * 8}")
    else:
        print(f"{'Позывной':<8} | {'Страна':<20} | {'Скорость (м/с)':>14} | {'Высота (м)':>12} | {'На земле':>8}")
        print(f"{'-' * 8}-+-{'-' * 20}-+-{'-' * 14}-+-{'-' * 12}-+-{'-' * 8}")

    # Данные
    for idx, aeroplane in enumerate(aeroplanes, start=1):
        on_ground_str = "Да" if aeroplane.on_ground else "Нет"

        if show_index:
            print(
                f"{idx:>3} | "
                f"{aeroplane.callsign:<8} | "
                f"{aeroplane.country:<20} | "
                f"{aeroplane.velocity:>14.2f} | "
                f"{aeroplane.altitude:>12.2f} | "
                f"{on_ground_str:>8}"
            )
        else:
            print(
                f"{aeroplane.callsign:<8} | "
                f"{aeroplane.country:<20} | "
                f"{aeroplane.velocity:>14.2f} | "
                f"{aeroplane.altitude:>12.2f} | "
                f"{on_ground_str:>8}"
            )

    print(f"{'=' * 80}\n")
