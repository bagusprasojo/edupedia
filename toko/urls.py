from django.urls import path
from .views import homepage_toko, keranjang, tambah_ke_keranjang, checkout

urlpatterns = [
    path('', homepage_toko, name='homepage_toko'),
    path('keranjang/', keranjang, name='keranjang'),
    path('beli/<uuid:uuid>/', tambah_ke_keranjang, name='tambah_ke_keranjang'),
    path('checkout/', checkout, name='checkout'),
]
