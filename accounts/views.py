from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import LoginForm
from toko.models import Order
from produk.models import Produk, PaketSoal
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data['username']
            pword = form.cleaned_data['password']
            user = authenticate(username=uname, password=pword)
            if user is not None:
                login(request, user)
                return redirect('role_redirect')
            else:
                messages.error(request, "Username atau password salah")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('role_redirect')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def role_redirect(request):
    user = request.user
    if user.is_seller:
        return redirect('seller_dashboard')
    else:
        return redirect('buyer_dashboard')


def seller_required(user):
    return user.is_authenticated and user.is_seller

def buyer_required(user):
    return user.is_authenticated and user.is_buyer

@user_passes_test(seller_required)
def seller_dashboard(request):
    products_qs = (
        Produk.objects
        .filter(penjual=request.user)
        .select_related('kategori')
        .prefetch_related('paket_soal')
        .annotate(total_purchases=Count('orderitem', distinct=True))
        .order_by('-tanggal_diperbarui')
    )

    digital_products = []
    for produk in products_qs:
        desc = (produk.deskripsi or '').strip()
        short_desc = f"{desc[:110]}..." if len(desc) > 110 else desc
        digital_products.append({
            'id': produk.id,
            'uuid': produk.uuid,
            'nama': produk.nama,
            'kategori': produk.kategori.nama if produk.kategori else 'Umum',
            'deskripsi_singkat': short_desc or 'Belum ada deskripsi singkat.',
            'status': 'Aktif' if produk.is_active else 'Nonaktif',
            'is_active': produk.is_active,
            'pengguna_aktif': produk.total_purchases or 0,
            'durasi': '-',
            'rating': '-',
            'kelulusan': '-',
            'harga': produk.harga,
            'paket_soal_count': produk.paket_soal.count(),
            'created_at': produk.tanggal_dibuat,
            'updated_at': produk.tanggal_diperbarui,
        })

    now = timezone.now()
    last_week = now - timedelta(days=7)
    seller_metrics = {
        'total_packages': products_qs.count(),
        'new_packages': products_qs.filter(tanggal_dibuat__gte=last_week).count(),
        'active_learners': sum(item['pengguna_aktif'] for item in digital_products),
        'avg_duration': "42 m",
        'pass_rate': "78%",
        'royalty_ready': "0",
        'royalty_month': "0",
        'royalty_target': "Target belum ditetapkan",
        'royalty_progress': 0,
        'next_level_points': 120,
    }

    context = {
        'digital_products': digital_products,
        'seller_metrics': seller_metrics,
        'pending_reviews': [],
        'seller_activity': [],
        'campaign': {},
    }
    return render(request, 'accounts/seller_dashboard.html', context)


@user_passes_test(seller_required)
def seller_products_list(request):
    products = (
        Produk.objects
        .filter(penjual=request.user)
        .select_related('kategori')
        .annotate(paket_count=Count('paket_soal', distinct=True))
        .order_by('-tanggal_diperbarui')
    )
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'start_index': page_obj.start_index() if page_obj.paginator.count else 0,
    }
    return render(request, 'accounts/seller_products_list.html', context)


@require_POST
@user_passes_test(seller_required)
def seller_product_toggle(request, pk):
    produk = get_object_or_404(Produk, pk=pk, penjual=request.user)
    activating = not produk.is_active
    if activating and produk.paket_soal.count() == 0:
        messages.warning(request, f"{produk.nama} belum memiliki paket soal, tambahkan terlebih dahulu sebelum mengaktifkan.")
        return redirect('seller_products_list')

    produk.is_active = not produk.is_active
    produk.save()
    status = "diaktifkan" if produk.is_active else "dinonaktifkan"
    messages.success(request, f"{produk.nama} berhasil {status}.")
    return redirect('seller_products_list')


@require_POST
@user_passes_test(seller_required)
def seller_product_delete(request, pk):
    produk = get_object_or_404(Produk, pk=pk, penjual=request.user)
    produk.delete()
    messages.success(request, f"{produk.nama} berhasil dihapus.")
    return redirect('seller_products_list')


@user_passes_test(seller_required)
def seller_paketsoal_list(request):
    base_qs = PaketSoal.objects.filter(produks__penjual=request.user).distinct()
    summary_qs = base_qs.annotate(total_soal=Count('soal', distinct=True))
    stats = {
        'total_paket': summary_qs.count(),
        'paket_siap': summary_qs.filter(total_soal__gt=0).count(),
        'paket_kosong': summary_qs.filter(total_soal=0).count(),
        'total_soal': summary_qs.aggregate(total=Count('soal', distinct=True))['total'] or 0,
        'total_produk': summary_qs.aggregate(total=Count('produks', distinct=True))['total'] or 0,
    }

    paket_qs = base_qs
    search_query = request.GET.get('q', '').strip()
    if search_query:
        paket_qs = paket_qs.filter(Q(nama__icontains=search_query) | Q(deskripsi__icontains=search_query))

    paket_qs = paket_qs.annotate(
        total_soal=Count('soal', distinct=True),
        total_produk=Count('produks', distinct=True),
    ).order_by('-id')

    status_filter = request.GET.get('status')
    if status_filter == 'ready':
        paket_qs = paket_qs.filter(total_soal__gt=0)
    elif status_filter == 'empty':
        paket_qs = paket_qs.filter(total_soal=0)

    paginator = Paginator(paket_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'start_index': page_obj.start_index() if page_obj.paginator.count else 0,
        'search_query': search_query,
        'status_filter': status_filter,
        'stats': stats,
    }
    return render(request, 'accounts/seller_paketsoal_list.html', context)


@require_POST
@user_passes_test(seller_required)
def seller_paketsoal_delete(request, uuid):
    paket = get_object_or_404(PaketSoal, uuid = uuid, penjual=request.user)
    nama = paket.nama
    paket.delete()
    messages.success(request, f"Paket soal '{nama}' berhasil dihapus.")
    return redirect('seller_paketsoal_list')


@user_passes_test(buyer_required)
def buyer_dashboard(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items', 'items__produk')
    total_produk = sum(order.items.count() for order in orders)
    return render(request, 'accounts/buyer_dashboard.html', {'orders': orders, 'total_produk': total_produk })
