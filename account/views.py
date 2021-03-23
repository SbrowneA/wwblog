from django.shortcuts import render, redirect
from django.contrib.auth import (authenticate,
                                 login as auth_login,
                                 logout as auth_logout,
                                 get_user_model)
from django.core import exceptions
# Create your views here.
from . import forms
from django.db import IntegrityError
from django.contrib import messages
from .decorators import *
from django.contrib.auth.models import Group

User = get_user_model()


@unauthenticated_user
def login_user(request):
    form = forms.LoginForm(request.POST or None)
    try:
        if form.is_valid():
            # print("form is valid")
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            if "@" in username:
                username = User.objects.get(email=username).username

            active = User.objects.get(username=username).is_active
            if not active:
                # print("exists but is not active ")
                return redirect("wwapp:unverified_user")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request=request, user=user)
                return redirect("wwapp:index")
            # check number of attempts a user has made within a session
            # attempt = request.session.get("attempt") or 0
            # request.session.['attempt'] = attempt + 1
            # request.session['invalid_user'] = 1
            form.add_error(None, "Email/username or password are incorrect.")
        return render(request, "account/login.html", {'form': form})
    except exceptions.ObjectDoesNotExist:
        form.add_error(None, "Email/username or password are incorrect.")
        request.session['invalid_user'] = 1
        return render(request, "account/login.html", {'form': form})


def logout_user(request):
    auth_logout(request)
    return redirect("wwapp:index")


@unauthenticated_user
def register_user(request):
    if request.session.get('successfully_registered') == 1:
        return redirect("wwapp:register_success", permanent=True)
    form = forms.RegisterFrom(request.POST or None)

    try:
        if form.is_valid() is True:
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password2")
            qs1 = User.objects.filter(username=username).count()
            qs2 = User.objects.filter(email=email).count()
            if qs1 == 0 and qs2 == 0:
                user = User.objects.create_user(username=username, password=password, email=email)
                request.session['successfully_registered'] = 1
                group = Group.objects.get(name='member')
                user.groups.add(group)
                return redirect("wwapp:register_success", permanent=True)
    except (exceptions.ValidationError, exceptions.ObjectDoesNotExist, IntegrityError):
        # form.add_error(form.fields['username'], "Something went wrong")
        # form.add_error(form.username, "Something went wrong")
        form.add_error(None, "Something went wrong")
        return render(request, "account/register.html", {'form': form})

    return render(request, "account/register.html", {'form': form})


@unauthenticated_user
def register_success(request):
    success = request.session.get('successfully_registered') or 0
    if success == 1:
        return render(request, "account/register_success.html")
    else:
        return redirect("wwapp:index")


@unauthenticated_user
def unverified_user(request):
    request.session['successfully_registered'] = 1
    return render(request, "account/unactivated_account.html")
