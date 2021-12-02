import datetime

from django.core.validators import EmailValidator, RegexValidator
from django.utils           import timezone
from django.core.exceptions import ValidationError

class UserValidator:
    NAME_REGEX     = '^[가-힣]{1,15}$'
    PHONE_REGEX    = '^01([016789])([0-9]{3,4})([0-9]{4})$'
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

    def validate_name(self, name):
        if type(name) is not str:
            raise ValidationError('NAME_MUST_BE_STR')

        name = name.replace(' ', '')

        if len(name) < self.NAME_MIN_LENGTH:
            raise ValidationError('NAME_TOO_SHORT')

        if len(name) > self.NAME_MAX_LENGTH:
            raise ValidationError('NAME_TOO_LONG')

        RegexValidator(regex=self.NAME_REGEX, message='INVALID_NAME')(name)

    def validate_phone(self, phone):
        if type(phone) is not str:
            raise ValidationError('PHONE_MUST_BE_STR')

        phone.replace(' ', '')

        RegexValidator(regex=self.PHONE_REGEX, message='INVALID_PHONE')(phone)

    def validate_email(self, email):
        if type(email) is not str:
            raise ValidationError('EMAIL_MUST_BE_STR')

        email = email.replace(' ', '')

        if len(email) > self.EMAIL_MAX_LENGTH:
            raise ValidationError('EMAIL_TOO_LONG')

        EmailValidator(message='INVALID_EMAIL')(email)

    def validate_date_of_birth(self, date_of_birth):
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

            if date_of_birth <= timezone.now().date() - datetime.timedelta(days=365*self.DATE_OF_BIRTH_MIN_VALUE):
                raise ValidationError('DATE_OF_BIRTH_TOO_SMALL')

        except ValueError:
            raise ValidationError('INVALID_DATE_OF_BIRTH')

    def validate_password(self, password):
        if type(password) is not str:
            raise ValidationError('PASSWORD_MUST_BE_STR')

        password = password.replace(' ', '')

        if len(password) < self.PASSWORD_MIN_LENGTH:
            raise ValidationError('PASSWORD_TOO_SHORT')

        if len(password) > self.PASSWORD_MAX_LENGTH:
            raise ValidationError('PASSWORD_TOO_LONG')

        RegexValidator(regex=self.PASSWORD_REGEX, message='INVALID_PASSWORD')(password)

    def validate_gender(self, gender):
        if type(gender) is not str:
            raise ValidationError('GENDER_MUST_BE_STR')

        if gender not in self.GENDER_LIST:
            raise ValidationError('INVALID_GENDER')

    def validate_location(self, location):
        if type(location) is not str:
            raise ValidationError('LOCATION_MUST_BE_STR')

        location = location.strip()

        if len(location) < self.LOCATION_MIN_LENGTH:
            raise ValidationError('LOCATION_TOO_SHORT')

        if len(location) > self.LOCATION_MAX_LENGTH:
            raise ValidationError('LOCATION_TOO_LONG')
