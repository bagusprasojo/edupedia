from .models import KeranjangItem

def cart_item_count(request):
    if request.user.is_authenticated:
        count = KeranjangItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'cart_count': count}