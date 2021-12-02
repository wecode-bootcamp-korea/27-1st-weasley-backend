import json

import jwt, bcrypt
from django.views           import View
from django.http            import JsonResponse
from django.core.exceptions import ValidationError

from users.models     import User
from users.validators import UserValidator
from my_settings      import SECRET_KEY, ALGORITHM


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