from django.urls import path
from .views import tambah_produk, upload_paket_soal, detail_produk, edit_produk, paket_soal_detail, hapus_soal, edit_soal


urlpatterns = [
    path('tambah/', tambah_produk, name='buat_produk'),
    path('upload-paket/', upload_paket_soal, name='upload_paket_soal'),
    path('produk/<uuid:uuid>/', detail_produk, name='detail_produk'),
    path('produk/<uuid:uuid>/edit/', edit_produk, name='edit_produk'),
    path('paket-soal/<uuid:uuid>/', paket_soal_detail, name='paket_soal_detail'),
    path('soal/<uuid:uuid>/delete/', hapus_soal, name='hapus_soal'),
    path('soal/<uuid:uuid>/edit/', edit_soal, name='edit_soal'),
    

]
