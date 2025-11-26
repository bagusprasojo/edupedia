from django import forms
from .models import Produk, Soal


class ProdukForm(forms.ModelForm):
    class Meta:
        model = Produk
        fields = ['nama', 'deskripsi', 'harga', 'gambar', 'kategori']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'harga': forms.NumberInput(attrs={'class': 'form-control'}),
            'kategori': forms.Select(attrs={'class': 'form-control'}),
            'gambar': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            
        }


class SoalForm(forms.ModelForm):
    class Meta:
        model = Soal
        fields = ['teks', 'opsi_a', 'opsi_b', 'opsi_c', 'opsi_d', 'jawaban_benar', 'pembahasan']
        widgets = {
            'teks': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'opsi_a': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'opsi_b': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'opsi_c': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'opsi_d': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'jawaban_benar': forms.Select(attrs={'class': 'form-select'}),
            'pembahasan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
