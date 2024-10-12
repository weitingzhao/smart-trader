from django import forms
from apps.common.models import *

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name']

class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['symbol', 'quantity', 'average_price']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'quantity', 'price', 'date']

class PositionSizingForm(forms.ModelForm):
    class Meta:
        model = UserStaticSetting
        fields = ['capital', 'risk', 'rounding', 'commission', 'tax']
