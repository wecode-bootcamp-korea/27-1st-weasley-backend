import os, uuid, datetime, schedule, time
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weasley.settings')
django.setup()

from django.utils     import timezone
from django.db        import IntegrityError, DatabaseError, transaction
from django.db.models import Sum, F

from users.models     import User
from shops.models     import Subscribe, Order, OrderStatus, OrderItem, OrderItemStatus

def subcribe_check():
    now = timezone.now().date()
    print(timezone.now())
    Subscribe.objects.filter(next_purchase_date__lt=now).delete()
    subscribe_users = Subscribe.objects.filter(next_purchase_date=now)\
        .values('user_id').annotate(total_price=Sum(F('product__category__price')*F('amount')))

    for subscribe_user in subscribe_users:
        with transaction.atomic():
            user = User.objects.get(id=subscribe_user['user_id'])

            subscribes = Subscribe.objects.filter(user=user, next_purchase_date=now)\
                .select_related('product', 'product__category', 'address')

            if subscribe_user['total_price'] <= user.point:
                order = Order(
                    user            = user,
                    address         = subscribes[0].address,
                    order_number    = uuid.uuid4(),
                    order_status_id = OrderStatus.Status.UNDONE
                )

                order_items = [
                    OrderItem(
                        product              = subscribe.product,
                        order_item_status_id = OrderItemStatus.Status.PRESHIPPIN,
                        amount               = subscribe.amount,
                        order                = order
                    )
                    for subscribe in subscribes
                ]

                user.point -= subscribe_user['total_price']
                user.save()

                order.order_status_id = OrderStatus.Status.DONE
                order.save()

                OrderItem.objects.bulk_create(order_items)

            interval = subscribes[0].interval
            subscribes.update(next_purchase_date=F('next_purchase_date')+datetime.timedelta(weeks=interval))



schedule.every().hours.at("00:00").do(subcribe_check)

while True:
    schedule.run_pending()
    time.sleep(1)
