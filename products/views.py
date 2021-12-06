import json

from django.core.exceptions import ValidationError
from django.http            import JsonResponse
from django.views           import View

from products.models        import Review, Product
from products.validators    import ProductValidator
from core.utils             import authorization

class ReviewView(View):
      @authorization
      def post(self, request):
          try:
              data = json.loads(request.body)

              user = request.user

              content    = data['content']
              star       = data['star']
              product_id = data['product_id']

              product_validator = ProductValidator()
              product_validator.validate_content(content)
              product_validator.validate_star(star)

              Review.objects.create(
                  content    = content,
                  star       = star,
                  product_id = product_id,
                  user       = user,
              )

              return JsonResponse({'MESSAGE' : 'CREATED'}, status=201)

          except ValidationError as e:
              return JsonResponse({'MESSAGE' : e.message}, status=400)

          except KeyError:
              return JsonResponse({'MESSAGE' : 'KEY_ERROR'}, status=400)

          except json.decoder.JSONDecodeError:
              return JsonResponse({'MESSAGE' : 'BODY_REQUIRED'}, status=400)
