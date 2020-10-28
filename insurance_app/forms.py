from django import forms

from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.forms import *
from .custom_validators import custom_password_validators_help_text_html

# from django_webix.forms import WebixModelForm

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['user','mobile_phone','work_phone','email2']
        labels = {
            'user': '',
            'mobile_phone':'Мобільний телефон',
            'work_phone':'Робочий телефон',
            'email2':'Додаткова електронна пошта'
        }
        widgets = {
            'user': forms.TextInput(attrs={'hidden':'true'}),
            'mobile_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'work_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email2': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']
        labels = {
            'email': 'Електронна пошта'
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    new_password1 = forms.CharField(
        label=("Новий пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class':'form-control'}),
        help_text=custom_password_validators_help_text_html()
    )


class SignupForm(UserCreationForm):

    password1 = forms.CharField(
        label = "Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=custom_password_validators_help_text_html(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name','password1', 'password2')

        labels = {
            'email':"Електронна пошта"
        }

class MyAuthenticationForm(AuthenticationForm):

    def __init__(self, request = None, *args, **kwargs):
        super().__init__(request = None, *args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        try:
            return obj.company_info.IAN_FULL_NAME
        except:
            return obj.IAN_FULL_NAME


class AddOrDeleteCompanyForm(forms.ModelForm):

    company = MyModelChoiceField(label='Компанії', empty_label="Оберіть компанію...",
                                 queryset=Company.objects.filter(update_date = Company.objects.last().update_date),
                                 widget=forms.Select(attrs={'class':'form-control selectpicker','data-live-search':'true'}))
    class Meta:
        model = CompanyUser
        fields = ['company']

class AddInfoToCompany(forms.ModelForm):

    class Meta:
        model = CompanyInfo
        fields = ['info_address','bank_props','position','pib','action_base']

        labels = {
            'info_address': 'Адреса',
            'bank_props': 'Банківські реквізити',
            'position': 'Посада',
            'pib': 'ПІБ',
            'action_base': 'На якій основі дієте'
        }

        widgets = {
            'info_address': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_props': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'pib': forms.TextInput(attrs={'class': 'form-control'}),
            'action_base': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MyPasswordResetForm(PasswordResetForm):

    email = forms.EmailField(
        label=("Електронна пошта"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )



class MySetPasswordForm(SetPasswordForm):

    new_password1 = forms.CharField(
        label=("Новий пароль"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
        help_text=custom_password_validators_help_text_html(),
    )

class AutoInsurance(forms.Form):
    name = forms.CharField(label="Ім'я",widget=forms.TextInput(attrs={'class': 'form-control'}))
    surname = forms.CharField(label='Прізвище',widget=forms.TextInput(attrs={'class': 'form-control'}))
    transport_type = forms.ChoiceField(choices=(("1", "Авто"),
                                                ("2", "Мотоцикл"),
                                                ("3", "Вантажівка"),
                                                ("4", "Автобус"),
                                                ("5", "Причіп"),),
                                       label='Вид транспорту',widget=forms.Select(attrs={'class': 'form-control'}))
    number = forms.CharField(label='Номерний знак',widget=forms.TextInput(attrs={'class': 'form-control'}))
    engine_capacity = forms.CharField(label="Об'єм двигуна",widget=forms.TextInput(attrs={'class': 'form-control'}))
    model_year = forms.CharField(label="Рік випуску авто",widget=forms.TextInput(attrs={'class': 'form-control'}))
    brand = forms.CharField(label="Марка автомобіля",widget=forms.TextInput(attrs={'class': 'form-control'}))
    model = forms.CharField(label="Модель автомобіля",widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label="Адреса",widget=forms.TextInput(attrs={'class': 'form-control'}))
