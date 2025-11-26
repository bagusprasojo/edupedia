from django.urls import path
from .views import homepage_toko, keranjang, tambah_ke_keranjang, checkout, produk_by_kategori, hapus_dari_keranjang

urlpatterns = [
    path('', homepage_toko, name='homepage_toko'),
    path('keranjang/', keranjang, name='keranjang'),
    path('beli/<uuid:uuid>/', tambah_ke_keranjang, name='tambah_ke_keranjang'),
    path('keranjang/hapus/<uuid:uuid>/', hapus_dari_keranjang, name='hapus_dari_keranjang'),
    path('checkout/', checkout, name='checkout'),
    path('kategori/<uuid:uuid>/', produk_by_kategori, name='produk_by_kategori'),
]
