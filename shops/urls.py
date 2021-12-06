from django.urls import path, include

from shops.views import CartView, OrderView

urlpatterns = [
    path('/carts', include([
        path('', CartView.as_view()),
        path('/<int:cart_id>', CartView.as_view())
    ])),
    path('/orders', include([
        path('', OrderView.as_view())
    ]))
]
