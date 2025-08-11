from django.contrib.auth.decorators import login_required
from produk.models import PaketSoal
from toko.models import Order
from cbt.models import HasilUjian
from django.shortcuts import render, get_object_or_404, redirect
from produk.models import Produk
from django.http import HttpResponse
from cbt.models import Soal, JawabanUjian



@login_required
def daftar_paket_ujian(request):
    return render(request, 'cbt/daftar_paket.html', {
        'paket_list': PaketSoal.objects.all(),
        'hasil_dict': {hasil.paket.id: hasil for hasil in HasilUjian.objects.filter(user=request.user)}
    })


@login_required
def kerjakan_paket(request, uuid):
    paket = get_object_or_404(PaketSoal, uuid=uuid)
    soal_list = Soal.objects.filter(paket=paket)

    # 🔐 Cek apakah user sudah beli produk yang mengandung paket ini
    orders = Order.objects.filter(user=request.user).prefetch_related('items__produk__paket_soal')
    sudah_beli = False
    for order in orders:
        for item in order.items.all():
            if paket in item.produk.paket_soal.all():
                sudah_beli = True
                break
    if not sudah_beli:
        return render(request, 'cbt/tidak_berhak.html')

    # 🔁 Cek apakah user sudah pernah mengerjakan
    # if HasilUjian.objects.filter(user=request.user, paket=paket).exists():
    #     return redirect('paket_per_produk', uuid=item.produk.uuid)

    # 📝 Proses pengerjaan
    if request.method == 'POST':
        benar = 0
        total = soal_list.count()
        hasil = HasilUjian.objects.create(user=request.user, paket=paket, nilai=0)

        for soal in soal_list:
            jawaban = request.POST.get(f"soal_{soal.id}")
            is_benar = jawaban == soal.jawaban_benar
            if is_benar:
                benar += 1

            JawabanUjian.objects.create(
                hasil=hasil,
                soal=soal,
                jawaban_dipilih=jawaban,
                benar=is_benar
            )

        nilai_akhir = round((benar / total) * 100, 2)
        hasil.nilai = nilai_akhir
        hasil.save()

        return redirect('hasil_ujian', hasil.uuid)

    return render(request, 'cbt/kerjakan.html', {
        'paket': paket,
        'soal_list': soal_list
    })

@login_required
def hasil_ujian(request, uuid):
    hasil = get_object_or_404(HasilUjian, uuid=uuid, user=request.user)
    jawaban_list = hasil.jawaban.select_related('soal').all()

    return render(request, 'cbt/hasil_ujian.html', {
        'hasil': hasil,
        'jawaban_list': jawaban_list,
    })



@login_required
def daftar_paket_per_produk(request, uuid):
    produk = get_object_or_404(Produk, uuid=uuid)

    # Cek apakah user beli produk ini
    sudah_beli = Order.objects.filter(
        user=request.user,
        items__produk=produk
    ).exists()
    if not sudah_beli:
        return render(request, 'cbt/tidak_berhak.html')

    paket_list = produk.paket_soal.all()

    # Susun statistik per paket
    statistik_paket = {}
    for paket in paket_list:
        hasil_list = HasilUjian.objects.filter(user=request.user, paket=paket)
        jumlah = hasil_list.count()
        rata2 = round(sum(h.nilai for h in hasil_list) / jumlah, 2) if jumlah else 0

        statistik_paket[paket.id] = {
            'jumlah': jumlah,
            'rata_rata': rata2,
            'hasil_terakhir': hasil_list.last() if jumlah else None
        }


    return render(request, 'cbt/paket_per_produk.html', {
        'produk': produk,
        'paket_list': paket_list,
        'statistik_paket': statistik_paket,
    })

