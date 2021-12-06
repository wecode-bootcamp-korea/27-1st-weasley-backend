import json

from django.http        import JsonResponse
from django.views       import View
from django.db.models   import Avg

from products.models    import Category, Product, Review

class ProductView(View):
      def get(self, request, **kwargs):

        new_id = kwargs['product_id']

        product_data = [{
            'name' : product.name,
            'ml_volume' : product.category.ml_volume,
            'category_price' : product.category.price,
            'thumb' : product.image_set.get(name='thumb').url,
            'price' : [{
                'manufacturing_cost' : price.manufacturing_cost,
                'transportation_cost' : price.transportation_cost,
                'development_cost' : price.development_cost,
                'commision_cost' : price.commision_cost,
                'other_market_price' : price.other_market_price
            } for price in product.price_set.all()],
        } for product in Product.objects.all()]

        category_data = [{
            'average' : Review.objects.aggregate(Avg('star')),
            'products' : [{
                'tags' : [tag.name for tag in product.tags.all()],
                'reviews' : [{
                    'content' : review.content,
                    'star' : review.star,
                    'product_id' : review.product_id,
                    'name' : review.user.name,
                    'created_at' : review.created_at,

                } for review in product.review_set.all()]
            } for product in category.product_set.all()]
        } for category in Category.objects.all()]

        return JsonResponse({'RESULT' : [product_data[new_id], category_data[new_id]], 'MESSAGE' : 'SUCCESS'}, status=200)
