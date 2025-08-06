from django.urls import path
from . import views
from .views import login_view, logout_view

urlpatterns = [    
    path('register/', views.register_view, name='register'),
    path('redirect/', views.role_redirect, name='role_redirect'),
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
