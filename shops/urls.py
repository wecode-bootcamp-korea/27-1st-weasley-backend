from django.urls import path

from shops.views import CartView

urlpatterns = [
    path('/carts', CartView.as_view()),
]
