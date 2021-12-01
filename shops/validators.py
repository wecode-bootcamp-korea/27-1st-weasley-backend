from django.core.exceptions import ValidationError

class ShopValidator:
    AMOUNT_MIN_VALUE = 1
    AMOUNT_MAX_VALUE = 99

    def validate_amount(self, amount):
        if type(amount) is not int:
            raise ValidationError('AMOUNT_MUST_BE_INT')

        if amount < self.AMOUNT_MIN_VALUE:
            raise ValidationError('AMOUNT_TOO_SMALL')

        if amount > self.AMOUNT_MAX_VALUE:
            raise ValidationError('AMOUNT_TOO_BIG')
