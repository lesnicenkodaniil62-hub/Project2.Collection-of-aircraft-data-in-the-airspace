"""
Пакет для работы с хранилищами данных.
"""

from src.storage.base import BaseStorage
from src.storage.json_saver import JSONSaver

__all__ = ["BaseStorage", "JSONSaver"]
