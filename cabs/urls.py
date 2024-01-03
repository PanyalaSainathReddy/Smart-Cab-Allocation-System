from django.urls import path

from .views import find_nearest_cab

urlpatterns = [
    path('find-nearest-cab/', find_nearest_cab),
]