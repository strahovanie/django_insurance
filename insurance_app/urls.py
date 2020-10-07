from django.urls import path

from . import views

app_name='insurance_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin_page', views.admin_page, name='admin_page'),
    path('login_user', views.login_user, name='login_user'),
    path('add_userprofile',views.add_userprofile,name='add_userprofile'),
    path('logout', views.logout, name='logout'),
    path('register',views.register,name='register'),
    path('add_company', views.add_company, name='add_company'),
    path('update_company', views.update_company, name='update_company'),
    path('add_chosen_company/',views.add_chosen_company,name='add_chosen_company'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
]
