from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordChangeView,
    PasswordResetConfirmView
)
from home.forms import (
    RegistrationForm,
    LoginForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
    UserPasswordChangeForm
)


# <editor-fold desc="Authentication -> Register">
def basic_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login/basic-login/')
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/signup/basic.html', context)


def cover_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login/cover-login/')
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/signup/cover.html', context)


def illustration_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login/illustration-login/')
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/signup/illustration.html', context)
#</editor-fold>

# <editor-fold desc="Authentication -> Login">
class BasicLoginView(LoginView):
  template_name = 'accounts/signin/basic.html'
  form_class = LoginForm

class CoverLoginView(LoginView):
  template_name = 'accounts/signin/cover.html'
  form_class = LoginForm

class IllustrationLoginView(LoginView):
  template_name = 'accounts/signin/illustration.html'
  form_class = LoginForm
#</editor-fold>

# <editor-fold desc="Authentication -> Reset">
class BasicResetView(PasswordResetView):
  template_name = 'accounts/reset/basic.html'
  form_class = UserPasswordResetForm

class CoverResetView(PasswordResetView):
  template_name = 'accounts/reset/cover.html'
  form_class = UserPasswordResetForm

class IllustrationResetView(PasswordResetView):
  template_name = 'accounts/reset/illustration.html'
  form_class = UserPasswordResetForm

class UserPasswordResetConfirmView(PasswordResetConfirmView):
  template_name = 'accounts/reset-confirm/basic.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'accounts/change/basic.html'
  form_class = UserPasswordChangeForm
#</editor-fold>

# <editor-fold desc="Authentication -> Lock">
def basic_lock(request):
  return render(request, 'accounts/lock/basic.html')

def cover_lock(request):
  return render(request, 'accounts/lock/cover.html')

def illustration_lock(request):
  return render(request, 'accounts/lock/illustration.html')
#</editor-fold>

# <editor-fold desc="Authentication -> Verification">
def basic_verification(request):
  return render(request, 'accounts/verification/basic.html')

def cover_verification(request):
  return render(request, 'accounts/verification/cover.html')

def illustration_verification(request):
  return render(request, 'accounts/verification/illustration.html')
#</editor-fold>

# <editor-fold desc="Error">
def error_404(request,exception=None ):
  return render(request, 'accounts/error/404.html')

def error_500(request, exception=None):
  return render(request, 'accounts/error/500.html')
#</editor-fold>

# logout
def logout_view(request):
    logout(request)
    return redirect('/accounts/login/basic-login/')
