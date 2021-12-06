from django.urls import path, include

from products.views import ReviewView, CategoriesView

urlpatterns = [
    path('/review', ReviewView.as_view()),
    path('/categories', CategoriesView.as_view()),
]