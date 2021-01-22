from django import forms
from .models import *
# from django.contrib.flatpages.models import FlatPage
# from tinymce.widgets import TinyMCE


class Login(forms.Form):
    username = forms.CharField(label="Username", max_length=14)
    # email = forms.CharField(label="Email", max_length=150)
    password = forms.CharField(label="Password", max_length=45)
    # password_confirm = forms.CharField(label="Confirm-Password", max_length=45)

#
# class Register(forms.Form):
#     pass
#
#
# class EditCategory(forms.Form):
#     # category_name = forms.CharField()
#     pass


# class ArticleForm(forms.ModelForm):
#     content = forms.CharField(
#         widget=TinyMCE(attrs={'cols': 100, 'rows': 60})
#     )
#
#     class Meta:
#         model = FlatPage
#         # model = ArticleVersion
#         # fields = ('title', 'author')
#         #
#         # widgets = {
#         #     'title': forms.TextInput(attrs={'class': 'form-control'}),
#         #     'author': forms.Select(attrs={'class': 'form-control'}),
#         # }



# class ArticleVersionForm(forms.ModelForm):
#     class Meta:
#         model = ArticleVersion
#         fields = ('content', '')
#
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'author': forms.Select(attrs={'class': 'form-control'}),
#         }
