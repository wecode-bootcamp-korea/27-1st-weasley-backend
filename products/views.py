import json

from django.http        import JsonResponse
from django.views       import View
from django.db.models   import Avg

from products.models    import Category, Product, Review, Price

class ProductView(View):
      def get(self, request, **kwargs):
#
#        product_id = kwargs['product_id']
#
#        product_data = [{
#            'name' : product.name,
#            'ml_volume' : product.category.ml_volume,
#            'category_price' : product.category.price,
#            'thumb' : product.image_set.get(name='thumb').url,
#            'tags' : [tag.name for tag in product.tags.all()],
#            'reviews' : [{
#                'content' : review.content,
#                'star' : review.star,
#                'product_id' : review.product_id,
#                'name' : review.user.name,
#                'created_at' : review.created_at,
#
#            } for review in product.review_set.all()],
#            'price' : [{
#                'manufacturing_cost' : price.manufacturing_cost,
#                'transportation_cost' : price.transportation_cost,
#                'development_cost' : price.development_cost,
#                'commision_cost' : price.commision_cost,
#                'other_market_price' : price.other_market_price
#            } for price in product.price_set.all()]
#        } for product in Product.objects.all()]
#
#        category_data = [{
#            'average' : Review.objects.aggregate(Avg('star')),
#            'products' :
#                'tags' : [tag.name for tag in product.tags.all()],
#                'reviews' : [{
#                    'content' : review.content,
#                    'star' : review.star,
#                    'product_id' : review.product_id,
#                    'name' : review.user.name,
#                    'created_at' : review.created_at,
#
#                } for review in product.review_set.all()]
#        } for product in Product.objects.all()]
#        } for category in Category.objects.all()]

        product = Product.objects.get(id=kwargs['product_id'])
        category_id = product.category.id
        price = Price.objects.get(id=kwargs['product_id'])

        results = {
            'product_id': product.id,
            'ml_volume': product.category.ml_volume,
            'thumb': product.image_set.filter(name='thumb')[0].url,
            'name': product.name,
            'category_price': product.category.price,
            'tags': [tag.name for tag in product.tags.all()],
            'average_star': product.category.product_set.aggregate(star = Avg('review__star'))['star'],
            'reviews' : [{
                'content' : review.content,
                'star' : review.star,
                'name' : review.user.name,
                'created_at' : review.created_at,
             } for review in product.review_set.all()],
            'price': {
                'manufacturing_cost': price.manufacturing_cost,
                'transportation_cost': price.transportation_cost,
                'development_cost': price.development_cost,
                'commision_cost': price.commision_cost,
                'other_market_price': price.other_market_price,
            }

        }

        return JsonResponse({'RESULT' : results, 'MESSAGE' : 'SUCCESS'}, status=200)
