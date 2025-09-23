"""
URL configuration for event_face project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
def api_root(request, format=None):
    return Response({
        "register": reverse("register", request=request, format=format),
        "login": reverse("login", request=request, format=format),
        "logout": reverse("token_blacklist", request=request, format=format),
        "token_refresh": reverse("token_refresh", request=request, format=format),
        "events": reverse("events-list", request=request, format=format),
    })


api_v1_str = "api"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{api_v1_str}/", api_root, name="api-root"),
    path(f"{api_v1_str}/auth/", include("auth_jwt.urls"), name="auth_jwt"),
    path(f"{api_v1_str}/events/", include("events.urls"), name="events"),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()


admin.site.site_header = 'Панель администрирования event-face'
admin.site.site_title = 'EventFace'
