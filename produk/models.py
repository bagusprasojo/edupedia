from django.db import models
from accounts.models import User
import uuid
import os
from mptt.models import MPTTModel, TreeForeignKey


def upload_to_uuid(instance, filename):
    ext = filename.split('.')[-1]  # Ambil ekstensi file
    filename = f"{uuid.uuid4().hex}.{ext}"  # Hasil: 6ad6cf424b0b4e30bb6d5a1c41c43d6b.jpg
    return os.path.join("produk_images", filename)


# class Kategori(MPTTModel):
#     nama = models.CharField(max_length=100)
#     parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

#     class MPTTMeta:
#         order_insertion_by = ['nama']

class Kategori(models.Model):
    nama = models.CharField(max_length=100)
    uuid = models.UUIDField(default=uuid.uuid4,editable=False,unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subkategori'
    )

    def __str__(self):
        return f"{self.parent.nama} > {self.nama}" if self.parent else self.nama


class Produk(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    penjual = models.ForeignKey(User, on_delete=models.CASCADE, related_name='produknya')
    nama = models.CharField(max_length=200)
    deskripsi = models.TextField()
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    gambar = models.ImageField(upload_to=upload_to_uuid, null=True, blank=True)
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True, blank=True)
    paket_soal = models.ManyToManyField('PaketSoal', blank=True, related_name='produks')
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    tanggal_diperbarui = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama

class PaketSoal(models.Model):
    nama = models.CharField(max_length=200)
    deskripsi = models.TextField(blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.nama

class Soal(models.Model):
    paket = models.ForeignKey(PaketSoal, on_delete=models.CASCADE, related_name='soal')
    teks = models.TextField()

    opsi_a = models.CharField(max_length=500)
    opsi_b = models.CharField(max_length=500)
    opsi_c = models.CharField(max_length=500)
    opsi_d = models.CharField(max_length=500)

    JAWABAN_CHOICES = [
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ]
    jawaban_benar = models.CharField(max_length=1, choices=JAWABAN_CHOICES)
    pembahasan = models.TextField(blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Soal #{self.id} - {self.teks[:30]}"

