from django.urls import path
from . import views

urlpatterns = [
    path('', views.daftar_paket_ujian, name='daftar_paket_ujian'),
    path('kerjakan/<uuid:uuid>/', views.kerjakan_paket, name='kerjakan_paket'),
    path('hasil/<uuid:uuid>/', views.hasil_ujian, name='hasil_ujian'),
    path('produk/<uuid:uuid>/', views.daftar_paket_per_produk, name='paket_per_produk'),
]
