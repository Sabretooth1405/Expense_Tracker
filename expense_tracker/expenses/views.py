from django.shortcuts import render, redirect
from .models import Expense
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DateRangeForm
@login_required(login_url='/login/')
def expense_list(req, **kwargs):
    if req.method=="POST":
        form=DateRangeForm(req.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            category=form.cleaned_data['category']
            expenses = Expense.objects.filter(user__username=req.user,date__range=[str(start_date),str(end_date)],category__in=category)
            form2=DateRangeForm(data={"start_date":start_date,"end_date":end_date,"category":category})
            return render(req, 'expenses/expenses.html', {"form": form2, "expenses": expenses,"username":req.user})
        else:
            print(form.errors)
            return redirect('about')

    else:
        form=DateRangeForm()
        if kwargs.get('username') == str(req.user):
            expenses = Expense.objects.filter(user__username=req.user)
            
            return render(req, 'expenses/expenses.html', {"form":form,"expenses": expenses,"username":req.user})
        else:
            print(type(kwargs.get('username')))
            print(type(req.user))
            messages.error(
                req, f"You are trying to access from an unauthorised account.Pls login with authorisation")
            return redirect('about')
