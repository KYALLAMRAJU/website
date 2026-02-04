from django.urls import path, include
from webapp import views
from django.urls import re_path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView,SpectacularSwaggerView

r=DefaultRouter()
r.register('apiviewset',views.DRFViewSet,basename='apiviewset')#here in normal view set basename is mandatory
r.register('apimodelviewset',views.DRFModelViewSet,basename='apimodelviewset') #here in modelview set basename is optional

urlpatterns = [

    # ---------------------------------------------------------DRF{DJANGO REST FRAMEWORK}------------------------------------------------
    path('api/',views.DRFAPIVIEW.as_view()),
    path('api/<int:id>/', views.DRFAPIVIEW.as_view()),

    path('apiinbuilt/', views.DRFInbuiltAPIViews1.as_view()),
    path('apiinbuilt2/<int:pk>/', views.DRFInbuiltAPIViews2.as_view()),

    path('apiinbuilt3/', views.DRFInbuiltAPIViews3.as_view()),
    path('apiinbuilt3/<int:pk>/', views.DRFInbuiltAPIViews4.as_view()),

    path('apiinbuilt4/', views.DRFInbuiltAPIViews5.as_view()),
    path('apiinbuilt4/<int:pk>/', views.DRFInbuiltAPIViews6.as_view()),

    #re_path(r'^api/(?P<uid>.*)/$', views.DRFAPIVIEW.as_view()),

    # ------------------------------------------------------------AUTHENTICATION AND AUTHORIZATION PATHS------------------------------------------------------------

    path('get-api-token/',obtain_auth_token, name='get-api-token'), #this is for token based authentication

#-----------------------------------------------------------------JWT AUTHENTICATION PATHS-----------------------------------------------------------------

    path('jwt-token-get/', TokenObtainPairView.as_view(), name='api-jwt-token'),
    path('jwt-token-refresh/', TokenRefreshView.as_view(), name='api-jwt-token-refresh'),
    path('jwt-token-verify/', TokenVerifyView.as_view(), name='api-jwt-token-verify'),

    path('', include(r.urls)),


#---------------------------------------------------------------- SESSION AUTHENTICATION PATHS ----------------------------------------------------------------
    path('accounts/', include('django.contrib.auth.urls')),

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # --------------------------------------------------------SWAGGER DOCUMENTATION PATH------------------------------------------------------------

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                                            # Define your website URL patterns here

    path('loginpage/', views.loginForm_view),
    path('signupform/', views.signupForm_view),
    path('forgotpassword/', views.forgotpasswordForm_view),
    path('home/', views.homepage_view),
    path('about/', views.aboutpage_view),
    path('audio/', views.audiopage_view),
    path('books/', views.books_view),
    path('gallery/', views.gallery_view),
    path('contact-submit/', views.contact_view),


    #----------------------------------------this below paths is a temporary path for my practice [FBV]-----------------------------------------------------
    path('wish/', views.wish_retrieveview),
    path('wishinsert/', views.wish_insertview),
    path('delete/<int:id>', views.wish_deleteview),
    path('update/<int:id>', views.wish_updateview),

    # wish data practice paths using CLASS BASED VIEWS
    path('wishcbv/', views.Wishgetview.as_view()),
    path('wishcbvtemplate/', views.wishgetviewtemplateview.as_view()),

    #-----------------------------------------THE BELOW ARE FOR MODEL RELATED VIEWS CLASSES [CBV] OPERATIONS BASED ON ID[PK]-----------------------------------------------------

    path('wishcreatecbv/', views.wishcreateview.as_view()),
    path('wishupdatecbv/<int:pk>/', views.wishupdateview.as_view()),
    path('wishdeletecbv/<int:pk>/', views.wishdeleteview.as_view()),
    path('wishlistcbv/', views.wishlistview.as_view()),
    path('wishlistcbv2/', views.wishlistview2.as_view(), name='wishlistcbv2'),
    path('<int:pk>/', views.wishdetailview.as_view(), name='wishdetail'),
    path('<slug:title>/', views.aboutdetail_view, name='aboutdetail'),

    # path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail_view, name='post_detail'),


    #------------------------------------------------------------------DJANGO REST FRAMEWORK API PATHS------------------------------------------------------------------

    path('api/wishlistwr/',views.wish_api_view1),
    path('api/wishlist2wr/',views.wish_api_view2),


    #----------------------------------------------------------THE BELOW PATH IS FOR CLASS BASED VIEW USING DJANGO REST FRAMEWORK------------------------------------------------
    path('api/testviewcbvwr/',views.test.as_view()),
    path('api/wishlistcbvwr/<int:id>/',views.jsonCBV.as_view(),name="wishlist-detail"),
    path('api/wishlistcbv1wr/',views.jsonCBV1.as_view()),
    path('api/wishlistcbv2wr/',views.jsonCBV2.as_view()),
    path('api/crudcbv/', views.crudCBV.as_view()),
    path('api/drfcrudcbv/', views.DRFCRUDCBV.as_view()),
    path('api/wishserializemetawr/',views.serializemetaCBV.as_view()),
    path('api/wishlistserializewr/',views.serializesingleCBV.as_view()),






]
