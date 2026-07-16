"""
Реализация хранилища на основе JSON-файла.

Поддерживает две концепции хранения:
1. Рабочий файл (data/aeroplanes.json) — используется как промежуточное хранилище
   при загрузке снапшотов.
2. Снапшоты (aeroplanes_<timestamp>.json) — отдельные файлы с уникальными именами,
   создаваемые при каждом сохранении. Позволяют хранить несколько состояний данных
   и переключаться между ними.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.models.aeroplane import Aeroplane
from src.storage.base import BaseStorage

logger = logging.getLogger(__name__)


class JSONSaver(BaseStorage):
    """
    Хранилище данных о воздушных судах в JSON-файле.

    Поддерживает создание снапшотов — отдельных файлов с уникальными именами,
    содержащих состояние данных на момент сохранения. Это позволяет:
    - Хранить несколько версий данных одновременно
    - Возвращаться к предыдущим состояниям
    - Избежать потери данных при перезаписи
    """

    def __init__(self) -> None:
        """
        Инициализация JSON-хранилища.

        Создаёт рабочий файл data/aeroplanes.json, если он не существует.
        """
        self.filepath: Path = Path("data/aeroplanes.json")
        self._data: Dict[str, List[Dict[str, Any]]] = {"aeroplanes": []}

        # Гарантируем существование директории data/
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        # Загружаем существующие данные, если файл есть
        if self.filepath.exists():
            self._load_from_file()
            logger.info(f"JSONSaver инициализирован: {self.filepath} " f"(загружено {self.count()} записей)")
        else:
            self._save_to_file()
            logger.info(f"JSONSaver инициализирован: {self.filepath} (создан новый файл)")

    def _load_from_file(self) -> None:
        """Загрузить данные из рабочего JSON-файла."""
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
        """Сохранить текущее состояние в рабочий JSON-файл."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Данные сохранены в {self.filepath}")
        except IOError as e:
            logger.error(f"Ошибка сохранения в {self.filepath}: {e}")
            raise

    def save_snapshot(self, aeroplanes: List[Aeroplane]) -> Path:
        """
        Сохранить список самолётов в отдельный файл-снапшот.

        Имя файла формируется на основе текущей даты и времени в формате
        aeroplanes_YYYYMMDD_HHMMSS.json, что гарантирует уникальность
        и позволяет легко идентифицировать время создания снапшота.

        Args:
            aeroplanes: Список объектов Aeroplane для сохранения.

        Returns:
            Path: Путь к созданному файлу-снапшоту.
        """
        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name: str = f"aeroplanes_{timestamp}.json"
        snapshot_path: Path = self.filepath.parent / snapshot_name

        data: Dict[str, List[Dict[str, Any]]] = {"aeroplanes": [a.to_dict() for a in aeroplanes]}

        try:
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Создан снапшот: {snapshot_path}")
        except IOError as e:
            logger.error(f"Ошибка создания снапшота {snapshot_path}: {e}")
            raise

        return snapshot_path

    def list_snapshots(self) -> List[Path]:
        """
        Получить список всех доступных снапшотов.

        Возвращает файлы в директории data/, соответствующие шаблону
        aeroplanes_*.json, отсортированные по убыванию имени (новые первыми).

        Returns:
            List[Path]: Список путей к файлам-снапшотам.
        """
        snapshots: List[Path] = []
        for file in self.filepath.parent.glob("aeroplanes_*.json"):
            snapshots.append(file)
        return sorted(snapshots, reverse=True)

    def load_snapshot(self, snapshot_path: Path) -> None:
        """
        Загрузить снапшот в рабочий файл.

        Копирует содержимое указанного снапшота в рабочий файл
        data/aeroplanes.json, делая его текущим рабочим состоянием.

        Args:
            snapshot_path: Путь к файлу-снапшоту для загрузки.

        Raises:
            FileNotFoundError: Если указанный снапшот не существует.
        """
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Снапшот не найден: {snapshot_path}")

        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "aeroplanes" in data:
                self._data = data
            else:
                logger.warning(f"Некорректный формат снапшота {snapshot_path}")
                self._data = {"aeroplanes": []}

            self._save_to_file()
            logger.info(f"Снапшот {snapshot_path.name} загружен в рабочий файл")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Ошибка загрузки снапшота {snapshot_path}: {e}")
            raise

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить самолёт в хранилище."""
        if self.exists(aeroplane.callsign):
            logger.warning(f"Самолёт {aeroplane.callsign} уже существует, обновление данных")
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
                if self._matches_criteria(aeroplane, **criteria):
                    result.append(aeroplane)
            except (ValueError, TypeError) as e:
                logger.warning(f"Не удалось загрузить запись: {e}, данные: {aeroplane_dict}")
                continue

        logger.debug(f"Найдено {len(result)} самолётов по критериям: {criteria}")
        return result

    def _matches_criteria(self, aeroplane: Aeroplane, **criteria: Any) -> bool:
        """Проверить, соответствует ли самолёт критериям."""
        if "country" in criteria:
            if aeroplane.country.lower() != str(criteria["country"]).lower():
                return False

        if "min_altitude" in criteria:
            if aeroplane.altitude < float(criteria["min_altitude"]):
                return False
        if "max_altitude" in criteria:
            if aeroplane.altitude > float(criteria["max_altitude"]):
                return False

        if "min_velocity" in criteria:
            if aeroplane.velocity < float(criteria["min_velocity"]):
                return False
        if "max_velocity" in criteria:
            if aeroplane.velocity > float(criteria["max_velocity"]):
                return False

        if "on_ground" in criteria:
            if aeroplane.on_ground != bool(criteria["on_ground"]):
                return False

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
