from django.shortcuts import render, redirect,HttpResponse
from .models import Expense
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DateRangeForm, ConversionForm
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
import requests
import csv

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


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['amount', 'date',
              'description', 'category', 'created_at']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    success_url = '/'


class ExpenseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Expense
    fields = ['amount', 'date',
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


class ExpenseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
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
        if kwargs.get('username') == str(req.user) and 'report-btn' in req.POST:
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
                return render(req, 'expenses/expense_report.html', {"form": form2, "start_date": start_date, "end_date": end_date,
                                                                    "amount": sum, "categories": cats, "username": req.user, "graph": graph})

            else:
                print(form.errors)
        
                return redirect('about')
        elif kwargs.get('username') == str(req.user) and 'csv-btn' in req.POST:
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
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="Report-from-{start_date}-to-{end_date}-for-{cats}.csv"'
                field_names = [f.name for f in Expense._meta.get_fields()]

                # the csv writer
                writer = csv.writer(response, delimiter=";")
                writer.writerow(field_names)
                expenses = Expense.objects.filter(user__username=req.user, date__range=[
                    str(start_date), str(end_date)], category__in=category)

                if expenses.exists():
                    for expense in expenses:
                        values = []
                        for field in field_names:
                            value = getattr(expense, field)
                            if callable(value):
                                try:
                                    value = value() or ''
                                except:
                                    value = 'Error retrieving value'
                            if value is None:
                                value = ''
                            values.append(value)

                        writer.writerow(values)
                return response
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


@login_required(login_url='/login/')
def convert(req, **kwargs):
    if req.method == "POST":
        if kwargs.get('username') == str(req.user):
            form = ConversionForm(req.POST)

            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                category = form.cleaned_data['category']
                expenses = Expense.objects.filter(user__username=req.user, date__range=[
                    str(start_date), str(end_date)], category__in=category)
                base = form.cleaned_data['initial_currency_code']
                final = form.cleaned_data['final_currency_code']
                form2 = ConversionForm(
                    data={"start_date": start_date, "end_date": end_date, "category": category, 'initial_currency_code': base, 
                    'final_currency_code': final})
                sum = expenses.aggregate(Sum('amount'))
                url = f'https://v6.exchangerate-api.com/v6/bf9ff5018a1041336fbbebed/pair/{base}/{final}/{sum["amount__sum"]}'
                res=requests.get(url)
                data=res.json()
                con_rate = 1/data['conversion_rate']
                con = str(round(con_rate, 2))
                return render(req, 'expenses/convert.html', {"form": form2, "data": data, "username": req.user,"con":con})
            else:
                print(form.errors)
                return redirect('about')
        else:
            return redirect('login')

    else:
        form = ConversionForm()
        if kwargs.get('username') == str(req.user):
            expenses = Expense.objects.filter(user__username=req.user)
            sum = expenses.aggregate(Sum('amount'))
            url = f'https://v6.exchangerate-api.com/v6/bf9ff5018a1041336fbbebed/pair/INR/USD/{sum["amount__sum"]}'
            
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()
            con_rate=1/data['conversion_rate']
            con = str(round(con_rate, 2))
            return render(req, 'expenses/convert.html', {"form": form, "data": data, "username": req.user,"con":con})
            
            
        else:
            print(type(kwargs.get('username')))
            print(type(req.user))
            messages.error(
                req, f"You are trying to access from an unauthorised account.Pls login with authorisation")
            return redirect('about')


