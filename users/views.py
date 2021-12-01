import json

import jwt, bcrypt
from django.views           import View
from django.http            import JsonResponse
from django.core.exceptions import ValidationError

from users.models     import User
from shops.models     import Cart
from users.validators import UserValidator
from my_settings      import SECRET_KEY, ALGORITHM

class UserCheckView(View):
    def post(self, request):
        try:
            data  = json.loads(request.body)

            email = data['email']

            UserValidator().validate_email(email)

            name = User.objects.get(email=email).name

            name = name[0] + '*'*(len(name)-1)

            result = {
                'email': email,
                'name' : name
            }

            return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': result}, status=200)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except ValidationError as e:
            return JsonResponse({'MESSAGE': e.message}, status=400)

        except User.DoesNotExist:
            result = {
                'email': email
            }
            return JsonResponse({'MESSAGE': 'USER_NOT_FOUND', 'RESULT': result}, status=400)


class SigninView(View):
    def post(self, request):
        try:
            data            = json.loads(request.body)

            email           = data['email']
            password        = data['password']

            user            = User.objects.get(email=email)
            user_id         = user.id
            hashed_password = user.password.encode('utf-8')

            if not bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return JsonResponse({'MESSAGE': 'LOGIN_FAILED'}, status=400)

            payload   = {
                'id': user_id
            }
            token     = jwt.encode(payload, SECRET_KEY, ALGORITHM)

            cart_list = Cart.objects.filter(
                user__id=user_id
            ).select_related(
                'product__category',
                'product'
            ).prefetch_related(
                'product__image_set',
                'product__tags'
            )

            results = [
                {
                    'product_id'    : cart_item.product.id,
                    'category_name' : cart_item.product.category.name,
                    'tags'          : list(map(
                        lambda x: x[0], cart_item.product.tags.values_list('name')
                    )),
                    'ml_volume'     : cart_item.product.category.ml_volume,
                    'price'         : cart_item.product.category.price,
                    'amount'        : cart_item.amount,
                    'thumb'         : cart_item.product.image_set.get(name='thumb').url
                }
                for cart_item in cart_list
            ]

            return JsonResponse({'MESSAGE': 'SUCCESS', 'TOKEN': token, 'RESULT': results}, status=200)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'MESSAGE': 'LOGIN_FAILED'}, status=400)

        except AttributeError:
            return JsonResponse({'MESSAGE': 'LOGIN_FAILED'}, status=400)
