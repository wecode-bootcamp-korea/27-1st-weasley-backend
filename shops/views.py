import json, datetime

import bcrypt
from django.views           import View
from django.http            import JsonResponse
from django.db.models       import Prefetch, F, Sum
from django.core.exceptions import ValidationError
from django.db              import IntegrityError

from shops.models           import Cart, Order, OrderItem
from products.models        import Image, Product
from core.utils             import authorization
from shops.validators       import ShopValidator
from users.models           import Address

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


class OrderView(View):
    @authorization
    def post(self, request, **kwargs):
        try:
            data       = json.loads(request.body)

            user       = request.user
            user_point = user.point

            address_id = data['address_id']
            address    = Address.objects.get(id=address_id)

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

            if user_point < total_price:
                return JsonResponse({'MESSAGE': 'POINT_TOO_SMALL'}, status=400)

            order_number = bcrypt.gensalt().decode('utf-8')

            while Order.objects.filter(order_number=order_number).exists():
                order_number = bcrypt.gensalt().decode('utf-8')

            order = Order(
                user            = user,
                address         = address,
                order_number    = order_number,
                order_status_id = 1
            )

            order_items = [
                OrderItem(
                    product              = cart_item.product,
                    order_item_status_id = 1,
                    amount               = cart_item.amount,
                    order                = order
                )
                for cart_item in cart_list
            ]

            order.save()
            OrderItem.objects.bulk_create(order_items)

            user.point -= total_price
            user.save()

            order.order_status_id = 2
            order.save()

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

        except Address.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_ADDRESS'}, status=400)

        except AttributeError:
            return JsonResponse({'MESSAGE': 'INVALID_ADDRESS'}, status=400)
