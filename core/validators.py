import datetime

from django.core.validators import EmailValidator, RegexValidator
from django.utils           import timezone
from django.core.exceptions import ValidationError

NAME_REGEX     = '^[가-힣]{1,15}$'
PHONE_REGEX    = '^01([0|1|6|7|8|9])([0-9](3,4))([0-9]{4})$'
PASSWORD_REGEX = '''^.*(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!"#$%&'()*+,\-./:;<=>?@[＼\]^_`{|}~\\)])[\w!"#$%&'()*+,\-./:;<=>?@[＼\]^`{|}~\\)]{8,45}$'''

NAME_MIN_LENGTH         = 1
NAME_MAX_LENGTH         = 15
EMAIL_MAX_LENGTH        = 150
DATE_OF_BIRTH_MIN_VALUE = 200
GENDER_LIST             = ['MALE', 'FEMALE']
PASSWORD_MIN_LENGTH     = 8
PASSWORD_MAX_LENGTH     = 45
LOCATION_MIN_LENGTH     = 1
LOCATION_MAX_LENGTH     = 200
AMOUNT_MIN_VALUE        = 1
AMOUNT_MAX_VALUE        = 99
CONTENT_MIN_LENGTH      = 1
CONTENT_MAX_LENGTH      = 1000

def validate_name(name):
    if type(name) is not str:
        raise ValidationError('NAME_MUST_BE_STR')

    name = name.replace(' ', '')

    if len(name) < NAME_MIN_LENGTH:
        raise ValidationError('NAME_TOO_SHORT')

    if len(name) > NAME_MAX_LENGTH:
        raise ValidationError('NAME_TOO_LONG')

    RegexValidator(regex=NAME_REGEX, message='INVALID_NAME')(name)

def validate_phone(phone):
    if type(phone) is not str:
        raise ValidationError('PHONE_MUST_BE_STR')

    phone.replace(' ', '')

    RegexValidator(regex=PHONE_REGEX, message='INVALID_PHONE')(phone)

def validate_email(email):
    if type(email) is not str:
        raise ValidationError('EMAIL_MUST_BE_STR')

    email = email.replace(' ', '')

    if len(email) > EMAIL_MAX_LENGTH:
        raise ValidationError('EMAIL_TOO_LONG')

    EmailValidator(message='INVALID_EMAIL')(email)

def validate_date_of_birth(date_of_birth):
    try:
        if type(date_of_birth) is not str:
            raise ValidationError('DATE_OF_BIRTH_MUST_BE_STR')

        date_of_birth = date_of_birth.replace(' ', '')

        date_of_birth = list(map(int, date_of_birth.split('-')))

        if len(date_of_birth) != 3:
            raise ValidationError('INVALID_DATE_OF_BIRTH')

        date_of_birth = datetime.date(*date_of_birth)

        if date_of_birth >= timezone.now().date():
            raise ValidationError('DATE_OF_BIRTH_TOO_BIG')

        if date_of_birth <= timezone.now().date() - datetime.timedelta(days=365*DATE_OF_BIRTH_MIN_VALUE):
            raise ValidationError('DATE_OF_BIRTH_TOO_SMALL')

    except ValueError:
        raise ValidationError('INVALID_DATE_OF_BIRTH')

def validate_password(password):
    if type(password) is not str:
        raise ValidationError('PASSWORD_MUST_BE_STR')

    password = password.replace(' ', '')

    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValidationError('PASSWORD_TOO_SHORT')

    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValidationError('PASSWORD_TOO_LONG')

    RegexValidator(regex=PASSWORD_REGEX, message='INVALID_PASSWORD')(password)

def validate_gender(gender):
    if type(gender) is not str:
        raise ValidationError('GENDER_MUST_BE_STR')

    if gender not in GENDER_LIST:
        raise ValidationError('INVALID_GENDER')

def validate_location(location):
    if type(location) is not str:
        raise ValidationError('LOCATION_MUST_BE_STR')

    location = location.strip()

    if len(location) < LOCATION_MIN_LENGTH:
        raise ValidationError('LOCATION_TOO_SHORT')

    if len(location) > LOCATION_MAX_LENGTH:
        raise ValidationError('LOCATION_TOO_LONG')

def validate_amount(amount):
    if type(amount) is not int:
        raise ValidationError('AMOUNT_MUST_BE_INT')

    if amount < AMOUNT_MIN_VALUE:
        raise ValidationError('AMOUNT_TOO_SMALL')

    if amount > AMOUNT_MAX_VALUE:
        raise ValidationError('AMOUNT_TOO_BIG')

def validate_content(content):
    if type(content) is not str:
        raise ValidationError('CONTENT_MUST_BE_STR')

    if len(content) < CONTENT_MIN_LENGTH:
        raise ValidationError('CONTENT_TOO_SHORT')

    if len(content) > CONTENT_MAX_LENGTH:
        raise ValidationError('CONTENT_TOO_LONG')
