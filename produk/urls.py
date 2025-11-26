from django.urls import path
from .views import tambah_produk, upload_paket_soal, detail_produk, edit_produk


urlpatterns = [
    path('tambah/', tambah_produk, name='buat_produk'),
    path('upload-paket/', upload_paket_soal, name='upload_paket_soal'),
    path('produk/<uuid:uuid>/', detail_produk, name='detail_produk'),
    path('produk/<uuid:uuid>/edit/', edit_produk, name='edit_produk'),
    

]
