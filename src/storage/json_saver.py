"""
Реализация хранилища на основе JSON-файла.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from src.models.aeroplane import Aeroplane
from src.storage.base import BaseStorage

logger = logging.getLogger(__name__)


class JSONSaver(BaseStorage):
    """
    Хранилище данных о воздушных судах в JSON-файле.

    Формат файла:
    {
        "aeroplanes": [
            {
                "callsign": "UAL1621",
                "country": "United States",
                "velocity": 268.79,
                "altitude": 10203.18,
                ...
            },
            ...
        ]
    }
    """

    def __init__(self) -> None:
        """
        Инициализация JSON-хранилища.
        """
        self.filepath: Path = Path("data/aeroplanes.json")
        self._data: Dict[str, List[Dict[str, Any]]] = {"aeroplanes": []}

        # Загружаем существующие данные, если файл есть
        if self.filepath.exists():
            self._load_from_file()
            logger.info(f"JSONSaver инициализирован: {self.filepath} (загружено {self.count()} записей)")
        else:
            self._save_to_file()
            logger.info(f"JSONSaver инициализирован: {self.filepath} (создан новый файл)")

    def _load_from_file(self) -> None:
        """Загрузить данные из JSON-файла."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "aeroplanes" in data:
                    self._data = data
                else:
                    logger.warning(f"Некорректный формат файла {self.filepath}, создаётся новый")
                    self._data = {"aeroplanes": []}
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Ошибка загрузки {self.filepath}: {e}")
            self._data = {"aeroplanes": []}

    def _save_to_file(self) -> None:
        """Сохранить данные в JSON-файл."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Данные сохранены в {self.filepath}")
        except IOError as e:
            logger.error(f"Ошибка сохранения в {self.filepath}: {e}")
            raise

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить самолёт в хранилище."""
        if self.exists(aeroplane.callsign):
            logger.warning(f"Самолёт {aeroplane.callsign} уже существует, обновление данных")
            # Обновляем существующую запись
            self._data["aeroplanes"] = [a for a in self._data["aeroplanes"] if a["callsign"] != aeroplane.callsign]

        self._data["aeroplanes"].append(aeroplane.to_dict())
        self._save_to_file()
        logger.info(f"Добавлен самолёт: {aeroplane.callsign}")

    def add_aeroplanes(self, aeroplanes: List[Aeroplane]) -> None:
        """Добавить несколько самолётов в хранилище."""
        added_count = 0
        for aeroplane in aeroplanes:
            if not self.exists(aeroplane.callsign):
                self._data["aeroplanes"].append(aeroplane.to_dict())
                added_count += 1
            else:
                logger.debug(f"Пропущен дубликат: {aeroplane.callsign}")

        if added_count > 0:
            self._save_to_file()
            logger.info(f"Добавлено {added_count} самолётов из {len(aeroplanes)}")

    def get_aeroplanes(self, **criteria: Any) -> List[Aeroplane]:
        """Получить самолёты по указанным критериям."""
        result: List[Aeroplane] = []

        for aeroplane_dict in self._data["aeroplanes"]:
            try:
                aeroplane = Aeroplane.from_dict(aeroplane_dict)

                # Применяем фильтры
                if self._matches_criteria(aeroplane, **criteria):
                    result.append(aeroplane)

            except (ValueError, TypeError) as e:
                logger.warning(f"Не удалось загрузить запись: {e}, данные: {aeroplane_dict}")
                continue

        logger.debug(f"Найдено {len(result)} самолётов по критериям: {criteria}")
        return result

    def _matches_criteria(self, aeroplane: Aeroplane, **criteria: Any) -> bool:
        """Проверить, соответствует ли самолёт критериям."""
        # Фильтр по стране
        if "country" in criteria:
            if aeroplane.country.lower() != str(criteria["country"]).lower():
                return False

        # Фильтр по высоте
        if "min_altitude" in criteria:
            if aeroplane.altitude < float(criteria["min_altitude"]):
                return False
        if "max_altitude" in criteria:
            if aeroplane.altitude > float(criteria["max_altitude"]):
                return False

        # Фильтр по скорости
        if "min_velocity" in criteria:
            if aeroplane.velocity < float(criteria["min_velocity"]):
                return False
        if "max_velocity" in criteria:
            if aeroplane.velocity > float(criteria["max_velocity"]):
                return False

        # Фильтр по статусу "на земле"
        if "on_ground" in criteria:
            if aeroplane.on_ground != bool(criteria["on_ground"]):
                return False

        # Фильтр по позывному
        if "callsign" in criteria:
            if aeroplane.callsign != str(criteria["callsign"]):
                return False

        return True

    def get_all_aeroplanes(self) -> List[Aeroplane]:
        """Получить все самолёты из хранилища."""
        result: List[Aeroplane] = []

        for aeroplane_dict in self._data["aeroplanes"]:
            try:
                aeroplane = Aeroplane.from_dict(aeroplane_dict)
                result.append(aeroplane)
            except (ValueError, TypeError) as e:
                logger.warning(f"Не удалось загрузить запись: {e}")
                continue

        return result

    def delete_aeroplane(self, callsign: str) -> bool:
        """Удалить самолёт по позывному."""
        initial_count = len(self._data["aeroplanes"])
        self._data["aeroplanes"] = [a for a in self._data["aeroplanes"] if a["callsign"] != callsign]

        deleted = len(self._data["aeroplanes"]) < initial_count
        if deleted:
            self._save_to_file()
            logger.info(f"Удалён самолёт: {callsign}")
        else:
            logger.warning(f"Самолёт не найден для удаления: {callsign}")

        return deleted

    def delete_aeroplanes(self, **criteria: Any) -> int:
        """Удалить самолёты по указанным критериям."""
        to_delete: List[str] = []

        for aeroplane_dict in self._data["aeroplanes"]:
            try:
                aeroplane = Aeroplane.from_dict(aeroplane_dict)
                if self._matches_criteria(aeroplane, **criteria):
                    to_delete.append(aeroplane.callsign)
            except (ValueError, TypeError) as e:
                logger.warning(f"Не удалось обработать запись: {e}")
                continue

        initial_count = len(self._data["aeroplanes"])
        self._data["aeroplanes"] = [a for a in self._data["aeroplanes"] if a["callsign"] not in to_delete]

        deleted_count = initial_count - len(self._data["aeroplanes"])
        if deleted_count > 0:
            self._save_to_file()
            logger.info(f"Удалено {deleted_count} самолётов по критериям: {criteria}")

        return deleted_count

    def clear(self) -> None:
        """Очистить хранилище."""
        self._data = {"aeroplanes": []}
        self._save_to_file()
        logger.info("Хранилище очищено")

    def count(self) -> int:
        """Получить количество самолётов в хранилище."""
        return len(self._data["aeroplanes"])

    def exists(self, callsign: str) -> bool:
        """Проверить, существует ли самолёт с указанным позывным."""
        return any(a["callsign"] == callsign for a in self._data["aeroplanes"])

    def __repr__(self) -> str:
        return f"<JSONSaver(filepath={self.filepath}, count={self.count()})>"
