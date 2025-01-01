from django import forms
from djangoeditorwidgets.widgets import MonacoEditorWidget
from apps.common.models import *


class StrategyAlgoScriptModelForm(forms.ModelForm):
    class Meta:
        model = StrategyAlgoScript
        fields = "__all__"
        widgets = {
            "text": MonacoEditorWidget(name="default", language="html", wordwrap=True)
        }