import json, datetime, uuid

import bcrypt
from django.views           import View
from django.http            import JsonResponse
from django.db.models       import Prefetch, F, Sum, Count, Q
from django.core.exceptions import ValidationError
from django.db              import IntegrityError, transaction, DatabaseError
from django.utils           import timezone

from shops.models           import Cart, Order, OrderItem, OrderStatus, OrderItemStatus, Subscribe
from products.models        import Image, Product
from users.models           import Address
from core.utils             import authorization
from shops.validators       import ShopValidator


class CartView(View):
    @authorization
    def get(self, request, **kwargs):
        user = request.user

        cart_list = Cart.objects.filter(
            user=user
        ).select_related(
            'product__category',
            'product'
        ).prefetch_related(
            Prefetch(
                'product__image_set',
                queryset=Image.objects.filter(
                    name='thumb'
                ),
                to_attr='thumb'
            ),
            'product__tags'
        )

        results = {
            "point": user.point,
            "cart_items": [
                {
                    'cart_id'       : cart_item.id,
                    'product_id'    : cart_item.product.id,
                    'category_name' : cart_item.product.category.name,
                    'tags'          : [tag.name for tag in cart_item.product.tags.all()],
                    'ml_volume'     : cart_item.product.category.ml_volume,
                    'price'         : cart_item.product.category.price,
                    'amount'        : cart_item.amount,
                    'thumb'         : cart_item.product.thumb[0].url
                }
                for cart_item in cart_list
            ]
        }

        return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': results}, status=200)

    @authorization
    def delete(self, request, **kwargs):
        try:
            cart_ids  = json.loads(request.GET.get('id', '[]'))

            if type(cart_ids) is not list or len(cart_ids)==0:
                return JsonResponse({'MESSAGE': 'INVALID_CART'}, status=400)

            user = request.user

            q    = Q()

            for cart_id in cart_ids:
                q.add(Q(id=cart_id), q.OR)

            cart_items = Cart.objects.filter(q, user=user)

            cart_items.delete()

            return JsonResponse({'MESSAGE': 'DELETED'}, status=200)

        except ValueError:
            return JsonResponse({'MESSAGE': 'INVALID_CART'}, status=400)

    @authorization
    def post(self, request, **kwargs):
        try:
            data           = json.loads(request.body)

            user           = request.user

            product_id     = data['product_id']
            amount         = data['amount']

            shop_validator = ShopValidator()
            shop_validator.validate_amount(amount)

            cart_item, is_created = Cart.objects.get_or_create(
                user       = user,
                product_id = product_id,
                defaults   = {'amount': amount}
            )

            if is_created:
                return JsonResponse({'MESSAGE': 'CREATED'}, status=201)

            amount    += cart_item.amount
            amount     = amount if not amount > shop_validator.AMOUNT_MAX_VALUE else 99

            cart_item.amount = amount
            cart_item.save()

            return JsonResponse({'MESSAGE': 'PATCHED'}, status=200)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except ValidationError as e:
            return JsonResponse({'MESSAGE': e.message}, status=400)

        except ValueError:
            return JsonResponse({'MESSAGE': 'INVALID_CART'}, status=400)

        except IntegrityError:
            return JsonResponse({'MESSAGE': 'INVALID_CART'}, status=400)

        except Cart.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_PRODUCT'}, status=400)

    @authorization
    def patch(self, request, **kwargs):
        try:
            data    = json.loads(request.body)

            user    = request.user

            cart_id = kwargs['cart_id']
            amount  = data['amount']

            ShopValidator().validate_amount(amount)

            cart_item = Cart.objects.get(id=cart_id, user=user)

            cart_item.amount = amount
            cart_item.save()

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except Cart.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_CART'}, status=400)

        except ValueError:
            return JsonResponse({'MESSAGE': 'INVALID_CART'}, status=400)

        except ValidationError as e:
            return JsonResponse({'MESSAGE': e.message}, status=400)


class AllOrderView(View):
    @authorization
    def get(self, request):
        user   = request.user

        orders = Order.objects.filter(user=user).select_related(
            'order_status'
        ).prefetch_related(
            'orderitem_set',
            Prefetch(
                'orderitem_set__product__image_set',
                queryset = Image.objects.filter(name='thumb'),
                to_attr  = 'thumb'
            ),
            'orderitem_set__product__category'
         ).annotate(order_items_count=Count('orderitem'))

        results = [
            {
                'order_id'          : order.id,
                'order_status'      : order.order_status.status,
                'ordered_at'        : datetime.datetime.date(order.created_at),
                'thumb'             : order.orderitem_set.all()[0].product.thumb[0].url,
                'order_number'      : order.order_number,
                'order_items_count' : order.order_items_count,
                'category_name'     : order.orderitem_set.all()[0].product.category.name,
            }
            for order in orders
        ]

        return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': results}, status=200)


class OrderView(View):
    @authorization
    def post(self, request, **kwargs):
        try:
            data       = json.loads(request.body)

            user       = request.user

            address    = Address.objects.get(user=user, id=data['address_id'])

            cart_list  = Cart.objects.filter(
                user = user
            ).select_related(
                'product',
                'product__category'
            ).annotate(
                price = Sum(F('amount')*F('product__category__price'))
            )

            total_price  = cart_list.aggregate(
                total_price=Sum('price')
            )['total_price']

            if user.point < total_price:
                return JsonResponse({'MESSAGE': 'POINT_TOO_SMALL'}, status=400)

            with transaction.atomic():
                order = Order(
                    user            = user,
                    address         = address,
                    order_number    = uuid.uuid4(),
                    order_status_id = OrderStatus.Status.UNDONE
                )

                order_items = [
                    OrderItem(
                        product              = cart_item.product,
                        order_item_status_id = OrderItemStatus.Status.PRESHIPPIN,
                        amount               = cart_item.amount,
                        order                = order
                    )
                    for cart_item in cart_list
                ]

                user.point -= total_price
                user.save()

                cart_list.delete()

                order.order_status_id = OrderStatus.Status.DONE
                order.save()

                OrderItem.objects.bulk_create(order_items)

                return JsonResponse({'MESSAGE': 'CREATED'}, status=201)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except Address.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_ADDRESS'}, status=400)

        except AttributeError:
            return JsonResponse({'MESSAGE': 'INVALID_ADDRESS'}, status=400)

        except DatabaseError:
            return JsonResponse({'MESSAGE': 'DATABASE_ERROR'}, status=400)

    @authorization
    def get(self, request, **kwargs):
        try:
            user     = request.user

            order_id = kwargs['order_id']

            order    = Order.objects.select_related(
                'address'
            ).prefetch_related(
                'orderitem_set',
                'orderitem_set__product',
                'orderitem_set__product__category',
                'orderitem_set__product__tags',
                Prefetch(
                    'orderitem_set__product__image_set',
                    queryset = Image.objects.filter(name='thumb'),
                    to_attr  = 'thumb'
                )
            ).get(id=order_id, user=user)

            results = {
                'name'        : user.name,
                'address'     : order.address.location if order.address else '배송지 정보가 없습니다.',
                'phone'       : user.phone,
                'order_items' : [
                    {
                        'category_name'     : order_item.product.category.name,
                        'amount'            : order_item.amount,
                        'ml_volume'         : order_item.product.category.ml_volume,
                        'thumb'             : order_item.product.thumb[0].url,
                        'tags'              : [tag.name for tag in order_item.product.tags.all()],
                        'order_item_status' : order_item.order_item_status.status,
                        'shipping_company'  : order_item.shipping_company.name if order_item.shipping_company else '배송 업체 정보가 없습니다.',
                        'shipping_number'   : order_item.shipping_number
                    }
                    for order_item in order.orderitem_set.all()
                ]
            }

            return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': results}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except Order.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_ORDER'}, status=400)


class SubscribeView(View):
    @authorization
    def post(self, request):
        try:
            data                   = json.loads(request.body)
            user                   = request.user
            subscribes             = Subscribe.objects.filter(user=user)

            if not subscribes.exists():
                interval           = 8
                next_purchase_date = timezone.now().date() + datetime.timedelta(days=1)

            else:
                interval           = subscribes[0].interval
                next_purchase_date = subscribes[0].next_purchase_date

            product_id             = data['product_id']
            amount                 = data['amount']
            address_id             = data['address_id']

            shop_validator         = ShopValidator()
            shop_validator.validate_amount(amount)

            if not Address.objects.filter(user=user, id=address_id).exists():
                return JsonResponse({'MESSAGE': 'INVALID_ADDRESS'}, status=400)

            if not Product.objects.filter(id=product_id).exists():
                return JsonResponse({'MESSAGE': 'INVALID_PRODUCT'}, status=400)

            if Subscribe.objects.filter(user=user, product_id=product_id).exists():
                return JsonResponse({'MESSAGE': 'SUBSCRIBE_ALREADY_EXIST'}, status=400)

            Subscribe.objects.create(
                user                 = user,
                address_id           = address_id,
                product_id           = product_id,
                amount               = amount,
                interval             = interval,
                next_purchase_date   = next_purchase_date
            )

            return JsonResponse({'MESSAGE': 'CREATED'}, status=201)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except ValidationError as e:
            return JsonResponse({'MESSAGE': e.message}, status=400)

        except IndexError:
            return JsonResponse({'MESSAGE': 'ADDRESS_NOT_FOUND'}, status=400)

        except AttributeError:
            return JsonResponse({'MESSAGE': 'INVALID_ADDRESS'}, status=400)

    @authorization
    def get(self, request, **kwargs):
        user       = request.user

        subscribes = list(Subscribe.objects.select_related('address', 'product', 'product__category').prefetch_related(
            Prefetch('product__image_set', queryset=Image.objects.filter(name='thumb'), to_attr='thumb')
        ).filter(user=user))

        results = [
            {
                'user_name'          : user.name,
                'address'            : subscribe.address.location,
                'next_purchase_date' : subscribe.next_purchase_date,
                'next_ship_date'     : subscribe.next_purchase_date + datetime.timedelta(days=7*subscribe.interval),
                'interval'           : subscribe.interval,
                'category_name'      : subscribe.product.category.name,
                'product_id'         : subscribe.product.id,
                'thumb'              : subscribe.product.thumb[0].url
            }
            for subscribe in subscribes
        ]

        return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': results}, status=200)

    @authorization
    def patch(self, request):
        try:
            data                              = json.loads(request.body)
            user                              = request.user

            interval                          = data['interval']
            subscribes                        = Subscribe.objects.filter(user=user)

            if not subscribes.exists():
                return JsonResponse({'MESSAGE': 'INVALID_SUBSCRIBE'}, status=400)

            if interval not in [4, 12, 16]:
                return JsonResponse({'MESSAGE': 'INVALID_INTERVAL'}, status=400)

            subscribes.update(interval=interval)

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except ValidationError as e:
            return JsonResponse({'MESSAGE': e.message}, status=400)
          
    def delete(self, request, **kwargs):
        try:
            user = request.user

            subscribe_ids = json.loads(request.GET.get('id', '[]'))

            subscribe_list = Subscribe.objects.filter(user=user, id__in=subscribe_ids)

            if not subscribe_list.exists():
                return JsonResponse({'MESSAGE': 'INVALID_SUBSCRIPTION'}, status=400)

            subscribe_list.delete()


            return JsonResponse({"MESSAGE": "DELETED"}, status=200)

        except ValueError:
            return JsonResponse({"MESSAGE": "INVALID_SUBSCRIPTION"},status=400)

        except KeyError:
            return JsonResponse({"MESSAGE": "KEY_ERROR"}, status=400)

        except TypeError:
            return JsonResponse({"MESSAGE": "TYPE_ERROR"}, status=400)
