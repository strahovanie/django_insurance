from django import forms

from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.forms import *

# from django_webix.forms import WebixModelForm

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = '__all__'
        labels = {
            "user": "Пользователь",
            "mobile_phone": "Мобильный телефон",
            "work_phone": "Рабочий телефон",
            "email2": "Дополнительная электронная почта"
        }
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control','disabled':True,}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'work_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email2': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']
        labels = {
            "username": "Имя пользователя",
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Электронная почта"
        }
        help_texts = {
            'username': None,
        }
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.TextInput(attrs={'class':'form-control'}),
        }

class MyPasswordChangeForm(PasswordChangeForm):

    old_password = forms.CharField(
        label=("Старый пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class':'form-control'}),
    )

    new_password1 = forms.CharField(
        label=("Новый пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class':'form-control'}),
    )
    new_password2 = forms.CharField(
        label=("Повторите новый пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class':'form-control'}),
    )


class SignupForm(UserCreationForm):
    password1 = forms.CharField(
        label = "Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label = "Повторите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control input-normal',}),
    )
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name','password1', 'password2')

        labels = {
            "username": "Имя пользователя",
            "email": "Электронная почта",
            "first_name": "Имя",
            "last_name": "Фамилия",
        }

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LoginForm(AuthenticationForm):
    username = UsernameField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(
        label=("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
    )
