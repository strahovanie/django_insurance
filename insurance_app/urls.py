from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
app_name='insurance_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin_page', views.admin_page, name='admin_page'),
    path('change_account_password', views.change_account_password, name='change_account_password'),
    path('login_user', views.login_user, name='login_user'),
    path('password/reset/', auth_views.PasswordResetView.as_view(template_name ='insurance_app/password_reset_form.html',
  email_template_name = 'insurance_app/password_reset_email.html', success_url = reverse_lazy('insurance_app:password_reset_done')), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(template_name ='insurance_app/password_reset_done.html'), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(success_url = reverse_lazy('insurance_app:password_reset_complete'),template_name ='insurance_app/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('password/reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name ='insurance_app/password_reset_complete.html'),
        name='password_reset_complete'),
    path('add_userprofile',views.add_userprofile,name='add_userprofile'),
    path('logout', views.logout, name='logout'),
    path('register',views.register,name='register'),
    path('add_company', views.add_company, name='add_company'),
    path('accept_chosen_request/',views.accept_chosen_request, name='accept_chosen_request'),
    path('accept_all_request/',views.accept_all_request, name='accept_all_request'),
    path('load_to_database/',views.load_to_database, name='load_to_database'),
    path('add_chosen_company/',views.add_chosen_company,name='add_chosen_company'),
    path('delete_chosen_company/',views.delete_chosen_company,name='delete_chosen_company'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('update_database/',views.update_database, name='update_database'),
]
