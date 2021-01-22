from django.contrib import admin
from .models import *
from tinymce.widgets import TinyMCE


class TinyMCEAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }


admin.site.register(User)
admin.site.register(Article, TinyMCEAdmin)
admin.site.register(Category)
admin.site.register(CategoryEditor)
admin.site.register(CategoryItem)
# admin.site.register(CategoryItemAssignation)



