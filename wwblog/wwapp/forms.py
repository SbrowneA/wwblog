from django import forms


class Login(forms.Form):
    username = forms.CharField(label="Username", max_length=14)
    # email = forms.CharField(label="Email", max_length=150)
    password = forms.CharField(label="Password", max_length=45)
    # password_confirm = forms.CharField(label="Confirm-Password", max_length=45)


class Register(forms.Form):
    pass


class EditCategory(forms.Form):
    # category_name = forms.CharField()
    pass
