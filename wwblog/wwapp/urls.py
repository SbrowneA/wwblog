from django.urls import path
from . import views
from account import views as account_views

# from django.conf.urls.static import static
# from django.conf import settings

app_name = 'wwapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', account_views.login_user, name='login'),
    path('logout/', account_views.logout_user, name='logout'),
    path('register/', account_views.register_user, name='register'),
    path('register/success', account_views.register_success, name='register_success'),
    path('unverified', account_views.unverified_user, name='unverified_user'),
    path('post/create', views.create_new_article, name='new_article'),
    path('post/<int:article_id>/view', views.open_article, name='open_article'),
    path('post/<int:article_id>/edit', views.edit_article, name='edit_article'),
    path('post/<int:article_id>/delete', views.delete_article, name='delete_article'),
    path('post/me', views.manage_own_content, name='manage_own_content'),
    # path('post/browse', views.browse_articles, name='browse_articles'),
    # path('author/browse', views.browse_users, name='browse_users'),
    # path('author/<int:user_id>/details', views.user_details, name='user_details'),
    # path('category/browse', views.browse_categories, name='browse_categories'),
    # path('category/<int:category_id>/view', views.open_category, name='open_category'),
    path('category/<int:category_id>/edit', views.edit_category, name='edit_category'),
    # path('category/<int:category_id>/new', views.create_sub_category, name='add_sub_category'),
    path('category/<int:category_id>/delete', views.delete_category, name='delete_category'),
    path('category/<int:category_id>/delete/<int:child_id>', views.delete_child_category, name='add_sub_category'),
    path('category/createproject', views.create_project, name='new_project'),
    # path('test', views.image_upload_test, name='upload_test'),
    # path('edit', views.editor_test, name='editor_test'),
]
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
