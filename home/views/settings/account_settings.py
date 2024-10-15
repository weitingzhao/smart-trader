from django.shortcuts import render,redirect
from django.contrib import messages
from apps.common.models import *
from home.forms.portfolio import UserStaticSettingForm


def default(request):
    return render(
        request=request,
        template_name='pages/settings/account_settings.html',
        context= {
            'parent': 'settings',
            'segment': 'account_settings',
        })
