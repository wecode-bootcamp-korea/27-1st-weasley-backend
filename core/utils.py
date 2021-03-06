import jwt
from django.http  import JsonResponse

from users.models import User
from my_settings  import SECRET_KEY, ALGORITHM

def authorization(func):

    def wrapper(self, request, *args, **kwargs):
        try:
            bearer_token = request.headers.get('Authorization')

            if not bearer_token:
                return JsonResponse({'MESSAGE': 'TOKEN_REQUIRED'}, status=401)

            if type(bearer_token) is not str:
                return JsonResponse({'MESSAGE': 'TOKEN_MUST_BE_STR'}, status=401)

            bearer_token = bearer_token.split()

            if bearer_token[0] != 'Bearer':
                return JsonResponse({'MESSAGE': 'TOKEN_MUST_BE_BEARER'}, status=401)

            token        = bearer_token[1]

            payload      = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            user         = User.objects.get(id=payload['id'])

            request.user = user

            return func(self, request, *args, **kwargs)

        except IndexError:
            return JsonResponse({'MESSAGE': 'TOKEN_MUST_BE_BEARER'}, status=401)

        except jwt.exceptions.InvalidAlgorithmError:
            return JsonResponse({'MESSAGE': 'INVALID_TOKEN'}, status=401)

        except jwt.exceptions.InvalidSignatureError:
            return JsonResponse({'MESSAGE': 'INVALID_TOKEN'}, status=401)

        except jwt.exceptions.DecodeError:
            return JsonResponse({'MESSAGE': 'INVALID_TOKEN'}, status=401)

        except KeyError:
            return JsonResponse({'MESSAGE': 'INVALID_TOKEN'}, status=401)

        except User.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_TOKEN'}, status=401)

    return wrapper
