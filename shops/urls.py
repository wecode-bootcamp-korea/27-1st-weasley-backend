from django.urls import path, include

from shops.views import CartView, AllOrderView, OrderView

urlpatterns = [
    path('/carts', include([
        path('', CartView.as_view()),
        path('/<int:cart_id>', CartView.as_view())
    ])),
    path('/orders', include([
        path('', OrderView.as_view())
        path('/all', AllOrderView.as_view()),
        path('/<int:order_id>', OrderView.as_view())
    ])),
]
