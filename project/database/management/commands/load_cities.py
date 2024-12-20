import json
from django.core.management.base import BaseCommand
from database.models import Cities


class Command(BaseCommand):
    help = 'Загрузка городов из файла JSON'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Путь к файлу JSON")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            # Открытие JSON-файла
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Проверка формата данных
            if not isinstance(data, list):
                self.stdout.write(self.style.ERROR("JSON должен содержать список городов"))
                return

            # Загрузка данных в базу
            for item in data:
                city_name = item.get("Город")
                region_name = item.get("Регион")

                if not city_name or not region_name:
                    self.stdout.write(self.style.WARNING(f"Пропуск недопустимого элемента: {item}"))
                    continue

                Cities.objects.create(name=city_name, region=region_name)
                self.stdout.write(self.style.SUCCESS(f"Добавлен город: {city_name}, регион: {region_name}"))

            self.stdout.write(self.style.SUCCESS("Все города были успешно загружены."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл не найден: {file_path}"))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Неверный формат файла JSON"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Произошла ошибка: {e}"))