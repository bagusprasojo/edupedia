from django.db.models import Avg, Count
from django.shortcuts import redirect, get_object_or_404, render

from cbt.models import HasilUjian
from produk.models import Kategori, PaketSoal, Produk
from .models import KeranjangItem, Order, OrderItem
from django.contrib.auth.decorators import login_required


def _annotated_product_queryset(queryset):
    return (
        queryset
        .select_related('kategori')
        .annotate(
            avg_rating=Avg('paket_soal__hasilujian__nilai'),
            attempt_count=Count('paket_soal__hasilujian', distinct=True),
            paket_count=Count('paket_soal', distinct=True),
        )
    )


def _build_cbt_stats():
    cbt_stats_raw = HasilUjian.objects.aggregate(
        total_ujian=Count('id'),
        total_peserta=Count('user', distinct=True),
        rata_nilai=Avg('nilai'),
    )
    return {
        'total_paket': PaketSoal.objects.count(),
        'total_ujian': cbt_stats_raw['total_ujian'] or 0,
        'total_peserta': cbt_stats_raw['total_peserta'] or 0,
        'rata_nilai': cbt_stats_raw['rata_nilai'],
    }


def _recent_cbt_results(limit=3):
    return HasilUjian.objects.select_related('user', 'paket').order_by('-waktu_selesai')[:limit]

@login_required
def tambah_ke_keranjang(request, uuid):
    produk = get_object_or_404(Produk, uuid=uuid)
    KeranjangItem.objects.get_or_create(user=request.user, produk=produk)
    return redirect('keranjang')

@login_required
def hapus_dari_keranjang(request, uuid):
    """
    Hapus item tertentu dari keranjang user aktif.
    """
    item = get_object_or_404(KeranjangItem, uuid=uuid, user=request.user)
    item.delete()
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
    kategori_list = Kategori.objects.order_by('nama')

    produk_qs = _annotated_product_queryset(
        Produk.objects.filter(is_active=True)
    )

    produk_terbaru_qs = produk_qs.order_by('-tanggal_dibuat')
    produk_terbaru = list(produk_terbaru_qs[:4])
    produk_terbaru_ids = [produk.id for produk in produk_terbaru]
    produk_list = produk_qs.exclude(id__in=produk_terbaru_ids).order_by('nama')

    kategori = 'Semua Kategori'

    cbt_stats = _build_cbt_stats()
    recent_results = _recent_cbt_results()

    return render(request, 'toko/homepage_toko.html', {
        'nama_kategori': kategori,
        'produk_list': produk_list,
        'produk_terbaru': produk_terbaru,
        'kategori_list': kategori_list,
        'cbt_stats': cbt_stats,
        'recent_results': recent_results,
    })

def produk_by_kategori(request, uuid):
    kategori = get_object_or_404(Kategori, uuid=uuid)
    kategori_list = Kategori.objects.order_by('nama')

    produk_qs = _annotated_product_queryset(
        Produk.objects.filter(is_active=True, kategori=kategori)
    )

    produk_terbaru_qs = produk_qs.order_by('-tanggal_dibuat')
    produk_terbaru = list(produk_terbaru_qs[:4])
    produk_terbaru_ids = [produk.id for produk in produk_terbaru]
    produk_list = produk_qs.exclude(id__in=produk_terbaru_ids).order_by('nama')
    
    return render(request, 'toko/homepage_toko.html', {
        'nama_kategori': kategori.nama,
        'produk_list': produk_list,
        'produk_terbaru': produk_terbaru,
        'kategori_list': kategori_list,
        'cbt_stats': _build_cbt_stats(),
        'recent_results': _recent_cbt_results(),
        'active_kategori': kategori,
    })

