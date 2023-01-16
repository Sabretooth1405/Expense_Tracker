from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns=[
    path('auth/',obtain_auth_token),
    path("",views.apiWelcome,name="api-welcome"),
    path('login-test/',views.apiLoginTest,name="login-test"),
    path('list/',views.expenseList,name='api-expense-list'),
    path('detail/<int:pk>',views.expenseDetail,name="api-expense-detail"),
    path('create/',views.ExpenseCreateView.as_view(),name='api-expense-create'),
    path('update/<int:pk>', views.ExpenseUpdateView.as_view(), name='api-expense-update'),
]