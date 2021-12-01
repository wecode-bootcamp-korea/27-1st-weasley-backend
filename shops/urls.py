from django.urls import path

from shops.views import CartView

urlpatterns = [
    path('all', CartView.as_view()),
]
