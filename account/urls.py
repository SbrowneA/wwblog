from django.urls import path
from . import views

# from django.conf.urls.static import static
# from django.conf import settings

app_name = 'account'

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    # path('reset-password/<str:key>/', views.reset_password, name='register'),
    # path('reset-password/recovery-email/', views.recovery_email, name='register'),
    # path('change-password/', views.change_password, name='register'),
    path('register/success/', views.register_success, name='register_success'),
    path('unverified/', views.unverified_user, name='unverified_user'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
