from django.urls import path
from webapp import views

urlpatterns = [
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


    # this below paths is a temporary path for my practice [FBV]
    path('wish/', views.wish_retrieveview),
    path('wishinsert/', views.wish_insertview),
    path('delete/<int:id>', views.wish_deleteview),
    path('update/<int:id>', views.wish_updateview),

    # wish data practice paths using CLASS BASED VIEWS
    path('wishcbv/', views.Wishgetview.as_view()),
    path('wishcbvtemplate/', views.wishgetviewtemplateview.as_view()),

    # THE BELOW ARE FOR MODEL RELATED VIEWS CLASSES [CBV] OPERATIONS BASED ON ID[PK]

    path('wishcreatecbv/', views.wishcreateview.as_view()),
    path('wishupdatecbv/<int:pk>/', views.wishupdateview.as_view()),
    path('wishdeletecbv/<int:pk>/', views.wishdeleteview.as_view()),
    path('wishlistcbv/', views.wishlistview.as_view()),
    path('wishlistcbv2/', views.wishlistview2.as_view(), name='wishlistcbv2'),
    path('<int:pk>/', views.wishdetailview.as_view(), name='wishdetail'),

    path('<slug:title>/', views.aboutdetail_view, name='aboutdetail'),

    # path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail_view, name='post_detail'),

]
