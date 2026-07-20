"""
Абстрактный базовый класс для работы с хранилищами данных.

Архитектура аналогична BaseAPI: реализация __repr__ вынесена в миксин,
абстрактный класс содержит ТОЛЬКО объявления методов (@abstractmethod).
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, List

from src.models.aeroplane import Aeroplane

logger = logging.getLogger(__name__)


class StorageReprMixin:
    """
    Миксин для строкового представления хранилища.

    Вынесен из абстрактного класса, чтобы BaseStorage содержал только
    объявления абстрактных методов без какой-либо реализации.
    """

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"<{self.__class__.__name__}>"


class BaseStorage(StorageReprMixin, ABC):
    """
    Абстрактный базовый класс для хранилищ данных о воздушных судах.

    Содержит ТОЛЬКО объявления абстрактных методов без реализации.
    Все классы-наследники обязаны реализовать каждый из этих методов.
    """

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить самолёт в хранилище."""
        pass

    @abstractmethod
    def add_aeroplanes(self, aeroplanes: List[Aeroplane]) -> None:
        """Добавить несколько самолётов в хранилище."""
        pass

    @abstractmethod
    def get_aeroplanes(self, **criteria: Any) -> List[Aeroplane]:
        """Получить самолёты по указанным критериям."""
        pass

    @abstractmethod
    def get_all_aeroplanes(self) -> List[Aeroplane]:
        """Получить все самолёты из хранилища."""
        pass

    @abstractmethod
    def delete_aeroplane(self, callsign: str) -> bool:
        """Удалить самолёт по позывному."""
        pass

    @abstractmethod
    def delete_aeroplanes(self, **criteria: Any) -> int:
        """Удалить самолёты по указанным критериям."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Очистить хранилище."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Получить количество самолётов в хранилище."""
        pass

    @abstractmethod
    def exists(self, callsign: str) -> bool:
        """Проверить, существует ли самолёт с указанным позывным."""
        pass
