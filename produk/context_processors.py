from produk.models import Kategori

def kategori_context(request):
    kategori_root = Kategori.objects.filter(parent__isnull=True)
    # print("Kategori Context:", kategori_root)  # Debugging line

    return {'kategori_root': kategori_root}
