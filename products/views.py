import json

from django.http        import JsonResponse
from django.views       import View
from django.db.models   import Avg, F

from products.models    import Category, Product, Review, Price

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
