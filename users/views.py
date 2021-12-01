import json, bcrypt

from django.http            import JsonResponse
from django.views           import View
from django.core.exceptions import ValidationError

from users.models           import User
from users.validators       import UserValidator

class SignupView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            V = UserValidator()
            V.validate_name(name)
            V.validate_phone(phone)
            V.validate_email(email)
            V.validate_date_of_birth(date_of_birth)
            V.validate_password(password)
            V.validate_gender(gender)

            if User.objects.filter(email = data['email']).exists():
                return JsonResponse({'MESSAGE' : 'EMAIL_ALREADY_EXIST'}, status = 400)

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            User.objects.create(
                name          = data['name'],
                phone         = data['phone'],
                email         = data['email'],
                date_of_birth = data['date_of_birth'],
                password      = hashed_password,
                gender        = data['gender'],
                point         = data['point']
            )

            return JsonResponse({'MESSAGE' : 'CREATED'}, status = 201)

        except KeyError:
            return JsonResponse({'MESSAGE' : 'KEY_ERROR'}, status = 400)

        except ValidationError as e:
            return JsonResponse({'MESSAGE' : e.message}, status = 400)
