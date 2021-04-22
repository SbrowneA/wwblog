from django.urls import path
from . import views

from django.conf.urls.static import static
from django.conf import settings

app_name = 'wwapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('post/create/', views.create_new_article, name='new_article'),
    path('post/<int:article_id>/view/', views.open_article, name='open_article'),
    path('post/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('post/<int:article_id>/delete/', views.delete_article, name='delete_article'),
    path('post/<int:article_id>/draft/', views.draft_article, name='draft_article'),
    path('me/', views.manage_own_content, name='manage_own_content'),
    path('me/images', views.browse_own_images, name='browse_own_images'),
    # path('post/browse', views.browse_articles, name='browse_articles'),
    # path('author/browse', views.browse_users, name='browse_users'),
    # path('user/<string:username>/details', views.user_details, name='user_details'),
    # path('category/browse', views.browse_categories, name='browse_categories'),
    path('category/<int:category_id>/view', views.open_category, name='open_category'),
    path('category/<int:category_id>/edit', views.edit_category, name='edit_category'),
    # path('category/<int:category_id>/new', views.create_sub_category, name='add_sub_category'),
    path('category/<int:category_id>/delete', views.delete_category, name='delete_category'),
    path('category/<int:category_id>/delete/<int:child_id>', views.delete_child_category, name='add_sub_category'),
    path('category/createproject', views.create_project, name='new_project'),
    # path('test', views.image_upload_test, name='upload_test'),
    # path('moderators/activate', views.activate_users, name="activate"),
    # path('moderators/dashboard', views.activate_users, name="activate"),
    # path('test', views.send_email_test, name='email_test'),
    path('image/imgur-upload', views.upload_image, name='upload_image'),
    # path('image/<int:image_id>/delete', views.delete_image, name='delete_image'),
    path('upload-to-imgur', views.upload_imgur_image, name="upload_to_imgur"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
the following urls cannot bee changed without making adjustments to dependent code
category and article(post) urls:
- decorators require format: '../<content_type>/<id>/<action>' 
- delete urls are statically referenced in JS in Head tag
"""