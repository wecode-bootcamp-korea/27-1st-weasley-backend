from django.db   import models

from core.models import TimeStampModel


class User(TimeStampModel):
    name          = models.CharField(max_length=15)
    phone         = models.CharField(max_length=11, unique=True)
    email         = models.CharField(max_length=500, unique=True)
    date_of_birth = models.DateField()
    password      = models.CharField(max_length=200)
    gender        = models.CharField(max_length=6)
    point         = models.PositiveIntegerField()


    class Meta:
        db_table = 'users'


    def __str__(self):
        return self.name


class Address(models.Model):
    user     = models.ForeignKey('User', on_delete=models.CASCADE)
    location = models.CharField(max_length=200)


    class Meta:
        db_table = 'addresses'


    def __str__(self):
        return self.location
