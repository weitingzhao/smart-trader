from django import forms
from apps.common.models import *

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name','cash','money_market','is_default']

class HoldingForm(forms.ModelForm):
    holding_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Holding
        fields = ['symbol','holding_id']


class HoldingBuyOrderForm(forms.ModelForm):
    holding_symbol = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Holding Symbol'
    }))

    order_place_date =  forms.DateTimeField(widget=forms.DateTimeInput(attrs={
        'type': 'datetime-local',
        'class': 'form-control'
    }))
    quantity_target = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'min': '0'
    }))
    price_market = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01'
    }))
    price_stop = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01'
    }))
    price_limit = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01'
    }))
    is_initial = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], widget=forms.Select(attrs={
        'class': 'form-select'
    }), initial=False)
    is_additional = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], widget=forms.Select(attrs={
        'class': 'form-select'
    }), initial=False)

    class Meta:
        model = HoldingBuyOrder
        fields = [
            'holding_symbol',
            'action', 'timing', 'order_place_date', 'quantity_target',
            'price_market', 'price_stop', 'price_limit',
            'is_initial', 'is_additional'
        ]



class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['symbol', 'quantity', 'average_price']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'quantity', 'price', 'date']

class UserStaticSettingForm(forms.ModelForm):
    class Meta:
        model = UserStaticSetting
        fields = [
            'capital', 'risk', 'rounding', 'commission', 'tax',
            'expect_gain_risk_ratio', 'position_min', 'position_max','total_risk_cap','net_risk_cap']
