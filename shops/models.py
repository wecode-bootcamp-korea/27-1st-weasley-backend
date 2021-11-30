from django.db   import models

from core.models import TimeStampModel


class ShippingCompany(models.Model):
    name = models.CharField(max_length=20)


    class Meta:
        db_table = 'shipping_companies'


class OrderItemStatus(models.Model):
    status = models.CharField(max_length=10)


    class Meta:
        db_table = 'order_item_status'


class OrderStatus(models.Model):
    status = models.CharField(max_length=10)


    class Meta:
        db_table = 'order_status'


class Cart(TimeStampModel):
    user    = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    amount  = models.PositiveSmallIntegerField()


    class Meta:
        db_table = 'carts'


class OrderItem(models.Model):
    product           = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    shipping_company  = models.ForeignKey('ShippingCompany', on_delete=models.SET_NULL, null=True)
    order_item_status = models.ForeignKey('OrderItemStatus', on_delete=models.CASCADE)
    order             = models.ForeignKey('Order', on_delete=models.CASCADE)
    amount            = models.PositiveSmallIntegerField()
    shipping_number   = models.CharField(max_length=100, blank=True, default='')


    class Meta:
        db_table = 'order_items'


    def __str__(self):
        return self.shipping_number


class Order(TimeStampModel):
    user         = models.ForeignKey('users.User', on_delete=models.CASCADE)
    address      = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length = 150, unique=True)
    order_status = models.ForeignKey('OrderStatus', on_delete=models.CASCADE)


    class Meta:
        db_table = 'orders'


    def __str__(self):
        return self.order_number


class Subscribe(TimeStampModel):
    user               = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product            = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    address            = models.ForeignKey('users.Address', on_delete=models.CASCADE)
    amount             = models.PositiveSmallIntegerField()
    interval           = models.PositiveSmallIntegerField()
    next_purchase_date = models.DateField()


    class Meta:
        db_table = 'subscribes'
