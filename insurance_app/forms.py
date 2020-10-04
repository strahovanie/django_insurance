from django import forms

from django.contrib.auth.models import User
from .models import UserProfile

# from django_webix.forms import WebixModelForm

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['user','mobile_phone']
        labels = {
            "user": "Пользователь"
        }
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.TextInput(attrs={'class':'form-control'}),
        }