from django.shortcuts import render,redirect
from django.contrib import messages
from apps.common.models import *
from home.forms.portfolio import UserStaticSettingForm


def default(request):
    try:
        user_static_setting = UserStaticSetting.objects.get(user=request.user)
        form_static_risk = UserStaticSettingForm(instance=user_static_setting)
    except UserStaticSetting.DoesNotExist:
        form_static_risk = UserStaticSettingForm()


    return render(
        request=request,
        template_name='pages/settings/risk_preferences.html',
        context= {
            'parent': 'settings',
            'segment': 'risk_preferences',
            'static_risk_form': form_static_risk,
            'messages': messages.get_messages(request),
        })


def settings_risk_static_risk(request):
    if request.method == 'POST':
        form = UserStaticSettingForm(request.POST)
        if form.is_valid():
            position_sizing, created = UserStaticSetting.objects.update_or_create(
                user=request.user,
                defaults=form.cleaned_data
            )
            if created:
                messages.success(request, 'static risk model created successfully.', extra_tags='static risk model')
            else:
                messages.success(request, 'static risk model updated successfully.', extra_tags='static risk model')
        else:
            messages.error(request, f'static risk model form is invalid.', extra_tags='static risk model')
            return render(
                request,
                template_name='pages/settings/risk_preferences.html',
                context={
                    'parent': 'account',
                    'segment': 'customize',
                    'position_sizing_form': form,
                })
    else:
        messages.error(request, "method not supported", extra_tags='position sizing')

    return redirect('risk_preferences')





























