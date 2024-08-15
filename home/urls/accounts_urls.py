from home import views
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [

    # Authentication -> Register
    path('register/basic-register/',
         views.account.basic_register,
         name="basic_register"),
    path('register/cover-register/',
         views.account.cover_register,
         name="cover_register"),
    path('register/illustration-register/',
         views.account.illustration_register,
         name="illustration_register"),

    # Authentication -> Login
    path('login/basic-login/',
         views.account.BasicLoginView.as_view(),
         name="basic_login"),
    path('login/cover-login/',
         views.account.CoverLoginView.as_view(),
         name="cover_login"),
    path('login/illustration-login/',
         views.account.IllustrationLoginView.as_view(),
         name="illustration_login"),

    # Authentication -> Reset
    path('reset/basic-reset/',
         views.account.BasicResetView.as_view(),
         name="basic_reset"),
    path('reset/cover-reset/',
         views.account.CoverResetView.as_view(),
         name="cover_reset"),
    path('reset/illustration-reset/',
         views.account.IllustrationResetView.as_view(),
         name="illustration_reset"),
    path('password-change/',
         views.account.UserPasswordChangeView.as_view(),
         name='password_change'),
    path('password-reset-confirm/<uidb64>/<token>/',
         views.account.UserPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-change-done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/done/change-done.html'
         ), name="password_change_done"),
    path('password-reset-done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/done/basic.html'
         ), name='password_reset_done'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/complete/basic.html'
         ), name='password_reset_complete'),

    # Authentication -> Lock
    path('lock/basic-lock/',
         views.account.basic_lock,
         name="basic_lock"),
    path('lock/cover-lock/',
         views.account.cover_lock,
         name="cover_lock"),
    path('lock/illustration-lock/',
         views.account.illustration_lock,
         name='illustration_lock'),

    # Authentication -> Verification
    path('verification/basic-verification/',
         views.account.basic_verification,
         name="basic_verification"),
    path('verification/cover-verification/',
         views.account.cover_verification,
         name="cover_verification"),
    path('verification/illustration-verification/',
         views.account.illustration_verification,
         name="illustration_verification"),

]
