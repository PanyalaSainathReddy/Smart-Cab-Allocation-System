from django.urls import include, path
from rest_framework import routers

from .views import (CookieTokenRefreshView,
                    GoogleLoginView, GoogleRegisterView,
                    LoginView, LogoutView, RegisterUserAPIView, UserDetailAPI)

router = routers.DefaultRouter()

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('register/google/', GoogleRegisterView.as_view(), name="google-register"),
    path('login/google/', GoogleLoginView.as_view(), name="google-login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('refresh/', CookieTokenRefreshView.as_view(), name="refresh"),
    path('user-details/', UserDetailAPI.as_view()),
    path('', include(router.urls)),
]