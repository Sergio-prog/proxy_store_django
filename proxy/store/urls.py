from django.urls import path
from django.views.generic import TemplateView

from . import views

from django.contrib.auth import views as auth_views

from .views import SignUpView

app_name = "store"
urlpatterns = [
    path("", views.index, name="index"),
    path("signin/", views.signin, name='signin'),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('deposit/', views.deposit, name='deposit'),
    path('products/<int:product_id>/', views.detail_product, name='detailed_product'),
    path('products/buy/<int:product_id>/', views.buy_product, name='buy_product'),
    path('profile', views.profile, name='profile'),
]
