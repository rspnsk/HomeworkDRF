from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # REST API
    path('api/', include([
        path('materials/', include('materials.urls')),
        path('users/', include('users.urls')),
    ])),
]