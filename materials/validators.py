from rest_framework.serializers import ValidationError


class YoutubeUrlValidator:
    """Валидатор для проверки, что ссылка ведет на youtube.com."""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        url = value.get(self.field)

        if url:
            if "youtube.com" not in url.lower():
                raise ValidationError(
                    {self.field: "Разрешены ссылки только на youtube.com"}
                )
