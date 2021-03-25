from django.contrib.auth import get_user_model
from django import forms
from django.core import exceptions

User = get_user_model()


def is_blacklisted_domain(address):
    domain = address.split("@")[1]
    with open("blacklisted-domains.csv", "r") as file:
        for line in file:
            if domain in line:
                return True
    return False


class LoginForm(forms.Form):
    username = forms.CharField(label="Username or Email",
                               widget=forms.TextInput(
                                   attrs={"class": 'form-control'}))
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput(attrs={"class": 'form-control'}))

    # def clean(self):
    #     cleaned_data = super().clean()
    #     username = self.cleaned_data.get("username")
    #     password = self.cleaned_data.get("password")

    # def clean_username(self):
    #     try:
    #         username = self.cleaned_data.get("username")
    #         # if username is not None:
    #         if "@" in username:
    #             check = User.objects.get(email="username").username
    #         User.objects.get(username=username)
    #         return username
    #     except (forms.ValidationError,  exceptions.ObjectDoesNotExist):
    #         raise forms.ValidationError("Email/Username or password are incorrect - form")


class RegisterFrom(forms.Form):
    username = forms.CharField(label="Username",
                               widget=forms.TextInput(attrs={"class": 'form-control'}))
    email = forms.EmailField(label="Email",
                             widget=forms.EmailInput(attrs={"class": 'form-control'}))
    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput(attrs={"class": 'form-control'}))
    password2 = forms.CharField(label="Confirm Password",
                                widget=forms.PasswordInput(attrs={"class": 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        username = self.clean_username()
        email = self.clean_email()
        password2 = clean_password2(cleaned_data)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # try:
        # if is_blacklisted_domain(email):
        #     raise forms.ValidationError("Please enter a valid email")
        num = User.objects.filter(email=email).count()
        if num == 0:
            return email
        else:
            raise forms.ValidationError("Please enter a valid email")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        num = User.objects.filter(username=username).count()
        if num == 0:
            return username
        raise forms.ValidationError("Please enter a valid username")


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(label="New Password",
                                widget=forms.PasswordInput(attrs={"class": 'form-control'}))
    password2 = forms.CharField(label="Confirm Password",
                                widget=forms.PasswordInput(attrs={"class": 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        password2 = clean_password2(cleaned_data)


class SendRecoveryEmailForm(forms.Form):
    email = old_password = forms.EmailField(label="Old Password",
                                            widget=forms.EmailInput(attrs={"class": 'form-control'}))


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label="Old Password",
                                   widget=forms.PasswordInput(attrs={"class": 'form-control'}))

    password1 = forms.CharField(label="New Password",
                                widget=forms.PasswordInput(attrs={"class": 'form-control'}))
    password2 = forms.CharField(label="Confirm Password",
                                widget=forms.PasswordInput(attrs={"class": 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        password2 = clean_password2(cleaned_data)


def clean_password2(cleaned_data):
    password1 = cleaned_data.get("password1")
    password2 = cleaned_data.get("password2")
    if password1 != password2:
        raise forms.ValidationError("Passwords do not match")
    return password2
