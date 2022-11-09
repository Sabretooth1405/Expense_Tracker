from django.shortcuts import render, redirect
from .models import Expense
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DateRangeForm
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User




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


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['user', 'amount','date','description', 'category','created_at']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    success_url='/'

class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    fields = ['user', 'amount','date','description', 'category','created_at']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        expense = self.get_object()
        if self.request.user == expense.user:
            return True
        return False
    
    success_url='/'

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    fields = ['user', 'amount','date','description', 'category','created_at']

    def test_func(self):
        expense = self.get_object()
        if self.request.user == expense.user:
            return True
        return False


    success_url='/'