from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('post/<int:article_id>/view', views.open_article, name='open_article'),
    path('post/<int:article_id>/edit', views.edit_article, name='edit_article'),
    path('post/browse', views.browse_articles, name='browse_articles'),
    path('author/browse', views.browse_users, name='browse_users'),
    path('author/<int:user_id>/details', views.user_details, name='user_details'),
    path('login', views.login, name='login'),
    path('category/browse', views.browse_categories, name='browse_categories'),
    path('category/<int:category_id>/view', views.open_category, name='open_category'),
    # path('category/<str:category_name>/edit', views.edit_category, name='edit_category'),
]
