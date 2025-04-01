import os
from csv import reader

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Команда для загрузки ингредиентов и тегов из CSV файлов в базу данных"""

    help = "Загружает начальные данные из CSV файлов в базу данных"

    DATA_CONFIG = {
        Ingredient: {
            "file": "ingredients.csv",
            "fields": {0: "name", 1: "measurement_unit"},
            "has_header": False,
        },
        Tag: {
            "file": "tags.csv",
            "fields": {0: "name", 1: "slug"},
            "has_header": False,
        }
    }

    def add_arguments(self, parser):
        """Добавляет опции для перезаписи существующих данных."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Полная очистка таблиц перед загрузкой данных"
        )

    def _get_file_path(self, filename):
        """Возвращает абсолютный путь к файлу данных."""
        return os.path.join(settings.BASE_DIR, "data", filename)

    def _validate_file(self, file_path):
        """Проверяет существование файла."""
        if not os.path.exists(file_path):
            raise FileNotFoundError("Файл %s не найден" % file_path)
        if not os.path.isfile(file_path):
            raise IsADirectoryError("%s является директорией" % file_path)

    def _load_model_data(self, model, config):
        """Загружает данные для конкретной модели."""
        file_path = self._get_file_path(config["file"])
        self.stdout.write(
            "Загрузка данных для %s из %s..." % (model.__name__, file_path)
        )

        try:
            self._validate_file(file_path)

            with open(file_path, "r", encoding="utf-8") as csv_file:
                csv_reader = reader(csv_file)

                if config["has_header"]:
                    next(csv_reader)

                objects = [
                    model(**{
                        model_field: row[col_index].strip()
                        for col_index, model_field in config["fields"].items()
                    })
                    for row in csv_reader
                ]

                model.objects.bulk_create(objects)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Успешно загружено %d записей для %s" %
                        (
                            len(objects), model.__name__
                        )
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                "Ошибка при загрузке %s: %s" % (model.__name__, str(e))
            ))

    @transaction.atomic
    def handle(self, *args, **options):
        """Основная логика выполнения команды."""
        if options["force"]:
            for model in self.DATA_CONFIG:
                model.objects.all().delete()
            self.stdout.write(
                self.style.WARNING("Все существующие данные удалены")
            )

        for model, config in self.DATA_CONFIG.items():
            self._load_model_data(model, config)
