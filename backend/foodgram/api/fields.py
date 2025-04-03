import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Превращаем картинку из запроса в картинку-файл."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            file_format, image = data.split(";base64,")
            file_extension = file_format.split("/")[1]
            data = ContentFile(
                base64.b64decode(image),
                name=f"{uuid.uuid4()}.{file_extension}",
            )
        return super().to_internal_value(data)
