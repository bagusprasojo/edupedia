from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from .forms import LoginForm
from toko.models import Order

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
    return render(request, 'accounts/seller_dashboard.html')


@user_passes_test(buyer_required)
def buyer_dashboard(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items', 'items__produk')
    total_produk = sum(order.items.count() for order in orders)
    return render(request, 'accounts/buyer_dashboard.html', {'orders': orders, 'total_produk': total_produk })
