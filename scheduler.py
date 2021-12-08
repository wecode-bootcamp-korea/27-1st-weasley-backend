import os, uuid, datetime, schedule, time
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weasley.settings')
django.setup()

from django.utils     import timezone
from django.db        import IntegrityError, DatabaseError, transaction
from django.db.models import Sum, F

from shops.models     import Subscribe, Order, OrderStatus, OrderItem, OrderItemStatus

def subcribe_check():
    now = timezone.now().date()
    Subscribe.objects.filter(next_purchase_date__lt=now).delete()
    subscribes = list(Subscribe.objects.select_related('product').filter(next_purchase_date=now))

    for subscribe in subscribes:
        print(subscribe)



schedule.every(10).seconds.do(subcribe_check)

while True:
    schedule.run_pending()
    time.sleep(1)
