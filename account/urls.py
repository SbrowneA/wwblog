from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# from django.conf.urls.static import static
# from django.conf import settings

app_name = 'account'

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('register/success/', views.register_success, name='register_success'),
    path('unverified/', views.unverified_user, name='unverified_user'),

    path('change-password/', views.change_password, name='change_password'),

    path('password_reset/',
         auth_views.PasswordResetView.as_view(email_template_name="account/email_templates/password_reset_email.html",
                                              subject_template_name="account/email_templates/password_reset_subject.txt",
                                              template_name="account/reset_send_email.html", success_url="sent/"),
         name='password_reset'),

    path('password_reset/sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="account/reset_email_sent.html"),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(success_url="/reset-password/success",
                                                     template_name="account/reset_password.html"),
         name='password_reset_confirm'),

    path('reset-password/success',
         auth_views.PasswordResetCompleteView.as_view(template_name="account/reset_password_success.html"),
         name='password_reset_complete'),
]

# reset password urls are linked statically in templates (can't be referenced dynamically)

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
