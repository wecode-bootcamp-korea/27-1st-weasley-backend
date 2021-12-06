from django.urls    import path, include

from products.views import ProductView

urlpatterns = [
    path('/product', include([
        path('', ProductView.as_view()),
        path('/<int:product_id>', ProductView.as_view())
    ])),
]
