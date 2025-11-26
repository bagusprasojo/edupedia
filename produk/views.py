from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .forms import ProdukForm, SoalForm
from .models import Produk, PaketSoal, Soal, Kategori
import openpyxl
from django.db import transaction

def detail_produk(request, uuid):
    produk = get_object_or_404(Produk, uuid=uuid)
    paket_list = produk.paket_soal.all()

    total_soal = sum(paket.soal.count() for paket in paket_list)

    return render(request, 'produk/detail_produk.html', {
        'produk': produk,
        'paket_list': paket_list,
        'total_soal': total_soal,
    })


def seller_required(user):
    return user.is_authenticated and user.is_seller

@user_passes_test(seller_required)
def tambah_produk(request):
    if request.method == 'POST':
        form = ProdukForm(request.POST, request.FILES)
        if form.is_valid():
            produk = form.save(commit=False)
            produk.penjual = request.user
            produk.save()
            return redirect('seller_products_list')
    else:
        form = ProdukForm()
    return render(request, 'produk/tambah_produk.html', {'form': form, 'title': 'Tambah Produk Baru'})


@user_passes_test(seller_required)
def edit_produk(request, uuid):
    produk = get_object_or_404(Produk, uuid=uuid, penjual=request.user)
    if request.method == 'POST':
        form = ProdukForm(request.POST, request.FILES, instance=produk)
        if form.is_valid():
            form.save()
            return redirect('seller_products_list')
    else:
        form = ProdukForm(instance=produk)
    return render(request, 'produk/tambah_produk.html', {'form': form, 'title': f'Edit: {produk.nama}'})


@user_passes_test(seller_required)
def paket_soal_detail(request, uuid):
    print("Masuk ke paket_soal_detail dengan UUID:", uuid)
    paket = get_object_or_404(PaketSoal, uuid=uuid)
    print("Paket ditemukan:", paket.nama)

    soal_qs = paket.soal.all().order_by('id')
    total_soal = soal_qs.count()
    paginator = Paginator(soal_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    produk_terkait = paket.produks.filter(penjual=request.user).select_related('kategori')
    print(f"Jumlah produk terkait: {produk_terkait.count()}")
    return render(request, 'produk/detail_paket_soal.html', {
        'paket': paket,
        'page_obj': page_obj,
        'soal_list': page_obj.object_list,
        'produk_terkait': produk_terkait,
        'total_soal': total_soal,
        'start_index': page_obj.start_index() if page_obj.paginator.count else 0,
    })


@require_POST
@user_passes_test(seller_required)
def hapus_soal(request, uuid):
    soal = get_object_or_404(
        Soal.objects.select_related('paket__penjual'),
        uuid=uuid,
        paket__penjual=request.user
    )
    paket_uuid = soal.paket.uuid
    soal.delete()
    messages.success(request, "Soal berhasil dihapus.")
    return redirect('paket_soal_detail', paket_uuid)


@user_passes_test(seller_required)
def edit_soal(request, uuid):
    soal = get_object_or_404(
        Soal.objects.select_related('paket__penjual'),
        uuid=uuid,
        paket__penjual=request.user
    )
    if request.method == 'POST':
        form = SoalForm(request.POST, instance=soal)
        if form.is_valid():
            form.save()
            messages.success(request, "Soal berhasil diperbarui.")
            return redirect('paket_soal_detail', soal.paket.uuid)
    else:
        form = SoalForm(instance=soal)
    return render(request, 'produk/edit_soal.html', {'form': form, 'paket': soal.paket, 'soal': soal})

@user_passes_test(seller_required)
@transaction.atomic
def upload_paket_soal(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        nama_paket = request.POST.get('nama_paket')
        deskripsi = request.POST.get('deskripsi')
        produk_ids = request.POST.getlist('produk')  # list of ID

        if not all([excel_file, nama_paket]):
            return render(request, 'produk/upload_excel.html', {'error': 'Lengkapi semua isian'})

        # Simpan paket soal dulu
        paket = PaketSoal.objects.create(nama=nama_paket, deskripsi=deskripsi, penjual=request.user)

        # Relasikan ke produk-produk
        for pid in produk_ids:
            produk = Produk.objects.get(id=pid)
            produk.paket_soal.add(paket)

        # Baca dan simpan soal dari Excel
        wb = openpyxl.load_workbook(excel_file)
        sheet = wb.active

        for row in sheet.iter_rows(min_row=2, values_only=True):
            teks = row[0]
            a = row[1]
            b = row[2]
            c = row[3]
            d = row[4]
            kunci = row[5]
            pembahasan = row[6]

            Soal.objects.create(
                paket=paket,
                teks=teks,
                opsi_a=a,
                opsi_b=b,
                opsi_c=c,
                opsi_d=d,
                jawaban_benar=kunci.upper(),
                pembahasan=pembahasan
            )

        return redirect('upload_paket_soal')  # atau ke dashboard

    # GET request
    semua_produk = Produk.objects.all()
    return render(request, 'produk/upload_excel.html', {'produk_list': semua_produk})
