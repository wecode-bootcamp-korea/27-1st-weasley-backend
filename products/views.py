from django.http     import JsonResponse
from django.views    import View

from products.models import Category


class CategoriesView(View):
    def get(self, request):
        categories = [{
            'name'        : category.name,
            'ml_volume'   : category.ml_volume,
            'price'       : category.price,
            'products'    : [{
                'thumb' : product.image_set.get(name='thumb').url,
                'tags'  : [tag.name for tag in product.tags.all()],
                'id'    : product.id
            } for product in category.product_set.all()]
        } for category in Category.objects.all()]

        return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': categories}, status=200) 
  
