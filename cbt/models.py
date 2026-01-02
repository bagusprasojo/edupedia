from django.db import models
from django.conf import settings
from produk.models import PaketSoal, Soal
import uuid

class HasilUjian(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    paket = models.ForeignKey(PaketSoal, on_delete=models.CASCADE)
    nilai = models.FloatField()
    waktu_selesai = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.paket.nama} - {self.nilai}"

class JawabanUjian(models.Model):
    hasil = models.ForeignKey(HasilUjian, on_delete=models.CASCADE, related_name='jawaban')
    soal = models.ForeignKey(Soal, on_delete=models.CASCADE)
    jawaban_dipilih = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        blank=True,
        null=True,
    )
    benar = models.BooleanField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Soal #{self.soal.id} - {self.jawaban_dipilih} - {'Benar' if self.benar else 'Salah'}"
