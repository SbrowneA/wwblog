from django import forms
from .models import *
from django.contrib.flatpages.models import FlatPage
from tinymce.widgets import TinyMCE


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

class TestArticle2(forms.Form):
    content = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30,
                              'class': 'tiny-mce-editor', 'id': 'tiny-mce'}))


class TestArticle(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30, 'class': 'tiny-mce-editor', 'id': 'tiny-mce'}))

    class Meta:
        model = FlatPage
        fields = ['content']


# class ArticleVersionForm(forms.ModelForm):
#     class Meta:
#         model = ArticleVersion
#         fields = ('content', '')
#
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'author': forms.Select(attrs={'class': 'form-control'}),
#         }
