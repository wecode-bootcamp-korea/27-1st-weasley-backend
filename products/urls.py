from django.urls    import path, include

from products.views import ProductView, ReviewView, CategoriesView

urlpatterns = [
    path('/<int:product_id>', ProductView.as_view()),
    path('/review', ReviewView.as_view()),
    path('/categories', CategoriesView.as_view()),
]