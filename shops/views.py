import json, datetime

from django.views           import View
from django.http            import JsonResponse
from django.db.models       import Prefetch, Count
from django.core.exceptions import ValidationError
from django.db              import IntegrityError

from shops.models           import Cart, Order
from products.models        import Image, Product
from core.utils             import authorization
from shops.validators       import ShopValidator


class CartView(View):
    @authorization
    def get(self, request, **kwargs):
        user = request.user

        cart_list = Cart.objects.filter(
            user__id=user.id
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

        results = [
            {
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

        return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': results}, status=200)

    @authorization
    def delete(self, request, **kwargs):
        try:
            product_id = kwargs['product_id']
            user       = request.user

            cart_item  = Cart.objects.get(user=user, product_id=product_id)
            cart_item.delete()

            return JsonResponse({'MESSAGE': 'DELETED'}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'PARAM_REQUIRED'}, status=400)

        except Cart.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_PRODUCT'}, status=400)

        except ValueError:
            return JsonResponse({'MESSAGE': 'INVALID_PRODUCT'}, status=400)

    @authorization
    def post(self, request):
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
            return JsonResponse({'MESSAGE': 'INVALID_PRODUCT'}, status=400)

        except IntegrityError:
            return JsonResponse({'MESSAGE': 'INVALID_PRODUCT'}, status=400)

        except Cart.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_PRODUCT'}, status=400)


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
                'address'     : order.address.location\
                    if order.address else '배송지 정보가 없습니다.',
                'phone'       : user.phone,
                'order_items' : [
                    {
                        'category_name'     : order_item.product.category.name,
                        'amount'            : order_item.amount,
                        'ml_volume'         : order_item.product.category.ml_volume,
                        'thumb'             : order_item.product.thumb[0].url,
                        'tags'              : [
                            tag.name
                            for tag in order_item.product.tags.all()
                        ],
                        'order_item_status' : order_item.order_item_status.status,
                        'shipping_company'  : order_item.shipping_company.name\
                            if order_item.shipping_company else '배송 업체 정보가 없습니다.',
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
