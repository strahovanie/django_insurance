from .models import *
from django.contrib.auth.forms import *
from .custom_validators import custom_password_validators_help_text_html
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


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

    def save(self, commit=True):
        mail_subject = 'Зміна паролю'
        message = render_to_string('insurance_app/password_change_email.html', {
            'domain': settings.DEFAULT_DOMAIN,
            'user': self.user,
            'admin_email': settings.EMAIL_HOST_USER
        })
        email = EmailMessage(
            mail_subject, message, to=[getattr(self.user, 'email')]
        )
        email.send()
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class SignupForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name','password1', 'password2')


class MyAuthenticationForm(AuthenticationForm):

    def __init__(self, request = None, *args, **kwargs):
        super().__init__(request = None, *args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class AddChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.IAN_FULL_NAME

class DeleteChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
            return obj.company_info.IAN_FULL_NAME


class AddCompanyForm(forms.ModelForm):

    company = AddChoiceField(label='Компанії', empty_label="Оберіть компанію...",
                                 queryset=Company.objects.filter(update_date = Company.objects.last().update_date),
                                 widget=forms.Select(attrs={'class':'form-control js-example-basic-single','id':'select_add'}))
    class Meta:
        model = CompanyUser
        fields = ['company']

class DeleteCompanyForm(forms.ModelForm):

    company = DeleteChoiceField(label='Компанії', empty_label="Оберіть компанію...",
                                 queryset=CompanyUser.objects.filter(user = None),
                                 widget=forms.Select(attrs={'class':'form-control js-example-basic-single','id':'select_delete'}))
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class DateInput(forms.DateInput):
    input_type = 'date'

class OrderForm(forms.ModelForm):

    company = DeleteChoiceField(label='Компанії', empty_label="Оберіть компанію...",
                                 queryset=CompanyUser.objects.filter(user = None),
                                 widget=forms.Select(attrs={'class':'form-control js-example-basic-single','id':'select_delete'}),
                                to_field_name="company_info")
    calc_type = forms.MultipleChoiceField(choices=(("1", "1"),
                                                ("2", "2"),
                                                ("3", "3"),
                                                ("4", "4"),
                                                ("5", "5")), required=True,label="Вид розрахунку",
                                          widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Order
        fields = ['company','reporting_date','calc_type']

        labels = {
            'reporting_date': 'Звітня дата',
        }

        widgets = {
            'reporting_date': DateInput(attrs={'class':'form-control'}),
        }


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
