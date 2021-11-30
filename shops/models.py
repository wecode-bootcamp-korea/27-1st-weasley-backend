from django.db   import models

from core.models import TimeStampModel


class Cart(TimeStampModel):
    user    = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    amount  = models.PositiveSmallIntegerField()


    class Meta:
        db_table = 'carts'


class Order(TimeStampModel):
    user    = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    address = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True)
    amount  = models.PositiveSmallIntegerField()


    class Meta:
        db_table = 'orders'


class Subscribe(TimeStampModel):
    user               = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product            = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    address            = models.ForeignKey('users.Address', on_delete=models.CASCADE)
    amount             = models.PositiveSmallIntegerField()
    interval           = models.PositiveSmallIntegerField()
    next_purchase_date = models.DateField()


    class Meta:
        db_table = 'subscribes'
