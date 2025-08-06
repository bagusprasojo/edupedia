from django.shortcuts import render
from produk.models import Produk, Kategori
from django.shortcuts import redirect, get_object_or_404, render
from .models import KeranjangItem, Order, OrderItem
from django.contrib.auth.decorators import login_required

@login_required
def tambah_ke_keranjang(request, uuid):
    produk = get_object_or_404(Produk, uuid=uuid)
    KeranjangItem.objects.get_or_create(user=request.user, produk=produk)
    return redirect('keranjang')

@login_required
def keranjang(request):
    item_keranjang = KeranjangItem.objects.filter(user=request.user)
    total = sum(item.produk.harga for item in item_keranjang)

    return render(request, 'toko/keranjang.html', {
        'item_keranjang': item_keranjang,
        'total': total
    })

@login_required
def checkout(request):
    keranjang = KeranjangItem.objects.filter(user=request.user)
    if not keranjang.exists():
        return redirect('keranjang')

    # Buat order baru
    order = Order.objects.create(user=request.user)

    # Simpan semua item keranjang ke OrderItem
    for item in keranjang:
        OrderItem.objects.create(
            order=order,
            produk=item.produk,
            harga=item.produk.harga
        )

    # Bersihkan keranjang
    keranjang.delete()

    return render(request, 'toko/checkout_sukses.html', {'order': order})


def homepage_toko(request):
    produk_terbaru = Produk.objects.order_by('-tanggal_dibuat')[:5]
    kategori = Kategori.objects.filter(parent__isnull=True)

    return render(request, 'toko/homepage_toko.html', {
        'produk_terbaru': produk_terbaru,
        'kategori_list': kategori,
    })
