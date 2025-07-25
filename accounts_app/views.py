from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('accounts_app:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('accounts_app:register')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('exporters_app:home')  # or your homepage

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('exporters_app:home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('accounts_app:login')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request,"You have successfuly logged out.")
    return redirect('exporters_app:home')
