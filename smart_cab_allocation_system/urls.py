from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from rest_framework import routers
from django.conf.urls import include

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/accounts/', include('registration.urls')),
    path('api/cabs/', include('cabs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)