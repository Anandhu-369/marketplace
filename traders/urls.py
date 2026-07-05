from django.urls import path
from traders.views import *
urlpatterns = [
    path('signup',SignupView.as_view(),name="signup"),
    path('homepage',HomePageView.as_view(),name="homepage"),
    path('productdetails/<int:pid>',ProductDetailsView.as_view(),name="productdetails"),
    path('addproduct',ProductCreateView.as_view(),name="addproduct"),
    path('chat',ChatView.as_view(),name='chat'),
]
