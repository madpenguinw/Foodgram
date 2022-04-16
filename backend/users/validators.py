from django.core.exceptions import ValidationError

NOT_CORRECT_NAME = [
    'me',
    'login',
    'username',
]


def validate_username(value):
    if value in NOT_CORRECT_NAME:
        raise ValidationError(
            ('Данное имя пользователя не доступно.'),
            params={'value': value},
        )
