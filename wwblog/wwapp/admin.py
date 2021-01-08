from django.contrib import admin
from .models import *
# from .models import \
#     User,\
#     Article,\
#     ArticleEditor,\
#     Category,\

admin.site.register(User)
admin.site.register(Article)
admin.site.register(Category)
admin.site.register(CategoryEditor)
admin.site.register(CategoryItem)
admin.site.register(CategoryItemAssignation)
admin.site.register(ArticleEditor)

