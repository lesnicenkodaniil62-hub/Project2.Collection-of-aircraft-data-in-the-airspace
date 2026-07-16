"""
Главный модуль программы для анализа воздушного пространства.

Этот файл является точкой входа (entry point) в приложение.
Он отвечает за:
1. Настройку системы логирования (консоль + файл).
2. Инициализацию и запуск пользовательского интерфейса.
3. Глобальную обработку исключений для безопасного завершения работы.
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

# Добавляем корневую директорию проекта в sys.path.
# Это позволяет импортировать модули из папки 'src' без установки пакета,
# что удобно при запуске скрипта напрямую через 'python main.py'.
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.user_interaction import user_interaction


def setup_logging(level: int = logging.DEBUG) -> None:
    """
    Настройка системы логирования с сохранением в папку logs.

    Реализует стратегию двойного логирования:
    - В консоль выводятся только важные сообщения (INFO и выше), чтобы не
      перегружать интерфейс отладочной информацией.
    - В файл записываются все сообщения (от DEBUG до CRITICAL) для
      последующего анализа и отладки.

    Args:
        level: Минимальный уровень логирования для модулей проекта (по умолчанию DEBUG).
    """
    # 1. Создаем директорию для логов, если её ещё нет.
    # exist_ok=True предотвращает ошибку FileExistsError при повторных запусках.
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "application.log"

    # Унифицированный формат для всех обработчиков:
    # Время | Уровень | Имя модуля | Сообщение
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Получаем корневой логгер (root logger), чтобы перехватывать сообщения
    # от всех модулей приложения, включая сторонние библиотеки.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Разрешаем пропуск всех сообщений

    # Очищаем обработчики, если они уже были добавлены.
    # Это важно при повторном вызове функции (например, в тестах или при перезапуске).
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # 2. Консольный обработчик (StreamHandler).
    # Выводит сообщения в stderr (стандартный поток ошибок), чтобы логи
    # не смешивались с обычным выводом программы (stdout) через print().
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)  # Фильтруем: в консоль пойдет только INFO, WARNING, ERROR, CRITICAL
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)

    # 3. Файловый обработчик (FileHandler).
    # Записывает все сообщения, включая DEBUG, в файл.
    # encoding="utf-8" гарантирует корректную запись кириллицы в любых ОС.
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(file_handler)

    # 4. Тонкая настройка уровней для конкретных модулей.
    # Наши модули должны логировать на заданном уровне (например, DEBUG).
    logging.getLogger("src").setLevel(level)

    # Сторонние библиотеки (requests, urllib3) часто очень многословны.
    # Принудительно повышаем их порог до WARNING, чтобы избежать "спама" в логах.
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def print_banner() -> None:
    """
    Вывод приветственного ASCII-баннера в консоль.
    Служит для визуального подтверждения успешного запуска приложения.
    """
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
    Главная функция программы (точка входа в бизнес-логику).

    Returns:
        int: Код выхода процесса.
             0 — успешное завершение,
             1 — завершение из-за необработанной критической ошибки.
    """
    try:
        # Инициализация логирования перед любыми другими действиями
        setup_logging(level=logging.DEBUG)

        # Получаем логгер для текущего модуля (__main__)
        logger = logging.getLogger(__name__)
        logger.info("Запуск программы")

        # Демонстрация работы всех уровней логирования.
        # Эти сообщения подтверждают, что FileHandler корректно сохраняет
        # все уровни, а StreamHandler фильтрует DEBUG.
        logger.debug("Это сообщение уровня DEBUG (попадет только в файл logs/application.log)")
        logger.info("Это сообщение уровня INFO")
        logger.warning("Это сообщение уровня WARNING")
        logger.error("Это сообщение уровня ERROR")
        logger.critical("Это сообщение уровня CRITICAL")

        # Вывод баннера и запуск основного интерактивного цикла
        print_banner()
        user_interaction()

        logger.info("Программа завершена штатным образом")
        return 0

    except KeyboardInterrupt:
        # Перехватываем Ctrl+C для корректного (graceful) завершения работы.
        # Это предотвращает вывод некрасивого traceback-а в консоль.
        print("\n\n  Программа прервана пользователем")
        logging.getLogger(__name__).info("Программа прервана пользователем (Ctrl+C)")
        return 0

    except Exception as e:
        # Перехват любых неожиданных исключений, чтобы программа не "падала" молча.
        # .exception() автоматически добавляет полный traceback в лог-файл.
        print(f"\n\n Критическая ошибка: {e}")
        logging.getLogger(__name__).exception("Критическая ошибка при выполнении программы")
        return 1


# Стандартная идиома Python для проверки, что файл запущен напрямую,
# а не импортирован как модуль.
if __name__ == "__main__":
    # sys.exit() принимает код возврата из main() и завершает процесс
    sys.exit(main())
