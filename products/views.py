import json

from django.core.exceptions import ValidationError
from django.http            import JsonResponse
from django.views           import View
from django.db.models       import Avg, F

from products.models        import Category, Product, Review, Price
from products.validators    import ProductValidator
from core.utils             import authorization


class CategoriesView(View):
    def get(self, request):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 5))

        categories = [{
            'name'        : category.name,
            'ml_volume'   : category.ml_volume,
            'price'       : category.price,
            'products'    : [{
                'thumb' : product.image_set.get(name='thumb').url,
                'tags'  : [tag.name for tag in product.tags.all()],
                'id'    : product.id
            } for product in category.product_set.all()]
        } for category in Category.objects.all()[offset:offset+limit]]

        return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': categories}, status=200) 

class ProductView(View):
      def get(self, request, **kwargs):

        product = Product.objects.get(id=kwargs['product_id'])
        category_id = product.category.id
        price = product.price_set.get()
        review = [
            *product.category.product_set.filter(review__isnull=False).annotate(
                content=F('review__content'),
                star=F('review__star'),
                date=F('review__created_at'),
                user_name=F('review__user__name')
            ).values(
                'id', 'content', 'star', 'date', 'user_name'
            )
        ]

        results = {
            'product_id': product.id,
            'ml_volume': product.category.ml_volume,
            'images': [{
                image.name: image.url
            } for image in product.image_set.all()],
            'name': product.name,
            'category_price': product.category.price,
            'tags': [tag.name for tag in product.tags.all()],
            'average_star': float('%.1f' %(sum(map(lambda x: x['star'], review)) / len(review))) if len(review) != 0 else 0,
            'review': review,
            'price': {
                'manufacturing_cost': price.manufacturing_cost,
                'transportation_cost': price.transportation_cost,
                'development_cost': price.development_cost,
                'commision_cost': price.commision_cost,
                'other_market_price': price.other_market_price,
            },
            'product_set': [
                {
                    'id': product.id,
                    'tags': [tag.name for tag in product.tags.all()]
                }
                for product in product.category.product_set.all()
            ]

        }

        return JsonResponse({'RESULT' : results, 'MESSAGE' : 'SUCCESS'}, status=200)
      

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