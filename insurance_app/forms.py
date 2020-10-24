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
            "user": '',
            "mobile_phone": "Мобільний телефон",
            "work_phone": "Робочий телефон",
            "email2": "Додаткова електронна пошта"
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
            "username": "Ім'я користувача",
            "first_name": "Ім'я",
            "last_name": "Прізвище",
            "email": "Електронна пошта"
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

    error_messages = {
        'password_mismatch': ('Паролі не співпадають'),
    }
    old_password = forms.CharField(
        label=("Старий пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class':'form-control'}),
    )

    new_password1 = forms.CharField(
        label=("Новий пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class':'form-control'}),
        help_text=custom_password_validators_help_text_html()
    )
    new_password2 = forms.CharField(
        label=("Повторіть новий пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class':'form-control'}),
    )


class SignupForm(UserCreationForm):

    error_messages = {
        'password_mismatch': ('Паролі не співпадають'),

    }

    password1 = forms.CharField(
        label = "Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=custom_password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label = "Повторіть пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control input-normal',}),
    )
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name','password1', 'password2')

        labels = {
            "email": "Електронна пошта",
            "first_name": "Ім'я",
            "last_name": "Прізвище",
        }
        help_texts = {
            'username': "Обов'язкове поле. До 150 символів. Може містити букви, цифри та знаки @/./+/-/_",
            'email': "Обов'язкове поле",
        }
        error_messages = {
            'username': {
                'unique': "Користувач з таким ім'ям вже існує",
            },
            'email': {
                'invalid': "Введіть коректну електронну пошту"
            }
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MyAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': (
            "Користувача з таким ім'ям та паролем не знайдено. Зверніть увагу: можливо "
            "у вас включений Caps Lock"
        ),
        'inactive': ("Цей акаунт неактивний"),
    }
    username = UsernameField(
        label="Ім'я користувача",
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(
        label=("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
    )


class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.IAN_FULL_NAME

class DeleteChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.company.IAN_FULL_NAME


class AddCompanyForm(forms.ModelForm):

    company = MyModelChoiceField(label='Компанії', empty_label="Оберіть компанію...",
                                 queryset=Company.objects.filter(update_date = Company.objects.last().update_date),
                                 widget=forms.Select(attrs={'class':'form-control selectpicker','data-live-search':'true'}))
    class Meta:
        model = CompanyUser
        fields = ['company','address','bank_props','position','pib','action_base']
        labels = {
            'address' : 'Адреса',
            'bank_props' : 'Банківські реквізити',
            'position' : 'Посада',
            'pib' : 'ПІБ',
            'action_base': 'На якій основі дієте',
        }
        help_text = {'action_base':'sfdde'}
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_props': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'pib': forms.TextInput(attrs={'class': 'form-control'}),
            'action_base': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DeleteCompanyForm(forms.ModelForm):

    company = DeleteChoiceField(label='Компанії',empty_label="Оберіть компанію...",
                                 queryset=Company.objects.filter(update_date = Company.objects.last().update_date),
                                 widget=forms.Select(
                                     attrs={'class': 'form-control selectpicker', 'data-live-search': 'true'}))
    class Meta:
        model = CompanyUser
        fields = ['company']

class MyPasswordResetForm(PasswordResetForm):

    email = forms.EmailField(
        label=("Електронна пошта"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("Користувач не зареєстрован на цю електронну пошту")

        return email


class MySetPasswordForm(SetPasswordForm):

    error_messages = {
        'password_mismatch': ('Паролі не співпадають'),
    }
    new_password1 = forms.CharField(
        label=("Новий пароль"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
        help_text=custom_password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=("Повторіть пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
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
