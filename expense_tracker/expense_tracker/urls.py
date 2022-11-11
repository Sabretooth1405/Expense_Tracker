"""expense_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from users import views as users_views
from django.conf import settings
from django.conf.urls.static import static
from expenses import views as exp_views
urlpatterns = [
    path('',users_views.about,name="about"),
    path('admin/', admin.site.urls),
    path("register/", users_views.register, name="register"),
    path("login/", users_views.login, name="login"),
    path("logout/", users_views.logout, name="logout"),
    path("profile/", users_views.profile, name="profile"),
    path("user/update/<int:pk>",
         users_views.UpdateUserProfile.as_view(), name="update-user"),
    path("user/update-image/<int:pk>",
         users_views.UpdateProfileImg.as_view(), name="update-user-image"),
    path('users/delete/<int:pk>',
         users_views.UserDeleteView.as_view(), name='user-delete'),
    path('expenses/create/', exp_views.ExpenseCreateView.as_view(),
         name='expense-create'),
    path('expenses/update/<int:pk>', exp_views.ExpenseUpdateView.as_view(),
         name='expense-update'),
    path('expenses/delete/<int:pk>', exp_views.ExpenseDeleteView.as_view(),
         name='expense-delete'),
    path('<str:username>/expenses/',exp_views.expense_list,name='expenses'),
    
    path('<str:username>/expenses_report/', exp_views.expense_report, name='expense-report'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
