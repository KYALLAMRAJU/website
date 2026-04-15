from django.urls import path, include
from django.conf import settings
from webapp import views  # change this line according to your company (update to your app name)

# ======================================================
#   DEVELOPMENT-ONLY URLs — never exposed in production
# ======================================================
urlpatterns = []

if settings.DEBUG:
    # ── Dev/test URLs live in urls_dev.py (git-ignored) ──
    try:
        from webapp.urls_dev import urlpatterns as dev_urlpatterns
        urlpatterns += dev_urlpatterns
    except ImportError:
        pass  # urls_dev.py is git-ignored; safe to skip if missing
# ======================================================
#   PRODUCTION URLs — always active
# ======================================================
urlpatterns += [
    # -------------------------------------------------------- WEBSITE URLS --------------------------------------------------------
    path("loginpage/", views.loginForm_view, name="loginpage"),           # change this line according to your company (update URL path as needed)

    path("signupform/", views.signupForm_view, name="signupform"),        # change this line according to your company (update URL path as needed)

    path("forgotpassword/", views.forgotpasswordForm_view, name="forgotpassword"),  # change this line according to your company

    path("home/", views.homepage_view, name="home"),                      # change this line according to your company (update URL path as needed)

    path("about/", views.aboutpage_view, name="about"),                   # change this line according to your company (update URL path as needed)

    path("audio/", views.audiopage_view, name="audio"),                   # change this line according to your company (add/remove pages as needed)

    path("books/", views.books_view, name="books"),                       # change this line according to your company (add/remove pages as needed)

    path("gallery/", views.gallery_view, name="gallery"),                 # change this line according to your company (add/remove pages as needed)

    path("contact-submit/", views.contact_view, name="contact-submit"),   # change this line according to your company

    path("session-ping/", views.session_ping, name="session-ping"),


    # ⚠️ Catch-all slug — MUST be last so it doesn't shadow specific paths above
    path("<slug:title>/", views.aboutdetail_view, name="aboutdetail"),    # change this line according to your company (update to match your detail view)
]
