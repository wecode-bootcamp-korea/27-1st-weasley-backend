import json

from django.views           import View
from django.http            import JsonResponse
from django.db.models       import Prefetch, Sum, F
from django.core.exceptions import ValidationError
from django.db              import IntegrityError

from shops.models           import Cart
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
            cart_id = kwargs['cart_id']
            user       = request.user

            cart_item  = Cart.objects.get(user=user, id=cart_id)
            cart_item.delete()

            return JsonResponse({'MESSAGE': 'DELETED'}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'PARAM_REQUIRED'}, status=400)

        except Cart.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_CART'}, status=400)

        except ValueError:
            return JsonResponse({'MESSAGE': 'INVALID_CART'}, status=400)

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
