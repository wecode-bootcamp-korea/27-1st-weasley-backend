from django.urls import path

from users.views import UserCheckView, SigninView

urlpatterns = [
    path('signin', SigninView.as_view()),
    path('check', UserCheckView.as_view()),
]
