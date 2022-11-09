from django import forms
from .models import ExpenseCategory
class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    category=forms.ModelMultipleChoiceField(queryset=ExpenseCategory.objects.all())