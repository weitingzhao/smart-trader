from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _  # Django 4.0.0 and more


class RegistrationForm(UserCreationForm):
  password1 = forms.CharField(
      label=_("Password"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
  )
  password2 = forms.CharField(
      label=_("Password Confirmation"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password Confirmation'}),
  )

  class Meta:
    model = User
    fields = ('username', 'email', )

    widgets = {
      'username': forms.TextInput(attrs={
          'class': 'form-control',
          'placeholder': 'Username'
      }),
      'email': forms.EmailInput(attrs={
          'class': 'form-control',
          'placeholder': 'Email'
      })
    }