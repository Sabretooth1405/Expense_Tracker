from django.shortcuts import render, redirect
from .models import Expense
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DateRangeForm,MailForm
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count, Q
from .models import ExpenseCategory
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


@login_required(login_url='/login/')
def expense_list(req, **kwargs):
    if req.method == "POST":
        if kwargs.get('username') == str(req.user):
            form = DateRangeForm(req.POST)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                category = form.cleaned_data['category']
                expenses = Expense.objects.filter(user__username=req.user, date__range=[
                                                str(start_date), str(end_date)], category__in=category)
                form2 = DateRangeForm(
                    data={"start_date": start_date, "end_date": end_date, "category": category})

                return render(req, 'expenses/expenses.html', {"form": form2, "expenses": expenses, "username": req.user})
            else:
                print(form.errors)
                return redirect('about')
        else:
            return redirect('login')

    else:
        form = DateRangeForm()
        if kwargs.get('username') == str(req.user):
            expenses = Expense.objects.filter(user__username=req.user)

            return render(req, 'expenses/expenses.html', {"form": form, "expenses": expenses, "username": req.user})
        else:
            print(type(kwargs.get('username')))
            print(type(req.user))
            messages.error(
                req, f"You are trying to access from an unauthorised account.Pls login with authorisation")
            return redirect('about')


class ExpenseCreateView(LoginRequiredMixin, UserPassesTestMixin,CreateView):
    model = Expense
    fields = [ 'amount', 'date',
              'description', 'category', 'created_at']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        expense = self.get_object()
        if self.request.user == expense.user:
            return True
        return False
    success_url = '/'


class ExpenseUpdateView(LoginRequiredMixin, UserPassesTestMixin,UpdateView):
    model = Expense
    fields = [ 'amount', 'date',
              'description', 'category', 'created_at']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        expense = self.get_object()
        if self.request.user == expense.user:
            return True
        return False

    success_url = '/'


class ExpenseDeleteView(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    model = Expense
    fields = ['user', 'amount', 'date',
              'description', 'category', 'created_at']

    def test_func(self):
        expense = self.get_object()
        if self.request.user == expense.user:
            return True
        return False

    success_url = '/'


@login_required(login_url='/login/')
def expense_report(req, **kwargs):
    if req.method == "POST":
        if kwargs.get('username') == str(req.user):
            form = DateRangeForm(req.POST)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                category = form.cleaned_data['category']
                categories = list(category)
                categories2 = [str(ct) for ct in categories]
                cats = ""
                for i, ct in enumerate(categories2):
                    cats += ct
                    if i < len(categories2)-2:
                        cats += ","
                    elif i == len(categories2)-2:
                        cats += " and "

                expenses = Expense.objects.filter(user__username=req.user, date__range=[
                                                str(start_date), str(end_date)], category__in=category)

                form2 = DateRangeForm(
                    data={"start_date": start_date, "end_date": end_date, "category": category})
                sum = expenses.aggregate(Sum('amount'))
                result = expenses.values('category').order_by(
                    'category').annotate(cat_total=Sum('amount'))
                # [{'category': 1, 'cat_total': 60.0}, {
                #     'category': 2, 'cat_total': 15.0}]
                amt_category = [r['cat_total'] for r in result]
                
                category3=[]
                for obj in list(result):
                    category3.append(str(ExpenseCategory.objects.filter(pk=obj['category']).first()))
                
                print(category3)
                fig = go.Figure(
                    data=[
                        go.Bar(
                            name="Original",
                            x=category3,
                            y=amt_category,
                            offsetgroup=0,
                            text=amt_category
                        ),
                    ],
                    layout=go.Layout(
                        title="Category-wise breakdown",
                        yaxis_title="Amount Spent",
                    )
                )
                graph=fig.to_html()
                return render(req, 'expenses/expense_report.html', {"form": form2, "start_date": start_date, "end_date": end_date,
                                                                    "amount": sum, "categories": cats, "username": req.user, "graph": graph})
        
            else:
                print(form.errors)
                return redirect('about')
        else:
            return redirect('login')

    else:
        form = DateRangeForm()
        if kwargs.get('username') == str(req.user):
            expenses = Expense.objects.filter(user__username=req.user)
            sum = expenses.aggregate(Sum('amount'))
            start_date = expenses.last().date
            end_date = expenses.first().date
            categories = "all items"
            result = expenses.values('category').order_by(
                'category').annotate(cat_total=Sum('amount'))
            # [{'category': 1, 'cat_total': 60.0}, {
            #     'category': 2, 'cat_total': 15.0}]
            amt_category = [r['cat_total'] for r in result]

            category3 = []
            for obj in list(result):
                category3.append(
                    str(ExpenseCategory.objects.filter(pk=obj['category']).first()))

            print(category3)
            fig = go.Figure(
                data=[
                    go.Bar(
                        name="Original",
                        x=category3,
                        y=amt_category,
                        offsetgroup=0,
                        text=amt_category
                    ),
                ],
                layout=go.Layout(
                    title="Category-wise breakdown",
                    yaxis_title="Amount Spent",
                )
            )
            graph = fig.to_html()
            
            return render(req, 'expenses/expense_report.html', {"form": form, "start_date": start_date, "end_date": end_date,
                                                                "amount": sum, "categories": categories, "username": req.user, "graph": graph})
            
        else:
            print(type(kwargs.get('username')))
            print(type(req.user))
            messages.error(
                req, f"You are trying to access from an unauthorised account.Pls login with authorisation")
            return redirect('about')
