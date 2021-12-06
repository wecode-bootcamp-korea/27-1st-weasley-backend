from django.urls import path, include

from products.views import CategoriesView

urlpatterns = [
    path('/categories', CategoriesView.as_view()),
]
