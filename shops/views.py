import json

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Prefetch

from shops.models     import Cart
from products.models  import Image
from core.utils       import authorization


class CartView(View):
    @authorization
    def get(self, request):
        user = request.user

        cart_list = Cart.objects.filter(
            user__id=user.id
        ).select_related(
            'product__category',
            'product'
        ).prefetch_related(
            Prefetch(
                'product__image_set',
                queryset=Image.objects.filter(
                    name='thumb'
                ),
                to_attr='thumb'
            ),
            'product__tags'
        )

        results = [
            {
                'product_id'    : cart_item.product.id,
                'category_name' : cart_item.product.category.name,
                'tags'          : list(map(
                    lambda x: x.name, cart_item.product.tags.all()
                )),
                'ml_volume'     : cart_item.product.category.ml_volume,
                'price'         : cart_item.product.category.price,
                'amount'        : cart_item.amount,
                'thumb'         : cart_item.thumb
            }
            for cart_item in cart_list
        ]

        return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': results}, status=200)
