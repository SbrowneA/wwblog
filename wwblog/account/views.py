from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.core import exceptions
# Create your views here.
from . import forms
from django.db import IntegrityError
from django.contrib import messages
User = get_user_model()


def login_user(request):
    form = forms.LoginForm(request.POST or None)
    try:
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            if "@" in username:
                username = User.objects.get(email=username).username

            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request=request, user=user)
                return redirect("wwapp:index")
            # check number of attempts a user has made within a session
            # attempt = request.session.get("attempt") or 0
            # request.session.['attempt'] = attempt + 1
            # request.session['invalid_user'] = 1
        return render(request, "account/login.html", {'form': form})
    except exceptions.ObjectDoesNotExist:
        messages.error(request, "Error")
        request.session['invalid_user'] = 1
        return render(request, "account/login.html", {'form': form})


def logout_user(request):
    auth_logout(request)
    return redirect("wwapp:index")


def register_user(request):
    values = {}
    form = forms.RegisterFrom(request.POST or None)

    try:
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password2")
            password2 = form.cleaned_data.get("password2")
            qs1 = User.objects.filter(username=username).count()
            qs2 = User.objects.filter(email=email).count()
            if password == password2 and qs1 == 0 and qs2 == 0:
                # user = \
                User.objects.create_user(username=username, password=password, email=email)
                return redirect("wwapp:register_success")
            # check number of attempts a user has made within a session
            # attempt = request.session.get("attempt") or 0
            # request.session.['attempt'] = attempt + 1
            request.session['failed_registration'] = 1
            # values['form'] = form
            # raise exceptions.ValidationError
    except IntegrityError:
        pass
    # except (exceptions.ValidationError, exceptions.ObjectDoesNotExist):
    #     return render(request, "account/login.html", values)
    values['form'] = form
    return render(request, "account/register.html", values)


def register_success(request):
    return render(request, "account/register_success.html")
