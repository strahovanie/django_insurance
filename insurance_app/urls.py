from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import MyPasswordResetForm, MyPasswordChangeForm, MyAuthenticationForm
app_name='insurance_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin_page', views.admin_page, name='admin_page'),
    path('login_user', auth_views.LoginView.as_view(template_name ='insurance_app/login_user.html', form_class = MyAuthenticationForm, redirect_field_name = 'index'), name='login_user'),
    path('password/reset/', auth_views.PasswordResetView.as_view(template_name ='insurance_app/password_reset_form.html', form_class = MyPasswordResetForm,
    email_template_name = 'insurance_app/password_reset_email.html', success_url = reverse_lazy('insurance_app:password_reset_done')), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(template_name ='insurance_app/password_reset_done.html'), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(form_class = MyPasswordChangeForm, success_url = reverse_lazy('insurance_app:password_reset_complete'),template_name ='insurance_app/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('password/reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name ='insurance_app/password_reset_complete.html'),
        name='password_reset_complete'),
    path('password/change/', auth_views.PasswordChangeView.as_view(template_name ='insurance_app/password_change_form.html',
                                                                   form_class = MyPasswordChangeForm,success_url = reverse_lazy('insurance_app:password_change_done') ), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name ='insurance_app/password_change_done.html'), name='password_change_done'),
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
    path('auto_insurance', views.auto_insurance, name='auto_insurance'),
    path('auto_fill/',views.auto_fill, name='auto_fill'),
    path('company_list',views.company_list, name='company_list'),
    path('company_detail/<int:company_IM_NUMIDENT>',views.company_detail, name='company_detail'),
    path('add_info_to_company/<int:company_IM_NUMIDENT>',views.add_info_to_company, name='add_info_to_company'),
    path('order/<int:order_id>',views.order, name='order'),
    path('order_history',views.order_history, name='order_history'),
    path('reject_order/<int:order_id>',views.reject_order, name='reject_order'),
    path('order_offered',views.order_offered, name='order_offered'),
]
