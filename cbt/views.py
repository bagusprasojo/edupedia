import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from cbt.models import HasilUjian, JawabanUjian, Soal
from produk.models import PaketSoal, Produk
from toko.models import Order

ANSWER_CHOICES = {'A', 'B', 'C', 'D'}


def _progress_session_key(user_id, paket_id):
    return f"cbt_progress_{user_id}_{paket_id}"


def _user_has_access(user, paket):
    return Order.objects.filter(
        user=user,
        items__produk__paket_soal=paket
    ).exists()


def _init_progress_session(request, paket):
    session_key = _progress_session_key(request.user.id, paket.id)
    progress = request.session.get(session_key)
    if not progress or not isinstance(progress, dict):
        progress = {'answers': {}}
    elif 'answers' not in progress:
        progress['answers'] = {}
    request.session[session_key] = progress
    return session_key, progress


def _store_answer(request, paket, soal_id, jawaban):
    jawaban = (jawaban or '').strip().upper()
    if jawaban not in ANSWER_CHOICES:
        return None

    session_key, progress = _init_progress_session(request, paket)
    answers = progress.setdefault('answers', {})
    answers[str(soal_id)] = jawaban
    request.session[session_key] = progress
    request.session.modified = True
    return progress


def _clear_progress(request, paket):
    session_key = _progress_session_key(request.user.id, paket.id)
    if session_key in request.session:
        del request.session[session_key]
        request.session.modified = True


def _resolve_question_number(request, total_soal):
    raw_value = request.GET.get('nomor', 1)
    if request.method == 'POST':
        raw_value = request.POST.get('current_number', raw_value)
    try:
        number = int(raw_value)
    except (TypeError, ValueError):
        number = 1

    if total_soal <= 0:
        return 1
    return max(1, min(total_soal, number))


def _question_url(paket_uuid, nomor):
    base = reverse('kerjakan_paket', args=[paket_uuid])
    return f"{base}?nomor={nomor}"


@login_required
def daftar_paket_ujian(request):
    return render(request, 'cbt/daftar_paket.html', {
        'paket_list': PaketSoal.objects.all(),
        'hasil_dict': {hasil.paket.id: hasil for hasil in HasilUjian.objects.filter(user=request.user)}
    })


@login_required
def kerjakan_paket(request, uuid):
    paket = get_object_or_404(PaketSoal, uuid=uuid)
    if not _user_has_access(request.user, paket):
        return render(request, 'cbt/tidak_berhak.html')

    soal_list = list(Soal.objects.filter(paket=paket).order_by('id'))
    total_soal = len(soal_list)
    if total_soal == 0:
        messages.warning(request, "Paket ini belum memiliki soal yang bisa dikerjakan.")
        return redirect('daftar_paket_ujian')

    session_key, progress = _init_progress_session(request, paket)
    answers = progress.get('answers', {})
    current_number = _resolve_question_number(request, total_soal)
    current_soal = soal_list[current_number - 1]

    if request.method == 'POST':
        action = request.POST.get('action')
        soal_id = request.POST.get('soal_id')
        selected_answer = request.POST.get('selected_answer')
        if soal_id and selected_answer:
            _store_answer(request, paket, soal_id, selected_answer)
            answers = request.session.get(session_key, {}).get('answers', {})

        if action == 'final_submit':
            return _finish_attempt(request, paket, soal_list, answers)

        if action == 'save_prev' and current_number > 1:
            return redirect(_question_url(paket.uuid, current_number - 1))
        if action == 'save_next' and current_number < total_soal:
            return redirect(_question_url(paket.uuid, current_number + 1))

    answered_count = sum(1 for value in answers.values() if value in ANSWER_CHOICES)
    unanswered_count = max(total_soal - answered_count, 0)
    progress_percent = int((answered_count / total_soal) * 100) if total_soal else 0

    palette = []
    for index, soal in enumerate(soal_list, start=1):
        status = 'answered' if answers.get(str(soal.id)) in ANSWER_CHOICES else 'unanswered'
        palette.append({
            'number': index,
            'soal_id': soal.id,
            'status': status,
            'url': _question_url(paket.uuid, index),
        })

    context = {
        'paket': paket,
        'current_soal': current_soal,
        'current_number': current_number,
        'total_soal': total_soal,
        'selected_answer': answers.get(str(current_soal.id), ''),
        'answered_count': answered_count,
        'unanswered_count': unanswered_count,
        'progress_percent': progress_percent,
        'has_prev': current_number > 1,
        'has_next': current_number < total_soal,
        'prev_number': current_number - 1,
        'next_number': current_number + 1,
        'question_palette': palette,
        'ajax_save_url': reverse('cbt_update_jawaban', args=[paket.uuid]),
    }

    return render(request, 'cbt/kerjakan.html', context)


def _finish_attempt(request, paket, soal_list, answers):
    total = len(soal_list)
    if total == 0:
        messages.warning(request, "Tidak ada soal untuk diselesaikan.")
        return redirect('daftar_paket_ujian')

    hasil = HasilUjian.objects.create(user=request.user, paket=paket, nilai=0)
    benar = 0

    for soal in soal_list:
        pilihan = answers.get(str(soal.id))
        is_benar = pilihan == soal.jawaban_benar if pilihan in ANSWER_CHOICES else False
        if is_benar:
            benar += 1
        JawabanUjian.objects.create(
            hasil=hasil,
            soal=soal,
            jawaban_dipilih=pilihan if pilihan in ANSWER_CHOICES else None,
            benar=is_benar,
        )

    nilai_akhir = round((benar / total) * 100, 2) if total else 0
    hasil.nilai = nilai_akhir
    hasil.save()
    _clear_progress(request, paket)
    return redirect('hasil_ujian', hasil.uuid)


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

    sudah_beli = Order.objects.filter(
        user=request.user,
        items__produk=produk
    ).exists()
    if not sudah_beli:
        return render(request, 'cbt/tidak_berhak.html')

    paket_list = produk.paket_soal.all()

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


@login_required
@require_http_methods(["PATCH"])
def update_jawaban_ajax(request, uuid):
    paket = get_object_or_404(PaketSoal, uuid=uuid)
    if not _user_has_access(request.user, paket):
        return JsonResponse({'error': 'Anda tidak memiliki akses ke paket ini.'}, status=403)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Payload tidak valid.'}, status=400)

    soal_id = payload.get('soal_id')
    jawaban = payload.get('jawaban')
    if not soal_id or not jawaban:
        return JsonResponse({'error': 'soal_id dan jawaban wajib diisi.'}, status=400)

    soal = get_object_or_404(Soal, id=soal_id, paket=paket)
    progress = _store_answer(request, paket, soal.id, jawaban)
    if progress is None:
        return JsonResponse({'error': 'Pilihan jawaban tidak dikenal.'}, status=400)

    total_soal = Soal.objects.filter(paket=paket).count()
    answered = sum(1 for value in progress.get('answers', {}).values() if value in ANSWER_CHOICES)
    percent = int((answered / total_soal) * 100) if total_soal else 0

    return JsonResponse({
        'status': 'ok',
        'answered': answered,
        'unanswered': max(total_soal - answered, 0),
        'progress_percent': percent,
        'soal_id': soal.id,
    })
