from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('post/<int:article_id>/view/', views.open_article, name='open_article'),
    path('post/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('user/<int:user_id>/details/', views.user_details, name='user_details'),
    path('login/', views.login, name='login'),
    # path('category/all', views.category_all, name='category_all'),
    # path('category/<str:category_name>/edit', views.category_edit, name='category_edit'),
    # path('category/<str:category_name>/view', views.category_open, name='category_open'),
]
