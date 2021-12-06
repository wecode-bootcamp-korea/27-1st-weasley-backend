from django.urls    import path

from products.views import ReviewView

urlpatterns = [
    path('/review', ReviewView.as_view()),
]
