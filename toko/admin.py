from django.contrib import admin
from .models import  Order, OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'tanggal', 'uuid')
    search_fields = ('user__username',)
    list_filter = ('user',)
    
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'produk', 'harga', 'uuid')
    search_fields = ('order__user__username', 'produk__nama')
    list_filter = ('order__user',)  

admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)

