"""
Главный модуль программы для анализа воздушного пространства.

Объединяет все компоненты:
- API-клиенты (Nominatim, OpenSky)
- Модель данных Aeroplane
- Хранилище JSONSaver
- Консольный интерфейс user_interaction

Использование:
    python main.py
"""

import logging
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHON_PATH для корректного импорта
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.user_interaction import user_interaction


def setup_logging(level: int = logging.INFO) -> None:
    """
    Настройка системы логирования.

    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
    """
    # Формат логов: время | уровень | модуль | сообщение
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Настройка корневого логгера
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Вывод в консоль (только WARNING и выше, чтобы не мешать интерфейсу)
            logging.StreamHandler(sys.stderr),
        ],
    )

    # Устанавливаем уровень для наших модулей
    logging.getLogger("src").setLevel(level)

    # Снижаем уровень для внешних библиотек (чтобы не спамили)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def print_banner() -> None:
    """Вывод приветственного баннера."""
    banner = r"""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║           ✈  СИСТЕМА АНАЛИЗА ВОЗДУШНОГО ПРОСТРАНСТВА  ✈                 ║
    ║                                                                          ║
    ║           Работа с API OpenSky Network и OpenStreetMap                   ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main() -> int:
    """
    Главная функция программы.

    Returns:
        Код выхода (0 — успех, 1 — ошибка)
    """
    try:
        # Настройка логирования
        setup_logging(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("Запуск программы")

        # Приветствие
        print_banner()

        # Запуск интерактивного режима
        user_interaction()

        logger.info("Программа завершена")
        return 0

    except KeyboardInterrupt:
        print("\n\n  Программа прервана пользователем")
        logging.getLogger(__name__).info("Программа прервана пользователем (Ctrl+C)")
        return 0
    except Exception as e:
        print(f"\n\n Критическая ошибка: {e}")
        logging.getLogger(__name__).exception("Критическая ошибка")
        return 1


if __name__ == "__main__":
    sys.exit(main())
