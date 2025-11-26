from django.urls import path
from . import views
from .views import login_view, logout_view

urlpatterns = [    
    path('register/', views.register_view, name='register'),
    path('redirect/', views.role_redirect, name='role_redirect'),
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/produk/', views.seller_products_list, name='seller_products_list'),
    path('seller/produk/<int:pk>/toggle/', views.seller_product_toggle, name='seller_product_toggle'),
    path('seller/produk/<int:pk>/delete/', views.seller_product_delete, name='seller_product_delete'),
    path('seller/paket-soal/', views.seller_paketsoal_list, name='seller_paketsoal_list'),
    path('seller/paket-soal/<uuid:uuid>/delete/', views.seller_paketsoal_delete, name='seller_paketsoal_delete'),
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
