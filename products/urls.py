from django.urls import path

from products.views import CategoryView

urlpatterns = [
    path('/category', CategoryView.as_view()),
]
