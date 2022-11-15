from django import forms
from .models import ExpenseCategory
class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    category=forms.ModelMultipleChoiceField(queryset=ExpenseCategory.objects.all())

class ConversionForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    category = forms.ModelMultipleChoiceField(
        queryset=ExpenseCategory.objects.all())
    initial_currency_code=forms.CharField(max_length=3)
    final_currency_code = forms.CharField(max_length=3)
    