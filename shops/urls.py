from django.urls import path, include

from shops.views import CartView, AllOrderView, OrderView

urlpatterns = [
    path('/carts', include([
        path('', CartView.as_view()),
        path('/<int:product_id>', CartView.as_view())
    ])),
    path('/orders', include([
        path('/all', AllOrderView.as_view()),
        path('/<int:order_id>', OrderView.as_view())
    ])),
]
