from django import forms
from .models import ExpenseCategory,Expense
from django.db.models import Q
class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    category=forms.ModelMultipleChoiceField(queryset=ExpenseCategory.objects.all())

    def __init__(self, uid, *args, **kwargs):
        super(DateRangeForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = ExpenseCategory.objects.filter(
            Q(user_id=uid)|Q(user_id=2)).distinct()

class ConversionForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    category = forms.ModelMultipleChoiceField(
        queryset=ExpenseCategory.objects.all())
    initial_currency_code=forms.CharField(max_length=3)
    final_currency_code = forms.CharField(max_length=3)

    def __init__(self,uid,*args, **kwargs):
        super(ConversionForm, self).__init__(*args, **kwargs)
        
        self.fields['category'].queryset = ExpenseCategory.objects.filter(
            Q(user_id=uid)|Q(user_id=2)).distinct()


class ExpCreateForm(forms.ModelForm):
    class Meta:
       model = Expense
       fields = ['amount','date','description','category','created_at']

    def __init__(self, *args, **kwargs):
        uid = kwargs.pop('uid', None)
        super(ExpCreateForm, self).__init__(*args, **kwargs)

        if uid is not None:
            self.fields['category'].queryset = ExpenseCategory.objects.filter(
                Q(user_id=uid) | Q(user_id=2)).distinct()