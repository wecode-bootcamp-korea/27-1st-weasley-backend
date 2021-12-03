from django.http     import JsonResponse
from django.views    import View

from products.models import Category


class CategoryView(View):
    def get(self, request):
        category_data = [
            {
                'category_name' : category.name,
                'ml_volume'     : category.ml_volume,
                'price'         : category.price,
                'products'      : [
                            {
                                'thumb' : product.image_set.get(name='thumb').url,
                                'tags'  : [i.name for i in product.tags.all()],
                                'id'    : product.id
                            }
                for product in category.product_set.all()]
            }
            for category in Category.objects.all()
        ]

        return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': category_data}, status=200) 
  
   
