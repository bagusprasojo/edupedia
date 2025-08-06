from django.contrib import admin
from .models import Produk, Kategori, PaketSoal, Soal

from .models import Kategori


class KategoriAdmin(admin.ModelAdmin):
    list_display = ('nama', 'parent')
    search_fields = ('nama',)


# Register your models here.
class ProdukAdmin(admin.ModelAdmin):
    model = Produk
    extra = 1
    verbose_name = 'Produk'
    verbose_name_plural = 'Produk'
    fields = ('penjual', 'nama', 'deskripsi', 'harga', 'gambar', 'kategori', 'paket_soal')
    readonly_fields = ('uuid',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('penjual', 'kategori')

class PaketSoalAdmin(admin.ModelAdmin):
    list_display = ['id', 'nama', 'get_produks', 'deskripsi']


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('produks')  # ✅ prefetch, bukan select_related

    def get_produks(self, obj):
        return ", ".join([p.nama for p in obj.produks.all()])
    get_produks.short_description = 'Digunakan di Produk'


class SoalAdmin(admin.ModelAdmin):
    # model = Soal
    # extra = 1
    # verbose_name = 'Soal'
    # verbose_name_plural = 'Soal'
    # fields = ('paket', 'teks', 'opsi_a', 'opsi_b', 'opsi_c', 'opsi_d','jawaban_benar', 'pembahasan')
    # list_display['paket', 'teks', 'opsi_a', 'opsi_b', 'opsi_c', 'opsi_d','jawaban_benar', 'pembahasan']
    # readonly_fields = ('paket',)
    list_display = ('id', 'paket__id', 'teks', 'opsi_a', 'opsi_b', 'opsi_c', 'opsi_d', 'jawaban_benar')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paket')



admin.site.register(Produk, ProdukAdmin)
admin.site.register(Kategori, KategoriAdmin)
admin.site.register(PaketSoal, PaketSoalAdmin)
admin.site.register(Soal, SoalAdmin)
