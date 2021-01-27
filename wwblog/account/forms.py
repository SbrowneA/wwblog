from django.contrib.auth import get_user_model
from django import forms
from django.core import exceptions

User = get_user_model()


# blacklisted_email_providers = ("yopmail","gorillamail")


class LoginForm(forms.Form):
    # todo allow email login as well
    username = forms.CharField(label="Username or Email",
                               widget=forms.TextInput(attrs={"class": 'form-control'}))
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput(attrs={"class": 'form-control'}))
    def clean(self):
        cleaned_data = super().clean()
        username = self.clean_username()
        password = self.cleaned_data.get("password")

    def clean_username(self):
        try:
            username = self.cleaned_data.get("username")
            if username is not None:
                if "@" in username:
                    username = User.objects.get(email="username").username
                User.objects.get(username=username)
                return username
        except (forms.ValidationError,  exceptions.ObjectDoesNotExist):
            raise forms.ValidationError("Email/Username or password are incorrect")


class RegisterFrom(forms.Form):
    username = forms.CharField(label="Username",
                               widget=forms.TextInput(attrs={"class": 'form-control'}))
    email = forms.EmailField(label="Email",
                             widget=forms.EmailInput(attrs={"class": 'form-control'}))
    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput(attrs={"class": 'form-control'}))
    password2 = forms.CharField(label="Confirm Password",
                                widget=forms.PasswordInput(attrs={"class": 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data.get("email")

        try:
            u = User.objects.get(email=email)
            raise forms.ValidationError("in use")
            # raise ValueError("in use")
        except forms.ValidationError:
            raise forms.ValidationError("Please enter a valid email address")
        except exceptions.ObjectDoesNotExist:
            return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        try:
            User.objects.get(username=username)
            raise forms.ValidationError("Please enter a valid username")
        except forms.ValidationError:
            raise forms.ValidationError("Please enter a valid username")
        except exceptions.ObjectDoesNotExist:
            return username

    def clean_password(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return password1, password2


