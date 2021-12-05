from django.urls import path, include

from users.views import SignupView, SigninView, AddressView

urlpatterns = [
    path('/signup', SignupView.as_view()),
    path('/signin', SigninView.as_view()),
    path('/addresses', include([
        path('', AddressView.as_view()),
    ])),
]
