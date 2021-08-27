from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import (authenticate,
                                 login as auth_login,
                                 logout as auth_logout,
                                 get_user_model)
from django.core import exceptions
from django.views.decorators.csrf import csrf_protect
from . import forms
from django.forms import Form
from django.db import IntegrityError
# from django.contrib import messages
from .decorators import *
from django.contrib.auth.models import Group
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
import re
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from smtplib import SMTPException

User = get_user_model()


@csrf_protect
@unauthenticated_user
@sensitive_post_parameters()
@never_cache
def login_user(request):
    form = forms.LoginForm(request.POST or None)
    try:
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            if valid_email(username):
                username = username.lower()
                username = User.objects.get(email=username).username

            active = User.objects.get(username=username).is_active
            if not active:
                return redirect("account:unverified_user")

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


@csrf_protect
@unauthenticated_user
@sensitive_post_parameters()
@never_cache
def register_user(request):
    if request.session.get('successfully_registered') == 1:
        return redirect("account:register_success", permanent=True)
    form = forms.RegisterFrom(request.POST or None)

    try:
        if request.method == "POST":
            if form.is_valid() is True:
                username = form.cleaned_data.get("username")
                email = form.cleaned_data.get("email")
                # this is in case is_email() is stricter than the django forms email validation
                if not valid_email(email):
                    raise ValueError()
                password = form.cleaned_data.get("password2")
                qs1 = User.objects.filter(username=username).count()
                qs2 = User.objects.filter(email=email).count()
                if qs1 == 0 and qs2 == 0:
                    user = User.objects.create_user(username=username, password=password, email=email)
                    request.session['successfully_registered'] = 1
                    group = Group.objects.get(name='member')
                    user.groups.add(group)
                    return redirect("account:register", permanent=True)
    except (exceptions.ValidationError, exceptions.ObjectDoesNotExist, IntegrityError):
        # form.add_error(form.fields['username'], "Something went wrong")
        # form.add_error(form.username, "Something went wrong")
        form.add_error(None, "Something went wrong")
        # return render(request, "account/register.html", {'form': form})
    except ValueError:
        form.add_error("email ", "Please enter a valid email")
        # return render(request, "account/register.html", {'form': form})

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


@csrf_protect
@login_required
@sensitive_post_parameters()
@never_cache
def change_password(request):
    values = {}
    form = forms.ChangePasswordForm(request.POST or None)
    if request.method == 'POST':
        # form = forms.ChangePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('old_password')
            user = authenticate(request, username=request.user.username, password=password)
            if user:
                values['success'] = True
                new_password = form.cleaned_data.get('password2')
                user.set_password(new_password)
                user.save()
            else:
                form.add_error("old_password", "This password is incorrect")
    # else:
    #     form = forms.ChangePasswordForm()

    values['form'] = form
    return render(request, "account/change_password.html", values)


def valid_email(value: str) -> bool:
    valid_email_format = "^(\\w|\\.|\\_|\\-)+[@](\\w|\\_|\\-|\\.)+[.]\\w{2,3}$"
    if re.search(valid_email_format, value):
        return True
    return False


@login_required
@minimum_role_required("moderator")
def moderator_dashboard(request):
    context = {}
    return render(request, "account/dashboard/dashboard.html", context)


@csrf_protect
@login_required
@minimum_role_required("moderator")
def manage_users(request):
    status = 200
    users = User.objects.get_users_up_to_role(User.objects.get_max_role_name(request.user))
    form = Form(request.POST or None)
    context = {
        "activated_user": None,
        "users": users,
        "form": form,
    }
    if request.method == "POST" and form.is_valid():
        if request.POST.get("activate"):
            user_id = request.POST["activate"]
            u = User.objects.get(id=user_id)
            status = _activate_user(user_id)
            context['activated_user'] = u
        elif request.POST.get("deactivate"):
            user_id = request.POST["deactivate"]
            u = User.objects.get(id=user_id)
            status = 0
        context['users'] = User.objects.get_users_up_to_role(User.objects.get_max_role_name(request.user))

    return render(request, "account/dashboard/manage_users.html", context, status=status)


def _activate_user(user_id):
    # todo use class views and make this a class method
    user = User.objects.get(id=user_id)
    if User.objects.activate_user(user):
        try:
            # send email
            context = {"username": user.username}
            html_message = render_to_string('account/email_templates/user_account_activated_email.html',
                                            context=context)
            plain_message = strip_tags(html_message)
            subject = render_to_string("account/email_templates/user_account_activated_subject.txt", context=context)

            send_mail(message=plain_message, recipient_list=[user.email], subject=subject, from_email=None,
                      auth_password=None, html_message=html_message)
        except SMTPException:
            print("failed to notify user of account action")
        return 201
    else:
        return 500


def _deactivate_user(user_id):
    """
    user = User.objects.get(id=user_id)
    if User.objects.activate_user(user):
        try:
            # todo make deactivation email
            # context = {"username": user.username}
            # html_message = render_to_string('account/email_templates/user_account_activated_email.html',
            #                                 context=context)
            # plain_message = strip_tags(html_message)
            # subject = render_to_string("account/email_templates/user_account_activated_subject.txt", context=context)
            #
            # send_mail(message=plain_message, recipient_list=[user.email], subject=subject, from_email=None,
            #           auth_password=None, html_message=html_message)
            return 201
        except SMTPException:
            print("failed to notify user of account action")
    else:
        return 500
    """
    return 500
