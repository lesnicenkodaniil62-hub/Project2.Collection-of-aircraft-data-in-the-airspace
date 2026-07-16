"""
Консольный интерфейс для взаимодействия с пользователем.

Реализует интерактивное меню с улучшенным UX:
- Диалог выбора режима работы с данными (замена/добавление)
- Предупреждения о несохранённых данных
- Статус-бар после каждого действия
- Система снапшотов для сохранения нескольких версий данных
"""

import logging
from typing import List

from src.api.nominatim import NominatimAPI
from src.api.opensky import OpenSkyAPI
from src.models.aeroplane import Aeroplane
from src.storage.json_saver import JSONSaver
from src.utils.data_processing import (filter_aeroplanes, get_aeroplanes_by_altitude_range, get_top_aeroplanes,
                                       print_aeroplanes, show_status_bar)

logger = logging.getLogger(__name__)


def user_interaction() -> None:
    """
    Основная функция для взаимодействия с пользователем через консоль.

    Возможности:
    1. Получить самолёты по стране (с выбором: заменить или добавить)
    2. Показать топ N самолётов по высоте
    3. Фильтровать самолёты по стране регистрации
    4. Фильтровать самолёты по диапазону высот
    5. Показать все загруженные самолёты
    6. Сохранить текущие данные в снапшот (отдельный файл)
    7. Загрузить данные из снапшота (с предупреждением)
    0. Выход (с проверкой несохранённых данных)
    """
    print("\n" + "=" * 80)
    print(" Добро пожаловать в систему анализа воздушного пространства!")
    print("=" * 80 + "\n")

    # Инициализация API и хранилища
    nominatim_api = NominatimAPI()
    opensky_api = OpenSkyAPI()
    json_saver = JSONSaver()

    all_aeroplanes: List[Aeroplane] = []
    has_unsaved_changes: bool = False

    while True:
        print("\nВыберите действие:")
        print("1. Получить самолёты по стране")
        print("2. Показать топ N самолётов по высоте")
        print("3. Фильтровать самолёты по стране регистрации")
        print("4. Фильтровать самолёты по диапазону высот")
        print("5. Показать все загруженные самолёты")
        print("6. Сохранить текущие данные в снапшот")
        print("7. Загрузить данные из снапшота")
        print("0. Выход")

        choice = input("\nВаш выбор: ").strip()

        if choice == "0":
            # Проверка несохранённых данных при выходе
            if has_unsaved_changes:
                confirm = (
                    input("\n⚠ В памяти есть несохранённые данные. " "Выйти без сохранения? (y/n): ").strip().lower()
                )
                if confirm != "y":
                    continue
            print("\nДо свидания!")
            break

        elif choice == "1":
            # Получить самолёты по стране
            country = input("Введите название страны (например, Spain, Germany): ").strip()
            if not country:
                print("Название страны не может быть пустым")
                continue

            print(f"\nПоиск координат для '{country}'...")
            coordinates = nominatim_api.get_coordinates(country)

            if coordinates:
                lat, lon = coordinates
                print(f"Координаты найдены: широта={lat:.4f}, долгота={lon:.4f}")
            else:
                print(f"Не удалось найти координаты для '{country}'")

            print(f"\nЗапрос самолётов для страны '{country}'...")
            states = opensky_api.get_aeroplanes(country)

            if not states:
                print(f"Самолёты не найдены для страны '{country}'")
                continue

            print(f"Найдено {len(states)} записей")

            # Преобразование в объекты Aeroplane
            aeroplanes = Aeroplane.cast_to_object_list(states, default_country=country)

            if not aeroplanes:
                print("Не удалось преобразовать данные в объекты самолётов")
                continue

            print(f"Успешно создано {len(aeroplanes)} объектов самолётов")

            # Диалог: заменить или добавить
            if all_aeroplanes:
                print(f"\n⚠ В памяти уже есть {len(all_aeroplanes)} самолётов.")
                choice_mem = input("Что сделать? (1) Заменить текущие данные " "(2) Добавить к текущим: ").strip()
                if choice_mem == "1":
                    all_aeroplanes = aeroplanes
                    print("✓ Текущие данные заменены новыми")
                else:
                    all_aeroplanes.extend(aeroplanes)
                    print("✓ Новые данные добавлены к текущим")
            else:
                all_aeroplanes = aeroplanes

            has_unsaved_changes = True
            print_aeroplanes(aeroplanes[:10], title=f"Первые 10 самолётов из '{country}'")
            show_status_bar(len(all_aeroplanes), json_saver.count())

        elif choice == "2":
            if not all_aeroplanes:
                print("Нет загруженных данных. Сначала выполните действие 1 или 7")
                continue
            try:
                n = int(input(f"Введите количество самолётов для топа " f"(1-{len(all_aeroplanes)}): ").strip())
                if n <= 0 or n > len(all_aeroplanes):
                    print(f"Число должно быть в диапазоне " f"от 1 до {len(all_aeroplanes)}")
                    continue
                top_aeroplanes = get_top_aeroplanes(all_aeroplanes, n, by="altitude")
                print_aeroplanes(top_aeroplanes, title=f"Топ {n} самолётов по высоте")
            except ValueError:
                print("Некорректное число. Введите целое положительное число")
            show_status_bar(len(all_aeroplanes), json_saver.count())

        elif choice == "3":
            if not all_aeroplanes:
                print("Нет загруженных данных. Сначала выполните действие 1 или 7")
                continue
            countries_input = input("Введите названия стран через запятую " "(например, Spain, Germany): ").strip()
            if not countries_input:
                print("Список стран не может быть пустым")
                continue
            countries = [c.strip() for c in countries_input.split(",") if c.strip()]
            if not countries:
                print("Некорректный формат списка стран")
                continue
            filtered = filter_aeroplanes(all_aeroplanes, countries=countries)
            if not filtered:
                print(f"Самолёты не найдены для стран: {', '.join(countries)}")
                continue
            print_aeroplanes(filtered, title=f"Самолёты из стран: {', '.join(countries)}")
            show_status_bar(len(all_aeroplanes), json_saver.count())

        elif choice == "4":
            if not all_aeroplanes:
                print("Нет загруженных данных. Сначала выполните действие 1 или 7")
                continue
            try:
                altitude_range = input("Введите диапазон высот (например, 5000-10000): ").strip()
                if "-" not in altitude_range:
                    print("Некорректный формат. Используйте формат: min-max")
                    continue
                parts = altitude_range.split("-")
                if len(parts) != 2:
                    print("Некорректный формат. Используйте формат: min-max")
                    continue
                min_alt = float(parts[0].strip())
                max_alt = float(parts[1].strip())
                if min_alt > max_alt:
                    print("Минимальная высота не может быть больше максимальной")
                    continue
                filtered = get_aeroplanes_by_altitude_range(all_aeroplanes, min_alt, max_alt)
                if not filtered:
                    print(f"Самолёты не найдены в диапазоне " f"высот {min_alt}-{max_alt} м")
                    continue
                print_aeroplanes(filtered, title=f"Самолёты на высоте {min_alt}-{max_alt} м")
            except ValueError:
                print("Некорректный формат высот. Введите числа")
            show_status_bar(len(all_aeroplanes), json_saver.count())

        elif choice == "5":
            if not all_aeroplanes:
                print("Нет загруженных данных. Сначала выполните действие 1 или 7")
                continue
            print_aeroplanes(all_aeroplanes, title="Все загруженные самолёты")
            show_status_bar(len(all_aeroplanes), json_saver.count())

        elif choice == "6":
            if not all_aeroplanes:
                print("Нет данных для сохранения")
                continue
            snapshot_path = json_saver.save_snapshot(all_aeroplanes)
            has_unsaved_changes = False
            print(f"✓ Данные сохранены в снапшот: {snapshot_path.name}")
            show_status_bar(len(all_aeroplanes), json_saver.count())

        elif choice == "7":
            # Предупреждение о несохранённых данных
            if has_unsaved_changes:
                confirm = (
                    input(
                        "\n⚠ В памяти есть несохранённые данные. "
                        "Они будут потеряны при загрузке. Продолжить? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if confirm != "y":
                    continue

            snapshots = json_saver.list_snapshots()
            if not snapshots:
                print("Нет доступных снапшотов. " "Сначала сохраните данные (пункт 6).")
                continue

            print("\nДоступные снапшоты:")
            for idx, snapshot in enumerate(snapshots, start=1):
                print(f"  {idx}. {snapshot.name}")

            choice_snap = input("Выберите номер снапшота (0 для отмены): ").strip()
            try:
                idx = int(choice_snap)
                if idx == 0:
                    continue
                idx -= 1
                if 0 <= idx < len(snapshots):
                    json_saver.load_snapshot(snapshots[idx])
                    all_aeroplanes = json_saver.get_all_aeroplanes()
                    has_unsaved_changes = False
                    print(f"✓ Загружено {len(all_aeroplanes)} " f"самолётов из снапшота")
                    print_aeroplanes(all_aeroplanes[:10], title="Первые 10 загруженных самолётов")
                else:
                    print("Некорректный номер.")
            except ValueError:
                print("Некорректный ввод.")

            show_status_bar(len(all_aeroplanes), json_saver.count())

        else:
            print("Некорректный выбор. Попробуйте снова")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    user_interaction()
