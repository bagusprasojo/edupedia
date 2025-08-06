from django.contrib import admin
from .models import HasilUjian, JawabanUjian

# Register your models here.
class HasilUjianAdmin(admin.ModelAdmin):
    list_display = ('user', 'paket', 'nilai', 'waktu_selesai', 'uuid')
    search_fields = ('user__username', 'paket__nama')
    list_filter = ('paket',)    

class JawabanUjianAdmin(admin.ModelAdmin):
    list_display = ('hasil', 'soal', 'jawaban_dipilih', 'benar', 'uuid')
    search_fields = ('hasil__user__username', 'soal__pertanyaan')
    list_filter = ('hasil__paket',) 

admin.site.register(HasilUjian, HasilUjianAdmin)
admin.site.register(JawabanUjian, JawabanUjianAdmin)   
    