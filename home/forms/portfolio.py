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
        'placeholder': 'Holding Symbol',
        'id': 'id_buy_holding_symbol'
    }))

    order_place_date =  forms.DateTimeField(widget=forms.DateTimeInput(attrs={
        'type': 'date',
        'class': 'form-control',
        'id': 'id_buy_order_place_date'
    }))
    quantity_target = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'min': '0',
        'id': 'id_buy_quantity_target'
    }))
    price_market = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01',
        'id': 'id_buy_price_market'
    }))
    price_stop = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01',
        'id': 'id_buy_price_stop'
    }))
    price_limit = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01',
        'id': 'id_buy_price_limit'
    }))
    is_initial = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], widget=forms.Select(attrs={
        'class': 'form-select',
        'id': 'id_buy_is_initial'
    }), initial=False)
    is_additional = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], widget=forms.Select(attrs={
        'class': 'form-select',
        'id': 'id_buy_is_additional'
    }), initial=False)

    class Meta:
        model = HoldingBuyOrder
        fields = [
            'holding_symbol',
            'action', 'timing', 'order_place_date',
            'quantity_target',
            'price_market', 'price_stop', 'price_limit',
            'is_initial', 'is_additional'
        ]

class HoldingSellOrderForm(forms.ModelForm):
    holding_symbol = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Holding Symbol',
        'id': 'id_sell_holding_symbol'
    }))

    order_place_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={
        'type': 'date',
        'class': 'form-control',
        'id': 'id_sell_order_place_date'
    }))

    quantity_target = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'min': '0',
        'id': 'id_sell_quantity_target'
    }))

    price_stop = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01',
        'id': 'id_sell_price_stop'
    }))
    price_limit = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01',
        'id': 'id_sell_price_limit'
    }))

    is_initial = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], widget=forms.Select(attrs={
        'class': 'form-select',
        'id': 'id_sell_is_initial'
    }), initial=False)

    good_until = forms.DateTimeField(widget=forms.DateTimeInput(attrs={
        'type': 'date',
        'class': 'form-control',
        'id': 'id_sell_good_until'
    }))

    class Meta:
        model = HoldingSellOrder
        fields = [
            'holding_symbol',
            'action', 'timing', 'order_place_date',
            'quantity_target',
            'price_stop', 'price_limit',
            'is_initial', 'good_until'
        ]


class UserStaticSettingForm(forms.ModelForm):
    class Meta:
        model = UserStaticSetting
        fields = [
            'capital', 'risk', 'rounding', 'commission', 'tax',
            'expect_gain_risk_ratio', 'position_min', 'position_max','total_risk_cap','net_risk_cap']





