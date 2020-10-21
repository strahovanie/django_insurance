from .classes import *
from .models import *
from django.contrib import auth
from .forms import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
import threading
from .processor import Processor


def index(request):
    companies = Company.objects.all()
    template = loader.get_template('insurance_app/index.html')
    context = {
        'companies': companies,
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
def update_database(request):
    if request.is_ajax() and request.method == 'POST':
        alert_data = request.POST["alert_data"]
        if alert_data.strip() == 'None':
            processor = Processor()
            thread = threading.Thread(target=processor.update_company)
            thread.start()
            return JsonResponse({'context': 'База даних компаній буде оновлена'})
        elif int(alert_data) > 7:
            processor = Processor()
            thread = threading.Thread(target=processor.load_company)
            thread.start()
            return JsonResponse({'context': 'База даних компаній буде завантажена'})
        else:
            return JsonResponse({'context': 'База даних компаній НЕ буде оновлена'})

@csrf_exempt
def accept_chosen_request(request):
    request_id = request.POST.get('request_id')
    confirm_request = Request.objects.get(id = request_id)
    confirm_request.confirm=True
    confirm_request.save()
    return JsonResponse({})

@csrf_exempt
def accept_all_request(request):
    requests = Request.objects.all()
    for request in requests:
        if request.confirm == False:
            request.confirm=True
            request.save()
    return JsonResponse({})

@csrf_exempt
def load_to_database(request):
    db_obj = DatabaseAccess()
    db_obj.update_company_user()
    return JsonResponse({})

def check_requests():
    flag=True
    rows = Request.objects.all()
    for row in rows:
        if row.confirm==False:
            flag=False
            break
    return flag

def admin_page(request):
    user = request.user
    admin = user.is_superuser
    db_obj = DatabaseAccess()
    try:
        data = db_obj.get_update_data()
        now = timezone.now()
        alert_data = (now - data).days
    except:
        alert_data = None
    requests = Request.objects.all()
    template = loader.get_template('insurance_app/admin_page.html')
    check_requests_flag = check_requests()
    print(dir(requests))
    context = {
        'admin': admin,
        'requests': requests,
        'check_requests_flag' : check_requests_flag,
        'alert_data': alert_data,
    }
    return HttpResponse(template.render(context, request))

def change_account_password(request):
    user = request.user
    template = loader.get_template('insurance_app/change_account_password.html')
    if request.method == "POST":
        form = MyPasswordChangeForm(data=request.POST, user=user)
        if form.is_valid():
            post3 = form.save(commit=False)
            post3.save()
            auth.login(request, user)
            return redirect('insurance_app:index')
    else:
        form = MyPasswordChangeForm(user=user)
    context = {
        'user' : user,
        'form': form,
    }
    return HttpResponse(template.render(context, request))

def add_company(request):
    user = request.user
    last_company = Company.objects.last()
    last_date = last_company.update_date
    companies = Company.objects.filter(update_date = last_date)
    template = loader.get_template('insurance_app/add_company.html')
    user_companies = CompanyUser.objects.filter(user=user)
    if request.method == "POST":
        form1 = UserUpdateForm(request.POST,instance=user)
        form2 = UserProfileForm(request.POST,instance=user.userprofile)
        if form1.is_valid() and form2.is_valid():
            post1 = form1.save(commit=False)
            post2 = form2.save(commit=False)
            post1.save()
            post2.save()
            return redirect('insurance_app:add_company')
    else:
        form1 = UserUpdateForm(instance=user)
        form2 = UserProfileForm(instance=user.userprofile)
        form3 = AddCompanyForm()
        form4 = DeleteCompanyForm()
        form4.fields['company']._set_queryset(CompanyUser.objects.filter(user = user))
    context = {
        'user' : user,
        'companies': companies,
        'form1': form1,
        'form2': form2,
        'form3': form3,
        'form4': form4,
        'user_companies': user_companies
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
def add_chosen_company(request):
    db_obj = DatabaseAccess()
    choice_id = request.POST['company']
    address = request.POST['address']
    bank_props = request.POST['bank_props']
    position = request.POST['position']
    pib = request.POST['pib']
    action_base = request.POST['action_base']
    current_company = Company.objects.get(id=choice_id)
    user = request.user
    db_obj.insert_add_request(user, current_company, address, bank_props, position, pib, action_base, 'add')
    print('Action "add" is added to requests table')
    return redirect('insurance_app:add_company')

@csrf_exempt
def delete_chosen_company(request):
    db_obj = DatabaseAccess()
    choice_id = request.POST['company']
    current_company = CompanyUser.objects.get(id=choice_id).company
    print(current_company)
    user = request.user
    # fromaddr = 'strahovka.work2020@gmail.com'
    # toaddr = auth_user.email
    # toaddr = current_company.email

    # username = 'strahovka.work2020@gmail.com'
    # password = 'cdnblpUYBvdlH8'
    # server = smtplib.SMTP('smtp.gmail.com:587')
    db_obj.insert_delete_request(user, current_company, 'delete')
    print('Action "delete" is added to requests table')
        # server.starttls()
        # server.login(username, password)
        # msg1 = 'Потвердите что вашу компанию обслуживает ' + str(site_user.first_name)
        # msg2 = 'Confirm that you want to add this company' + str(current_company.IAN_FULL_NAME) + str(
        #     current_company.IM_NUMIDENT)
        # server.sendmail(fromaddr, toaddr, msg2.encode("utf8"))
        # server.quit()
    return redirect('insurance_app:add_company')

def update_company(request):
    db_obj = DatabaseAccess()
    obj = Updates()
    modify_obj = DataModify()
    try:
        data = db_obj.get_update_data()
        now = timezone.now()
        print((now - data).days)
        if (now - data).days < 7:
            print(1)
            tuple_obj = obj.parser()
            rows = Company.objects.filter(update_date = data)
            modify_obj.modify_company(tuple_obj[0])
            obj.compare(rows, tuple_obj[0])
            print(db_obj.upload_companies(tuple_obj[0]) + '1')
        else: return HttpResponse("Not updated")
    except AttributeError:
        print(2)
        tuple_obj = obj.parser()
        modify_obj.modify_company(tuple_obj[0])
        print(db_obj.upload_companies(tuple_obj[0]) + '2')
    return HttpResponse("Updated")


def login_user(request):

    if request.method == 'POST':
        user_form = LoginForm(data=request.POST)
        user = authenticate(username=user_form.data['username'],password=user_form.data['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('insurance_app:index')
        else:
            form = LoginForm()
            return render(request,'insurance_app/login_user.html',{'login_error':'User is not found','form':form})
    else:
        form = LoginForm()
        return render(request, 'insurance_app/login_user.html', context={'form':form})

def logout(request):
    auth.logout(request)
    return redirect('insurance_app:index')

#default_token_generator
def reset_password(request):
    if request.method == 'POST':
        form1 = PasswordResetForm(request.POST)
        if form1.is_valid():
            user = form1.save()
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Активация вашего аккаунта'
            message = render_to_string('insurance_app/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form1.cleaned_data.get('email')
            domain = to_email.split('@')[1]
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'insurance_app/activate_account.html', {'domain':domain})
    else:
        form1 = PasswordResetForm()
    return render(request, 'insurance_app/password_reset_form.html', {'form1': form1})

def register(request):
    if request.method == 'POST':
        form1 = SignupForm(request.POST)
        if form1.is_valid():
            user = form1.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Активация вашего аккаунта'
            message = render_to_string('insurance_app/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form1.cleaned_data.get('email')
            domain = to_email.split('@')[1]
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'insurance_app/activate_account.html', {'domain':domain})
    else:
        form1 = SignupForm()
    return render(request, 'insurance_app/register.html', {'form1': form1})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('insurance_app:add_userprofile')
    else:
        return HttpResponse('Activation link is invalid!')

def add_userprofile(request):

    if request.method == 'POST':
        user = request.user
        post_values = request.POST.copy()
        post_values['user'] = user
        form = UserProfileForm(post_values)
        if form.is_valid():
            post1 = form.save(commit=False)
            post1.save()
            return redirect('insurance_app:index')
    else:
        form = UserProfileForm()
    return render(request, 'insurance_app/add_userprofile.html', {'form': form})