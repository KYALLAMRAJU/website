"""
URL configuration for webProject project.

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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from webapp.views import health_check

# ─── CUSTOM ERROR HANDLERS ────────────────────────────────────────────────────
# These must be registered in the ROOT urls.py (not in webapp/urls.py)
# Django looks for handler404, handler500, handler403, handler400 only here.
# They only activate when DEBUG = False in settings.py.
from webapp.views import error_404, error_500, error_403, error_400
handler404 = error_404   # wrong URL / page not found
handler500 = error_500   # server crash
handler403 = error_403   # no permission
handler400 = error_400   # bad request
# ──────────────────────────────────────────────────────────────────────────────

urlpatterns = [
    # ── Health check — always available (used by ALB, uptime monitors, k8s probes)
    path("health/", health_check, name="health-check"), # this is for health check endpoint
    path("admin/", admin.site.urls), # this is for Django admin
    # ── OAuth2 / Social login (django-allauth) — must be before webapp.urls ──
    path("accounts/", include("allauth.urls")), # this is for django-allauth (social login)
    path("", include("webapp.urls")),  # change this line according to your company (update to your app's urls module)
    #the empty string above means that the webapp.urls will be included at the root URL level (i.e., it will handle all URLs that don't match the admin or accounts paths).
]

if settings.DEBUG:

    # DRF browsable API login/logout — only needed locally

    urlpatterns += [path("api-auth/", include("rest_framework.urls"))] # this is for DRF BROWSABLE API

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
