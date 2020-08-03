from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, redirect

from users.models import User
from .forms import SignUpForm, FormLogin
from .services import data_validation

LOGIN_URL = 'auth:login'
SIGN_UP_URL = 'auth:sign_up'


def log_in(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('main-page')
        else:
            return render(request, 'LoginPage.html', context={'form': FormLogin()})
    elif request.method == 'POST':
        form = FormLogin(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('main-page')
            else:
                messages.add_message(request, messages.WARNING, 'Incorrect email or password')
                return redirect(LOGIN_URL)


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(LOGIN_URL)
    else:
        return redirect('main-page')


def sign_up(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('main-page')
        else:
            return render(request, 'SignUp.html', context={'form': SignUpForm()})
    else:
        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        moderator = request.POST.get('moderator', False)
        error = data_validation(request)
        if error is not None:
            messages.add_message(request, messages.WARNING, error)
            return redirect(SIGN_UP_URL)
        try:
            user = User.objects.create_user(email=email, password=password)
        except IntegrityError:
            messages.add_message(request, messages.WARNING, 'That email has already taken')
            return redirect(SIGN_UP_URL)
        if user is not None:
            user.name = username
            if moderator:
                user.is_moderator = True
            user.save()
            return redirect(LOGIN_URL)
        else:
            return redirect(SIGN_UP_URL)
