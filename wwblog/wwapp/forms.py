from django import forms
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

class ArticleEdit(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    secret_note = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    # publish_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control'}))
    # needs to be cleaned to make sure users in list are not author or already an editor
    # add_editor = forms.Select(attrs={'class': 'form-control'})

    content = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30,
                              'class': 'tiny-mce-editor', 'id': 'tiny-mce'}))


# class TestArticle(forms.ModelForm):
#     content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30,
#                                                     'class': 'tiny-mce-editor', 'id': 'tiny-mce'}))
#
#     class Meta:
#         model = FlatPage
#         fields = ['content']
