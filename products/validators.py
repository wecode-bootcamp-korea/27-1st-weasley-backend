from django.core.exceptions import ValidationError

class ProductValidator:
    CONTENT_MIN_LENGTH = 1
    CONTENT_MAX_LENGTH = 1000
    STAR_MIN_LENGTH    = 1
    STAR_MAX_LENGTH    = 5

    def validate_content(self, content):
        if type(content) is not str:
            raise ValidationError('CONTENT_MUST_BE_STR')

        if len(content) < self.CONTENT_MIN_LENGTH:
            raise ValidationError('CONTENT_TOO_SHORT')

        if len(content) > self.CONTENT_MAX_LENGTH:
            raise ValidationError('CONTENT_TOO_LONG')
            
    def validate_star(self, star):
        if int(star) < self.STAR_MIN_LENGTH:
            raise ValidationError('STAR_TOO_SMALL')

        if int(star) > self.STAR_MAX_LENGTH:
            raise ValidationError('STAR_TOO_BIG')