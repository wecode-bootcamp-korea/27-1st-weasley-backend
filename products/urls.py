<<<<<<< HEAD
from django.urls import path, include

from products.views import CategoriesView

urlpatterns = [
    path('/categories', CategoriesView.as_view()),
=======
from django.urls    import path

from products.views import ReviewView

urlpatterns = [
    path('/review', ReviewView.as_view()),
>>>>>>> main
]
