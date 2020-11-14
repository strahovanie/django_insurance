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
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

def index(request):
    companies = Company.objects.all()
    template = loader.get_template('insurance_app/index.html')
    context = {
        'companies': companies,
    }
    return HttpResponse(template.render(context, request))

def company_list(request):
    user = request.user
    try:
        user_companies = CompanyUser.objects.filter(user=user)
    except:
        user_companies = None
    return render(request, 'insurance_app/company_list.html', {'user_companies': user_companies})

@csrf_exempt
def add_info_to_company(request, company_IM_NUMIDENT):
    db_obj = DatabaseAccess()
    user = request.user
    company_info = CompanyInfo.objects.get(IM_NUMIDENT = company_IM_NUMIDENT)
    address = request.POST['info_address']
    bank_props = request.POST['bank_props']
    position = request.POST['position']
    pib = request.POST['pib']
    action_base = request.POST['action_base']
    db_obj.insert_change_request(user, company_info, address, bank_props, position, pib, action_base)
    return redirect('insurance_app:company_detail', company_IM_NUMIDENT=company_IM_NUMIDENT)

def company_detail(request, company_IM_NUMIDENT):
    last_date = Company.objects.last().update_date
    str_last_date = last_date.strftime("%d-%m-%Y %H:%M")
    user_flag = False
    user = request.user
    company_info = CompanyInfo.objects.get(IM_NUMIDENT = company_IM_NUMIDENT)
    form1 = AddInfoToCompany(instance=company_info)
    try:
        company = Company.objects.get(IM_NUMIDENT=company_IM_NUMIDENT, update_date=last_date)
        rows = CompanyUser.objects.filter(user=user)
        for row in rows:
            if row.company_info.IM_NUMIDENT == company.IM_NUMIDENT:
                user_flag = True
    except ObjectDoesNotExist:
        company = None
    return render(request, 'insurance_app/company_detail.html', {'company': company, 'user_flag': user_flag, 'str_last_date':str_last_date, 'form1':form1})


@csrf_exempt
def update_database(request):
    if request.is_ajax() and request.method == 'POST':
        alert_data = request.POST["alert_data"]
        if int(alert_data) > 7:
            processor = Processor()
            thread = threading.Thread(target=processor.update_company)
            thread.start()
            return JsonResponse({'context': 'База даних компаній буде оновлена'})
        elif alert_data.strip() == 'None':
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


def add_company(request):
    user = request.user
    template = loader.get_template('insurance_app/add_company.html')
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
        'form1': form1,
        'form2': form2,
        'form3': form3,
        'form4': form4,
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
def add_chosen_company(request):
    db_obj = DatabaseAccess()
    choice_id = request.POST['company']
    current_company = Company.objects.get(id=choice_id)
    try:
        company_info = CompanyInfo.objects.get(IM_NUMIDENT = current_company.IM_NUMIDENT)
    except:
        db_obj.create_company_info(current_company.IM_NUMIDENT, current_company.IAN_FULL_NAME)
        company_info = CompanyInfo.objects.get(IM_NUMIDENT=current_company.IM_NUMIDENT)
    user = request.user
    db_obj.insert_request(user, company_info, 'add')
    print('Action "add" is added to requests table')
    return redirect('insurance_app:add_company')

@csrf_exempt
def delete_chosen_company(request):
    db_obj = DatabaseAccess()
    choice_id = request.POST['company']
    company_info = CompanyUser.objects.get(id=choice_id).company_info
    user = request.user
    # fromaddr = 'strahovka.work2020@gmail.com'
    # toaddr = auth_user.email
    # toaddr = current_company.email

    # username = 'strahovka.work2020@gmail.com'
    # password = 'cdnblpUYBvdlH8'
    # server = smtplib.SMTP('smtp.gmail.com:587')
    db_obj.insert_request(user, company_info, 'delete')
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

def logout(request):
    auth.logout(request)
    return redirect('insurance_app:index')

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
        form = UserProfileForm({'user': user})
        post = form.save()
        post.save()
        login(request, user)
        return redirect('insurance_app:add_userprofile')
    else:
        return HttpResponse('Activation link is invalid!')

def add_userprofile(request):

    if request.method == 'POST':
        user = request.user
        form = UserProfileForm(request.POST, instance=user.userprofile)
        if form.is_valid():
            post1 = form.save(commit=False)
            post1.save()
            return redirect('insurance_app:index')
    else:
        user = request.user
        try:
            form = UserProfileForm(instance=user.userprofile)
        except: form = None
    return render(request, 'insurance_app/add_userprofile.html', {'form': form})

def auto_insurance(request):
    form = AutoInsurance()
    return render(request, 'insurance_app/auto_insurance.html', {'form': form})

@csrf_exempt
def auto_fill(request):
    number = request.POST["number"]
    update_obj = Updates()
    context = update_obj.gai(number)
    return JsonResponse({'context':context})

def order(request):
    template = loader.get_template('insurance_app/order.html')
    if request.POST:
        db_obj = DatabaseAccess()
        choice_id = request.POST['company']
        company_info = CompanyUser.objects.get(id=choice_id).company_info
        print(request.POST)
        user = request.user
        reporting_date = request.POST['reporting_date']
        calc_type = request.POST.getlist('calc_type',False)
        if calc_type == False:
            form = OrderForm(request.POST)
            form.fields['company']._set_queryset(CompanyUser.objects.filter(user=user))
            context = {
                'form': form,
            }
            return HttpResponse(template.render(context, request))
        else:
            db_obj.insert_order(user, company_info, reporting_date, calc_type)
            return redirect('insurance_app:order')
    else:
        user = request.user
        user_orders = Order.objects.order_by("-id").filter(user=user)
        if len(user_orders)>3:
            user_orders3 = Order.objects.order_by("-id").filter(user=user)[:3]
        else: user_orders3 = []
        form = OrderForm(instance=user)
        form.fields['company']._set_queryset(CompanyUser.objects.filter(user=user))
        context = {
            'form': form,
            'user_orders':user_orders,
            'user_orders3':user_orders3
        }
        return HttpResponse(template.render(context, request))

def order_history(request):
    template = loader.get_template('insurance_app/order_history.html')
    user = request.user
    user_orders = Order.objects.order_by("-id").filter(user=user)
    context = {
        'user_orders': user_orders,
    }
    return HttpResponse(template.render(context, request))

def csrf_failure(request, reason=""):
    ctx = {'message': 'Виникла помилка. Перевірте, чи підключені cookies у вашому браузері або перезавантажте сторінку, або спробуйте увійти ще раз'}
    return render(request, 'insurance_app/csrf_failure.html', ctx)