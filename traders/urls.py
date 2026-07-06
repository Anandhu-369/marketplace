from django.urls import path
from traders.views import *
urlpatterns = [
    path('signup',SignupView.as_view(),name="signup"),
    path('homepage',HomePageView.as_view(),name="homepage"),
    path('productdetails/<int:pid>',ProductDetailsView.as_view(),name="productdetails"),
    path('addproduct',ProductCreateView.as_view(),name="addproduct"),
    path('chat',ChatView.as_view(),name='chat'),
    path('addtocart/<int:cid>',AddToCartView.as_view(),name="addtocart"),
    path('cartlist',CartListView.as_view(),name="cartlist"),
    path('removecart/<int:cid>',RemoveCartView.as_view(),name="remcart"),
    path("profile",ShowProfileView.as_view(),name="profile"),
    path("editprofile",EditProfileView.as_view(),name="editprofile"),
]
