from django.urls import path

from shops.views import AllCartView

urlpatterns = [
    path('all', AllCartView.as_view()),
]
