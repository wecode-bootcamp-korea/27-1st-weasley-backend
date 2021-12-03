from django.urls import path, include

from shops.views import CartView

urlpatterns = [
    path('/carts', include([
        path('', CartView.as_view()),
        path('/<int:product_id>', CartView.as_view())
    ])),
]
