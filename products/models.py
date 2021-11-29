from django.db   import models

from core.models import TimeStampModel


class Category(models.Model):
    name      = models.CharField(max_length=10)
    ml_volume = models.PositiveIntegerField()
    price     = models.PositiveIntegerField()


    class Meta:
        db_table = 'categories'


    def __str__(self):
        return self.name


class Product(models.Model):
    category   = models.ForeignKey('Category', on_delete=models.CASCADE)
    outer_name = models.CharField(max_length=50)
    inner_name = models.CharField(max_length=50)


    class Meta:
        db_table = 'products'


    def __str__(self):
        return self.inner_name


class Review(TimeStampModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    user    = models.ForeignKey('users.User', on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
    star    = models.PositiveSmallIntegerField()


    class Meta:
        db_table = 'reviews'


    def __str__(self):
        return self.content


class Price(models.Model):
    product             = models.ForeignKey('Product', on_delete=models.CASCADE)
    manufacturing_cost  = models.PositiveIntegerField()
    transportation_cost = models.PositiveIntegerField()
    development_cost    = models.PositiveIntegerField()
    commision_cost      = models.PositiveIntegerField()
    other_market_price  = models.PositiveIntegerField()


    class Meta:
        db_table = 'prices'


class Image(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    name    = models.CharField(max_length=20)
    url     = models.CharField(max_length=1000)


    class Meta:
        db_table = 'images'


    def __str__(self):
        return self.name
