"""
Абстрактный базовый класс для работы с хранилищами данных.
Реализует принцип SRP (SOLID) — один класс отвечает за контракт хранилища.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, List

from src.models.aeroplane import Aeroplane

logger = logging.getLogger(__name__)


class BaseStorage(ABC):
    """
    Абстрактный базовый класс для хранилищ данных о воздушных судах.

    Все классы-наследники обязаны реализовать методы для:
    - Добавления самолётов
    - Получения самолётов по критериям
    - Удаления самолётов
    - Очистки хранилища
    """

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """
        Добавить самолёт в хранилище.

        Args:
            aeroplane: Объект Aeroplane для добавления

        Raises:
            ValueError: Если самолёт уже существует (по callsign)
        """
        pass

    @abstractmethod
    def add_aeroplanes(self, aeroplanes: List[Aeroplane]) -> None:
        """
        Добавить несколько самолётов в хранилище.

        Args:
            aeroplanes: Список объектов Aeroplane для добавления
        """
        pass

    @abstractmethod
    def get_aeroplanes(self, **criteria: Any) -> List[Aeroplane]:
        """
        Получить самолёты по указанным критериям.

        Поддерживаемые критерии (зависят от реализации):
        - country: Фильтр по стране регистрации
        - min_altitude: Минимальная высота
        - max_altitude: Максимальная высота
        - min_velocity: Минимальная скорость
        - max_velocity: Максимальная скорость
        - on_ground: Фильтр по статусу "на земле"
        - callsign: Точное совпадение позывного

        Args:
            **criteria: Критерии фильтрации

        Returns:
            Список объектов Aeroplane, соответствующих критериям
        """
        pass

    @abstractmethod
    def get_all_aeroplanes(self) -> List[Aeroplane]:
        """
        Получить все самолёты из хранилища.

        Returns:
            Список всех объектов Aeroplane
        """
        pass

    @abstractmethod
    def delete_aeroplane(self, callsign: str) -> bool:
        """
        Удалить самолёт по позывному.

        Args:
            callsign: Позывной самолёта для удаления

        Returns:
            True если самолёт найден и удалён, False если не найден
        """
        pass

    @abstractmethod
    def delete_aeroplanes(self, **criteria: Any) -> int:
        """
        Удалить самолёты по указанным критериям.

        Args:
            **criteria: Критерии фильтрации для удаления

        Returns:
            Количество удалённых самолётов
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Очистить хранилище (удалить все самолёты).
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Получить количество самолётов в хранилище.

        Returns:
            Количество объектов Aeroplane
        """
        pass

    @abstractmethod
    def exists(self, callsign: str) -> bool:
        """
        Проверить, существует ли самолёт с указанным позывным.

        Args:
            callsign: Позывной для проверки

        Returns:
            True если самолёт существует, False иначе
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
