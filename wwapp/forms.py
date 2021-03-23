from django import forms
# from django.contrib.flatpages.models import FlatPage
from tinymce.widgets import TinyMCE


# from .models import Category


class CategoryEdit(forms.Form):
    # TODO use init func to set initial instead of setting initial from view
    # def __init__(self, name: str, description=""):
    # category_name

    category_name = forms.CharField(required=True,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}))
    new_category_name = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'New Title', 'initial': ''}))
    category_description = forms.CharField(required=False,
                                           widget=forms.Textarea(
                                               attrs={'class': 'form-control', 'placeholder': 'Description (optional)',
                                                      'initial': '', 'rows': '2'}))
    parent_category_select = forms.Select(choices=[])

    def clean(self):
        super().clean()
        category_description = self.clean_category_description()

    def clean_category_description(self):
        category_description = self.cleaned_data.get('category_description')
        if category_description:
            num = len(category_description)
            if num <= 300:
                return category_description
            else:
                raise forms.ValidationError(
                    f"Description must be less than 300 characters (currently {num} characters long)")

    # def clean(self):
    #     super().clean()
    #     category_name = self.cleaned_data.get('category_name')
    #     new_category_name = self.clean_new_category_name()
    #     parent_category_select = self.cleaned_data.get('parent_category_select')
    #
    # def clean_new_category_name(self):
    #     new_category_name = self.cleaned_data.get('new_category_name')
    #     cats = Category.objects.filter(category_name=new_category_name)
    #     if len(cats) > 0 and new_category_name != "":
    #         raise forms.ValidationError("The title must be unique")
    #     return new_category_name


class ArticleEdit(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}))
    placeholder = 'place any secret notes here..\n WARNING: the author, all the editors on this post,' \
                  ' and moderators can read this '
    secret_note = forms.CharField(label='secret notes', required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': placeholder, }))
    # publish_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control'}))
    # needs to be cleaned to make sure users in list are not author or already an editor
    # add_editor = forms.Select(attrs={'class': 'form-control'})
    parent_article = forms.Select(choices=[])
    categories_select = forms.Select(choices=[])
    # publish_to_select = forms.Select(choices=CHOICES)
    # publish_to_select = forms.ChoiceField(choices=[])
    publish_to_select = forms.ChoiceField(required=False, choices=[])
    # editors = forms.ModelMultipleChoiceField(queryset=None,
    #                                          widget=forms.ModelMultipleChoiceField(attrs={'class': 'form-control'}))
    content = forms.CharField(required=False,
                              widget=TinyMCE(attrs={'cols': 80, 'rows': 30,
                                                    'class': 'tiny-mce-editor', 'id': 'tiny-mce'}))

    # def clean:
    #
    #     if "publish_article" in form.data:


class TestEmail(forms.Form):
    subject = forms.CharField(required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}))
    recipient = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipient'}))
    body = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'message'}))
