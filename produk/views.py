from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .forms import ProdukForm
from .models import Produk, PaketSoal, Soal
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
            return redirect('seller_dashboard')  # atau redirect ke daftar produk
    else:
        form = ProdukForm()
    return render(request, 'produk/tambah_produk.html', {'form': form})

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
        paket = PaketSoal.objects.create(nama=nama_paket, deskripsi=deskripsi)

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
