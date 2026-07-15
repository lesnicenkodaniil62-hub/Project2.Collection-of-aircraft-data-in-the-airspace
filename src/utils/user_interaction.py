"""
Консольный интерфейс для взаимодействия с пользователем.
"""

import logging
from typing import List

from src.api.nominatim import NominatimAPI
from src.api.opensky import OpenSkyAPI
from src.models.aeroplane import Aeroplane
from src.storage.json_saver import JSONSaver
from src.utils.data_processing import (filter_aeroplanes, get_aeroplanes_by_altitude_range, get_top_aeroplanes,
                                       print_aeroplanes)

logger = logging.getLogger(__name__)


def user_interaction() -> None:
    """
    Основная функция для взаимодействия с пользователем через консоль.

    Возможности:
    1. Ввести название страны для запроса информации о самолетах
    2. Получить топ N самолетов по высоте полета
    3. Получить самолеты по стране их регистрации
    4. Фильтрация по диапазону высот
    5. Сохранение данных в JSON-файл
    """
    print("\n" + "=" * 80)
    print(" Добро пожаловать в систему анализа воздушного пространства!")
    print("=" * 80 + "\n")

    # Инициализация API и хранилища
    nominatim_api = NominatimAPI()
    opensky_api = OpenSkyAPI()
    json_saver = JSONSaver("aeroplanes.json")

    all_aeroplanes: List[Aeroplane] = []

    while True:
        print("\nВыберите действие:")
        print("1. Получить самолёты по стране")
        print("2. Показать топ N самолётов по высоте")
        print("3. Фильтровать самолёты по стране регистрации")
        print("4. Фильтровать самолёты по диапазону высот")
        print("5. Показать все загруженные самолёты")
        print("6. Сохранить текущие данные в файл")
        print("7. Загрузить данные из файла")
        print("0. Выход")

        choice = input("\nВаш выбор: ").strip()

        if choice == "0":
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

            # Добавляем в общий список
            all_aeroplanes.extend(aeroplanes)

            # Показываем первые 10
            print_aeroplanes(aeroplanes[:10], title=f"Первые 10 самолётов из '{country}'")

            # Сохраняем в хранилище
            json_saver.add_aeroplanes(aeroplanes)
            print(f"Данные сохранены в хранилище (всего: {json_saver.count()})")

        elif choice == "2":
            # Топ N по высоте
            if not all_aeroplanes:
                print("Нет загруженных данных. Сначала выполните действие 1 или 7")
                continue

            try:
                n = int(input(f"Введите количество самолётов для топа (1-{len(all_aeroplanes)}): ").strip())

                if n <= 0 or n > len(all_aeroplanes):
                    print(f"Число должно быть в диапазоне от 1 до {len(all_aeroplanes)}")
                    continue

                top_aeroplanes = get_top_aeroplanes(all_aeroplanes, n, by="altitude")
                print_aeroplanes(top_aeroplanes, title=f"Топ {n} самолётов по высоте")

            except ValueError:
                print("Некорректное число. Введите целое положительное число")

        elif choice == "3":
            # Фильтрация по стране
            if not all_aeroplanes:
                print("Нет загруженных данных. Сначала выполните действие 1 или 7")
                continue

            countries_input = input("Введите названия стран через запятую (например, Spain, Germany): ").strip()

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

        elif choice == "4":
            # Фильтрация по диапазону высот
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
                    print(f"Самолёты не найдены в диапазоне высот {min_alt}-{max_alt} м")
                    continue

                print_aeroplanes(filtered, title=f"Самолёты на высоте {min_alt}-{max_alt} м")

            except ValueError:
                print("Некорректный формат высот. Введите числа")

        elif choice == "5":
            # Показать все загруженные самолёты
            if not all_aeroplanes:
                print("Нет загруженных данных. Сначала выполните действие 1 или 7")
                continue

            print_aeroplanes(all_aeroplanes, title="Все загруженные самолёты")

        elif choice == "6":
            # Сохранить в файл
            if not all_aeroplanes:
                print("Нет данных для сохранения")
                continue

            json_saver.add_aeroplanes(all_aeroplanes)
            print(f"Данные сохранены в файл 'aeroplanes.json' (всего: {json_saver.count()})")

        elif choice == "7":
            # Загрузить из файла
            loaded = json_saver.get_all_aeroplanes()

            if not loaded:
                print("Файл пуст или не содержит данных")
                continue

            all_aeroplanes = loaded
            print(f"Загружено {len(loaded)} самолётов из файла")
            print_aeroplanes(all_aeroplanes[:10], title="Первые 10 загруженных самолётов")

        else:
            print("Некорректный выбор. Попробуйте снова")


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    user_interaction()
