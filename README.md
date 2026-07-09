# Проект Сбор данных о воздушных судах в воздушном пространстве

## Описание:

Сбор данных о воздушных судах в воздушном пространстве

## Установка:

1. Клонируйте репозиторий:
```
git clone 
```
2. Установите зависимости:
```
На данный момент появилась библиотека requests и python-dotenv также в пректе теперь участвует библиотека os, dadataim, json, logging.
А такж используются линтер, статический анализатор и форматер кода. 
Для обработки и анализа данных в формате Excel я импртирокал библиотеку pandas.
А для чтения формата xlsx нужно в прект установить ещё и openpyxl.
Поскольку проект прошёл тестирование через pytest, у него есть зависимости — именно эти инструменты. Они указаны в файле pyproject.toml. 
А также теперьв тестирование участвует Mock и patch. На даный момет всё.
Если у вас они отсутствуют, вы можете установить их с помощью команд, приведённых ниже.
1. flake8 
poetry add --group lint flake8
2. mypy
poetry add --group lint mypy
3. black
poetry add --group lint black
4. isort
poetry add --group lint isort
5. requests
poetry add requests
6. pandas
poetry add pandas
7. openpyxl
poetry add openpyxl
8. python-dotenv
poetry add python-dotenv
9. pytest
poetry add --group dev pytest
Code coverage в
Code coverage в библиотеку pytest
poetry add --group dev pytest-cov

```
Более подробные настройки линтеров можно узнать тут, а также тесты, которые прошли функции можно узнать тут же [документации](docs/README.md).

## Использование:



## Документация:

Для получения дополнительной информации обратитесь к [документации](docs/README.md).

## Лицензия:

Этот проект лицензирован по [лицензии MIT](LICENSE).