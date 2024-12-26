from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .forms import SignUpForm
from .models import User



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            print("Se va a loggear")
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                return HttpResponse('Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/login')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'], name=form.cleaned_data['name'])
            messages.success(request, 'User registered successfully!')
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})
