from django.urls import path, include
from django.conf import settings
from webapp import views

# ======================================================
#   DEVELOPMENT-ONLY URLs — never exposed in production
# ======================================================
urlpatterns = []

if settings.DEBUG:
    from django.urls import re_path
    from rest_framework.routers import DefaultRouter
    from rest_framework.authtoken.views import obtain_auth_token
    from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
        TokenVerifyView,
    )
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    r = DefaultRouter()
    r.register(
        "apiviewset", views.DRFViewSet, basename="apiviewset"
    )  # normal ViewSet — basename mandatory
    r.register(
        "apimodelviewset", views.DRFModelViewSet, basename="apimodelviewset"
    )  # ModelViewSet — basename optional

    urlpatterns += [
        # ----------------------------------------------------------THE BELOW PATHS ARE FOR CLAUDE-----------------------------------------------
        path("claude/", views.claude_page, name="claude"),
        # ---------------------------------------------------------DRF {DJANGO REST FRAMEWORK}------------------------------------------------
        path("api/", views.DRFAPIVIEW.as_view()),
        path("api/<int:id>/", views.DRFAPIVIEW.as_view()),
        path("apiinbuilt/", views.DRFInbuiltAPIViews1.as_view()),
        path("apiinbuilt2/<int:pk>/", views.DRFInbuiltAPIViews2.as_view()),
        path("apiinbuilt3/", views.DRFInbuiltAPIViews3.as_view()),
        path("apiinbuilt3/<int:pk>/", views.DRFInbuiltAPIViews4.as_view()),
        path("apiinbuilt4/", views.DRFInbuiltAPIViews5.as_view()),
        path("apiinbuilt4/<int:pk>/", views.DRFInbuiltAPIViews6.as_view()),
        # ------------------------------------------------------------ TOKEN / JWT AUTH (practice) ------------------------------------------------------------
        path("get-api-token/", obtain_auth_token, name="get-api-token"),
        path("jwt-token-get/", TokenObtainPairView.as_view(), name="api-jwt-token"),
        path("jwt-token-refresh/", TokenRefreshView.as_view(), name="api-jwt-token-refresh"),
        path("jwt-token-verify/", TokenVerifyView.as_view(), name="api-jwt-token-verify"),
        # Router (DRF ViewSet + ModelViewSet)
        path("", include(r.urls)),
        # -------------------------------------------------------- SWAGGER / REDOC DOCS --------------------------------------------------------
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
        # ---------------------------------------- WISH PRACTICE PATHS [FBV] ----------------------------------------
        path("wish/", views.wish_retrieveview),
        path("wishinsert/", views.wish_insertview),
        path("delete/<int:id>", views.wish_deleteview),
        path("update/<int:id>", views.wish_updateview),
        # wish data practice paths using CLASS BASED VIEWS
        path("wishcbv/", views.Wishgetview.as_view()),
        path("wishcbvtemplate/", views.wishgetviewtemplateview.as_view()),
        # ----------------------------------------- MODEL RELATED VIEW CLASSES [CBV] -----------------------------------------
        path("wishcreatecbv/", views.wishcreateview.as_view()),
        path("wishupdatecbv/<int:pk>/", views.wishupdateview.as_view()),
        path("wishdeletecbv/<int:pk>/", views.wishdeleteview.as_view()),
        path("wishlistcbv/", views.wishlistview.as_view()),
        path("wishlistcbv2/", views.wishlistview2.as_view(), name="wishlistcbv2"),
        path("<int:pk>/", views.wishdetailview.as_view(), name="wishdetail"),
        # ------------------------------------------------------------------ DRF API PATHS ------------------------------------------------------------------
        path("api/wishlistwr/", views.wish_api_view1),
        path("api/wishlist2wr/", views.wish_api_view2),
        # ---------------------------------------------------------- CBV USING DJANGO REST FRAMEWORK --------------------------------------------------------
        path("api/testviewcbvwr/", views.test.as_view()),
        path("api/wishlistcbvwr/<int:id>/", views.jsonCBV.as_view(), name="wishlist-detail"),
        path("api/wishlistcbv1wr/", views.jsonCBV1.as_view()),
        path("api/wishlistcbv2wr/", views.jsonCBV2.as_view()),
        path("api/crudcbv", views.DRFCRUDCBV.as_view()),
        path("api/wishserializemetawr/", views.serializemetaCBV.as_view()),
        path("api/wishlistserializewr/", views.serializesingleCBV.as_view()),
    ]


# ======================================================
#   PRODUCTION URLs — always active
# ======================================================
urlpatterns += [
    # -------------------------------------------------------- CLAUDE API --------------------------------------------------------
    path("api/claude/", views.claude_api, name="claude-api"),
    # -------------------------------------------------------- WEBSITE URLS --------------------------------------------------------
    path("loginpage/", views.loginForm_view, name="loginpage"),
    path("signupform/", views.signupForm_view, name="signupform"),
    path("forgotpassword/", views.forgotpasswordForm_view, name="forgotpassword"),
    path("home/", views.homepage_view, name="home"),
    path("about/", views.aboutpage_view, name="about"),
    path("audio/", views.audiopage_view, name="audio"),
    path("books/", views.books_view, name="books"),
    path("gallery/", views.gallery_view, name="gallery"),
    path("contact-submit/", views.contact_view, name="contact-submit"),
    path("session-ping/", views.session_ping, name="session-ping"),
    # Session auth (needed for login/logout on the website)
    path("accounts/", include("django.contrib.auth.urls")),
    # ⚠️ Catch-all slug — MUST be last so it doesn't shadow specific paths above
    path("<slug:title>/", views.aboutdetail_view, name="aboutdetail"),
]
