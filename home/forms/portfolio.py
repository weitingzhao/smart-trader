from django import forms
from apps.common.models import *

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name','cash','money_market','is_default']

class UserStaticSettingForm(forms.ModelForm):
    class Meta:
        model = UserStaticSetting
        fields = [
            'capital', 'risk', 'rounding', 'commission', 'tax',
            'expect_gain_risk_ratio', 'position_min', 'position_max','total_risk_cap','net_risk_cap']


class HoldingForm(forms.ModelForm):
    holding_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Holding
        fields = ['symbol','holding_id']


class HoldingOrderForm(forms.ModelForm):

    holding_symbol = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Holding Symbol',
        'id': 'id_holding_symbol'
    }))

    quantity_target = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'min': '0',
        'id': 'id_quantity_target'
    }))
    price_market = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01',
        'id': 'id_buy_price_market'
    }))
    price_stop = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01',
        'id': 'id_price_stop'
    }))
    price_limit = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'step': '0.01',
        'id': 'id_price_limit'
    }))

    order_type = forms.ChoiceField(choices=OrderTypeChoices.choices, widget=forms.Select(attrs={
        'class': 'form-select',
    }), initial=OrderTypeChoices.NONE)

    class Meta:
        abstract = True
        fields = [
            'holding_symbol', 'action', 'timing', 'order_type',
            'quantity_target','price_market','price_stop', 'price_limit',
        ]


class HoldingBuyOrderForm(HoldingOrderForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['id'] = f'id_buy_{field_name}'

    wishlist = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'min': '0',
        'id': 'id_holding_buy_wishlist'
    }))

    class Meta:
        model = HoldingBuyOrder
        fields = [
            'holding_symbol', 'action', 'timing','order_type',
            'quantity_target', 'price_market', 'price_stop', 'price_limit',
            "wishlist"
        ]

class HoldingSellOrderForm(HoldingOrderForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['id'] = f'id_sell_{field_name}'

    is_obsolete = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], widget=forms.Select(attrs={
        'class': 'form-select',
        'id': 'id_holding_sell_is_obsolete'
    }), initial=False)

    class Meta:
        model = HoldingSellOrder
        fields = [
            'holding_symbol', 'action', 'timing', 'order_type',
            'quantity_target','price_market', 'price_stop', 'price_limit',
            'is_obsolete'
        ]








