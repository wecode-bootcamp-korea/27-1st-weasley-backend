import json

import jwt, bcrypt
from django.views           import View
from django.http            import JsonResponse
from django.core.exceptions import ValidationError

from users.models           import User, Address
from users.validators       import UserValidator
from my_settings            import SECRET_KEY, ALGORITHM
from core.utils             import authorization


class SignupView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            name           = data['name']
            phone          = data['phone']
            email          = data['email']
            date_of_birth  = data['date_of_birth']
            password       = data['password']
            gender         = data['gender']

            user_validator = UserValidator()
            user_validator.validate_name(name)
            user_validator.validate_phone(phone)
            user_validator.validate_email(email)
            user_validator.validate_date_of_birth(date_of_birth)
            user_validator.validate_password(password)
            user_validator.validate_gender(gender)

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            if User.objects.filter(email=email).exists():
                return JsonResponse({'MESSAGE' : 'EMAIL_ALREADY_EXIST'}, status = 400)

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'MESSAGE' : 'PHONE_ALREADY_EXIST'}, status = 400)

            user = User.objects.create(
                name          = name,
                phone         = phone,
                email         = email,
                date_of_birth = date_of_birth,
                password      = hashed_password,
                gender        = gender
            )

            access_token = jwt.encode({'id' : user.id}, SECRET_KEY, ALGORITHM)

            return JsonResponse({'MESSAGE' : 'CREATED', 'TOKEN' : access_token}, status = 201)

        except KeyError:
            return JsonResponse({'MESSAGE' : 'KEY_ERROR'}, status = 400)

        except ValidationError as e:
            return JsonResponse({'MESSAGE' : e.message}, status = 400)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)


class UserCheckView(View):
    def post(self, request):
        try:
            data  = json.loads(request.body)

            email = data['email']

            UserValidator().validate_email(email)

            mosaic_name = User.objects.get(email=email).mosaic_name

            result      = {
                'email': email,
                'name' : mosaic_name
            }

            return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': result}, status=200)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except ValidationError as e:
            return JsonResponse({'MESSAGE': e.message}, status=400)

        except User.DoesNotExist:
            result = {'email': email}
            return JsonResponse({'MESSAGE': 'USER_NOT_FOUND', 'RESULT': result}, status=400)


class SigninView(View):
    def post(self, request):
        try:
            data            = json.loads(request.body)

            email           = data['email']
            password        = data['password']

            user            = User.objects.get(email=email)
            hashed_password = user.password.encode('utf-8')

            if not bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return JsonResponse({'MESSAGE': 'LOGIN_FAILED'}, status=400)

            payload   = {'id': user.id}
            token     = jwt.encode(payload, SECRET_KEY, ALGORITHM)

            return JsonResponse({'MESSAGE': 'SUCCESS', 'TOKEN': token}, status=200)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'MESSAGE': 'LOGIN_FAILED'}, status=400)

        except AttributeError:
            return JsonResponse({'MESSAGE': 'LOGIN_FAILED'}, status=400)


class AddressView(View):
    @authorization
    def post(self, request, **kwargs):
        try:
            data = json.loads(request.body)

            user     = request.user

            location = data['location']

            UserValidator().validate_location(location)

            address, is_created = Address.objects.get_or_create(user=user, location=location)

            if is_created:
                return JsonResponse({'MESSAGE': 'CREATED'}, status=201)

            return JsonResponse({'MESSAGE': 'ADDRESS_ALREADY_EXIST'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

        except ValidationError as e:
            return JsonResponse({'MESSAGE': e.message}, status=400)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'BODY_REQUIRED'}, status=400)

    @authorization
    def get(self, request, **kwargs):
        user      = request.user

        addresses = Address.objects.filter(user=user)

        results   = [
            {
                'address_id' : address.id,
                'location'   : address.location,
            }
            for address in addresses
        ]

        return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': results}, status=200)
