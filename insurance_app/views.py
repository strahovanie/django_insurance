import os
import pandas
from .classes import *
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
from django.db.models import Q

def index(request):
    # companu = CompanyInfo.objects.get(IM_NUMIDENT=20693867)
    # tmp=Order(user=request.user, company_info=companu, reporting_date='2020-06-21', calc_type='1', offered=True)
    # tmp.save()
    companies = Company.objects.all()
    template = loader.get_template('insurance_app/index.html')
    context = {
        'companies': companies,
    }
    company_code = "19209435"
    api_key = "VChFavBht5ug"
    return HttpResponse(template.render(context, request))

def choose_company(request):
    template1 = loader.get_template('insurance_app/choose_company.html')
    company_user = CompanyUser.objects.filter(user=request.user)
    print(company_user)
    if company_user:
        context = {'company_user': company_user}
        return HttpResponse(template1.render(context, request))
    else:
        return render(request, 'insurance_app/choose_company_info.html')

def company_is_chosen(request, IM_NUMIDENT):
    template1 = loader.get_template('insurance_app/text_page.html')
    request.session['company_IM_NUMIDENT'] = IM_NUMIDENT
    company = Company.objects.filter(IM_NUMIDENT=IM_NUMIDENT).last()
    context = {'text': 'Ви увійшли у компанію '+ company.IAN_FULL_NAME}
    return HttpResponse(template1.render(context, request))

def company_logout(request, IM_NUMIDENT):
    template1 = loader.get_template('insurance_app/text_page.html')
    request.session['company_IM_NUMIDENT'] = None
    company = Company.objects.filter(IM_NUMIDENT=IM_NUMIDENT).last()
    context = {'text': 'Ви вийшли з компанії '+ company.IAN_FULL_NAME}
    return HttpResponse(template1.render(context, request))

def company_list(request):
    user = request.user
    try:
        user_companies = CompanyUser.objects.filter(user=user)
    except:
        user_companies = None
    try:
        company_docs = Documents.objects.filter(user=user, type_of_contract = 'contract')
    except:
        company_docs = None
    try:
        session_company = request.session['company_IM_NUMIDENT']
        print(session_company)
    except:
        session_company = None
    return render(request, 'insurance_app/company_list.html', {'user_companies': user_companies,
                                                               'session_company': session_company,
                                                               'company_docs': company_docs})

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
    template1 = loader.get_template('insurance_app/text_page.html')
    context = {'text': 'Запит на зміну інформації про компанію ' + company_info.IAN_FULL_NAME + ' був відправлений адміністратору'}
    return HttpResponse(template1.render(context, request))

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

def admin_page_contract(request):
    user = request.user
    admin = user.is_superuser
    docs = Documents.objects.all()
    template = loader.get_template('insurance_app/admin_page_contract.html')
    context = {
        'admin': admin,
        'docs': docs,
    }
    return HttpResponse(template.render(context, request))

def received_contract_act(request, doc_id):
    user = request.user
    doc = Documents.objects.get(id=doc_id)
    if request.POST:
        file_location_received = request.POST['file_location_received']
        doc.file_location_received = file_location_received
        doc.received = True
        doc.signed_by_client = True
        doc.save()
        return redirect('insurance_app:admin_page_contract')
    else:
        doc_form = DocContractActForm()
        template = loader.get_template('insurance_app/received_contract_act.html')
        context = {
            'doc':doc,
            'user':user,
            'doc_form': doc_form,
        }
        return HttpResponse(template.render(context, request))

def received_bill(request, doc_id):
    user = request.user
    doc = Documents.objects.get(id=doc_id)
    if request.POST:
        file_location_received = request.POST['file_location_received']
        current_payment_amount = request.POST['current_payment_amount']
        doc.file_location_received = file_location_received
        doc.current_payment_amount = current_payment_amount
        doc.received = True
        doc.signed_by_client = True
        if float(current_payment_amount) >= doc.full_payment_amount:
            doc.paid_in_full = True
        doc.save()
        return redirect('insurance_app:admin_page_contract')
    else:
        doc_form = DocBillForm()
        template = loader.get_template('insurance_app/received_bill.html')
        context = {
            'doc':doc,
            'user':user,
            'doc_form': doc_form,
        }
        return HttpResponse(template.render(context, request))

def add_company(request):
    user = request.user
    template = loader.get_template('insurance_app/add_company.html')
    if request.method == "POST":
        pass
    else:
        form3 = AddCompanyForm()
        form4 = DeleteCompanyForm()
        form4.fields['company']._set_queryset(CompanyUser.objects.filter(user = user))
    context = {
        'user' : user,
        'form3': form3,
        'form4': form4,
    }
    return HttpResponse(template.render(context, request))

def user_page(request):
    user = request.user
    template = loader.get_template('insurance_app/user_page.html')
    if request.method == "POST":
        form1 = UserUpdateForm(request.POST,instance=user)
        form2 = UserProfileForm(request.POST,instance=user.userprofile)
        if form1.is_valid() and form2.is_valid():
            post1 = form1.save(commit=False)
            post2 = form2.save(commit=False)
            post1.save()
            post2.save()
            template1 = loader.get_template('insurance_app/text_page.html')
            context = {'text': 'Данні аккаунта було успішно змінено '}
            return HttpResponse(template1.render(context, request))
    else:
        form1 = UserUpdateForm(instance=user)
        form2 = UserProfileForm(instance=user.userprofile)
    context = {
        'user' : user,
        'form1': form1,
        'form2': form2,
    }
    return HttpResponse(template.render(context, request))

def create_contract(request, IM_NUMIDENT):
    print(IM_NUMIDENT)
    user = request.user
    template = loader.get_template('insurance_app/create_contract.html')
    company_info = CompanyInfo.objects.get(IM_NUMIDENT = IM_NUMIDENT)
    if request.POST:
        with open('insurance_app/contract_files_sended/contract_'+IM_NUMIDENT+'.txt', 'w') as f:
            f.write("DOC"+IM_NUMIDENT)
        user = request.user
        user_email = user.email
        mail_subject = 'Договір '
        filepath_result = 'insurance_app/contract_files_sended/contract_'+IM_NUMIDENT+'.txt'
        message = render_to_string('insurance_app/send_result.html', {
            'user': user,
            'domain': settings.DEFAULT_DOMAIN,
        })
        email = EmailMessage(
            mail_subject, message, to=[user_email]
        )
        email.attach_file(filepath_result)
        email.send()
        tmp = Documents.objects.get(company_info = company_info, type_of_contract = 'contract')
        tmp.signed_by_us = True
        tmp.sended = True
        tmp.file_location_sended = 'insurance_app/contract_files_sended/contract_'+IM_NUMIDENT+'.txt'
        tmp.save()
        return redirect('insurance_app:index')
    else:
        context = {'IM_NUMIDENT': IM_NUMIDENT,
                   'company_info': company_info}
    return HttpResponse(template.render(context, request))

@csrf_exempt
def add_chosen_company(request):
    create_contract_flag = False
    db_obj = DatabaseAccess()
    user = request.user
    choice_id = request.POST['company']
    current_company = Company.objects.get(id=choice_id)
    try:
        company_info = CompanyInfo.objects.get(IM_NUMIDENT = current_company.IM_NUMIDENT)
    except:
        db_obj.create_company_info(current_company.IM_NUMIDENT, current_company.IAN_FULL_NAME)
        company_info = CompanyInfo.objects.get(IM_NUMIDENT=current_company.IM_NUMIDENT)
    try:
        contract_get = Documents.objects.get(company_info = company_info, type_of_contract = 'contract')
    except:
        tmp = Documents(user=user, company_info=company_info, type_of_contract="contract")
        tmp.save()
        create_contract_flag = True
        print(tmp)
    db_obj.insert_request(user, company_info, 'add')
    IM_NUMIDENT = company_info.IM_NUMIDENT
    print('Action "add" is added to requests table')
    if create_contract_flag:
        return redirect('insurance_app:create_contract', IM_NUMIDENT = IM_NUMIDENT)
    else:
        template1 = loader.get_template('insurance_app/text_page.html')
        context = {'text': 'Запит на додання компанії ' + current_company.IAN_FULL_NAME + ' був відправлений адміністратору'}
        return HttpResponse(template1.render(context, request))

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
    template1 = loader.get_template('insurance_app/text_page.html')
    context = {'text': 'Запит на видалення компанії ' + company_info.IAN_FULL_NAME + ' був відправлений адміністратору'}
    return HttpResponse(template1.render(context, request))

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

def order(request,order_id):
    template = loader.get_template('insurance_app/order.html')
    try:
        session_order_company = request.session['company_IM_NUMIDENT']
        session_company = CompanyInfo.objects.get(IM_NUMIDENT = session_order_company)
    except:
        session_company = None
    user = request.user
    print(session_company)
    if session_company:
        user_orders_offered = Order.objects.order_by("-order_date").filter(user=user, company_info = session_company,
                                                            offered=True, rejected=False,active=False)
        user_orders = Order.objects.order_by("-order_date").filter(user=user, company_info=session_company,active=True)
        print(user_orders_offered)
        if len(user_orders_offered) > 3:
            user_orders_offered3 = Order.objects.order_by("-order_date").filter(user=user, company_info = session_company,
                                                                offered=True, rejected=False, active=False)[:3]
        else: user_orders_offered3 = []
    else:
        user_orders_offered = []
        user_orders = []
        user_orders_offered3 = []
    if request.POST:
        print(request.POST)
        db_obj = DatabaseAccess()
        choice_id = request.session['company_IM_NUMIDENT']
        print(choice_id)
        company_info = CompanyInfo.objects.get(IM_NUMIDENT=choice_id)
        user = request.user
        reporting_date = request.POST['reporting_date']
        calc_type = request.POST['calc_type']
        new_calc_type, order = db_obj.find_offered_order(user, company_info, reporting_date, calc_type)
        if not new_calc_type:
            order = db_obj.insert_order(user, company_info, reporting_date, calc_type)
        file_path = "insurance_app/xlsx_files/r3_"+choice_id+".xlsx"
        print('XXX')
        print(calc_type)
        print(type(calc_type))
        if calc_type == '1':
            print(calc_type)
            print(os.listdir)
            print(os.path.exists(file_path))
            if os.path.exists(file_path):
                print("KKK")
                return redirect('insurance_app:show_count_result', order_id = order.id)
            else:
                return redirect('insurance_app:show_count_error', order_id=order.id, reason='not_enough_data')
        else:
            return redirect('insurance_app:order', 0)
    else:
        if order_id == 0:
            form = OrderForm()
            order = 0
        elif order_id!=0:
            try:
                order = Order.objects.get(id=order_id)
                print(order.company_info.IAN_FULL_NAME)
                if order.user == user and order.company_info.IM_NUMIDENT == session_order_company:
                    form = OrderForm({'reporting_date': str(order.reporting_date), 'calc_type': str(order.calc_type)})
                else:
                    form = None
                    order = None
            except:
                form = None
                order = None
        context = {
            'form': form,
            'order': order,
            'user_orders': user_orders,
            'user_orders_offered':user_orders_offered,
            'user_orders_offered3': user_orders_offered3,
            'session_company': session_company,
        }
        return HttpResponse(template.render(context, request))

def show_count_result(request, order_id):
    template = loader.get_template('insurance_app/show_count_result.html')
    if request.POST:
        order = Order.objects.get(id=order_id)
        doc_act = Documents.objects.get(order_id=order_id, type_of_contract = 'act')
        doc_act.sended = True
        doc_act.save()
        doc_bill= Documents.objects.get(order_id=order_id, type_of_contract = 'bill')
        doc_bill.sended = True
        doc_bill.save()
        filepath_act = doc_act.file_location_sended
        filepath_bill = doc_bill.file_location_sended
        order.accepted = True
        order.save()
        user = request.user
        user_email = user.email
        mail_subject = 'Результат замовлення № ' + str(order.id)
        filepath_result = order.result_file
        message = render_to_string('insurance_app/send_result.html', {
            'user': user,
            'domain': settings.DEFAULT_DOMAIN,
        })
        email = EmailMessage(
            mail_subject, message, to=[user_email]
        )
        email.attach_file(filepath_result)
        email.attach_file(filepath_act)
        email.attach_file(filepath_bill)
        email.send()
        return redirect('insurance_app:index')
    else:
        file_path = "insurance_app/xlsx_files/r3_32717175.xlsx"
        data = pandas.read_excel(file_path, 'Лист1', usecols="C")
        new_data = data.to_dict('index')
        print(new_data)
        output_data = new_data[1]['Всього:'] + 5
        order = Order.objects.get(id = order_id)
        order.enough_data = True
        order.done = True
        order.result_file = 'insurance_app/result_files_sended/result_'+order.company_info.IM_NUMIDENT+'_'+order.calc_type+'_'+str(order.reporting_date)+'.txt'
        order.save()
        with open('insurance_app/result_files_sended/result_'+order.company_info.IM_NUMIDENT+'_'+order.calc_type+'_'+str(order.reporting_date)+'.txt', 'w') as f:
            f.write(str(output_data))
        with open('insurance_app/act_files_sended/act_'+order.company_info.IM_NUMIDENT+'_'+order.calc_type+'_'+str(order.reporting_date)+'.txt', 'w') as f:
            f.write("ACT"+order.company_info.IM_NUMIDENT)
        tmp1 = Documents(user=request.user, company_info = order.company_info, type_of_contract='act', order_id = order.id,
                        file_location_sended = 'insurance_app/act_files_sended/act_'+order.company_info.IM_NUMIDENT+'_'+order.calc_type+'_'+str(order.reporting_date)+'.txt',
                        signed_by_us = True)
        tmp1.save()
        with open('insurance_app/bill_files_sended/bill_'+order.company_info.IM_NUMIDENT+'_'+order.calc_type+'_'+str(order.reporting_date)+'.txt', 'w') as f:
            f.write("BILL"+order.company_info.IM_NUMIDENT)
        tmp2 = Documents(user=request.user, company_info=order.company_info, type_of_contract='bill', order_id=order.id,
                        file_location_sended='insurance_app/bill_files_sended/bill_' + order.company_info.IM_NUMIDENT + '_' + order.calc_type + '_' + str(
                            order.reporting_date) + '.txt',
                        signed_by_us=True, full_payment_amount = 500.0, current_payment_amount = 0.0)
        tmp2.save()
        context = {'output_data': output_data, 'order_id': order_id}
    return HttpResponse(template.render(context, request))


def show_count_error(request, order_id, reason):
    template = loader.get_template('insurance_app/show_count_error.html')
    if reason == 'not_enough_data':
        error = 'Не вистачає даних Розділу 3 для цього виду розрахунку.' \
                ' Будь ласка, перейдіть у вкладку "Завантаження" та завантажте Розділ 3'
    context = {'error': error}
    return HttpResponse(template.render(context, request))

def order_history(request):
    template = loader.get_template('insurance_app/order_history.html')
    user = request.user
    try:
        session_company = request.session['company_IM_NUMIDENT']
        user_company = CompanyInfo.objects.get(IM_NUMIDENT = session_company)
    except:
        session_company = None
        user_company = None
    if user_company:
        user_orders = Order.objects.order_by("-order_date").filter(
        Q(user=user, company_info = user_company, active=True) | Q(user=user, company_info = user_company, offered=True, rejected=True))
    else:
        user_orders = None
    context = {
        'user_orders': user_orders,
        'session_company': session_company,
        'user_company' : user_company,
    }
    return HttpResponse(template.render(context, request))

def show_order(request, order_id):
    template = loader.get_template('insurance_app/show_order.html')
    user = request.user
    IM_NUMIDENT = request.session['company_IM_NUMIDENT']
    try:
        order = Order.objects.get(id=order_id)
        if order.user == user and order.company_info.IM_NUMIDENT == IM_NUMIDENT:
            user_flag = True
        else:
            user_flag = False
        with open('insurance_app/result_files_sended/result_' + order.company_info.IM_NUMIDENT + '_'
                  + order.calc_type + '_' + str(order.reporting_date) + '.txt', 'r') as f:
            file_info = f.read()
    except:
        order = None
        user_flag = None
        file_info = None
    context = {'order': order, 'user_flag': user_flag, 'file_info': file_info}
    return HttpResponse(template.render(context, request))

def reject_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.rejected = True
    order.order_date = datetime.datetime.now()
    order.save()
    return redirect('insurance_app:order', order_id = 0)

def order_offered(request):
    template = loader.get_template('insurance_app/order_offered.html')
    user = request.user
    try:
        session_company = request.session['company_IM_NUMIDENT']
        user_company = CompanyInfo.objects.get(IM_NUMIDENT = session_company)
    except:
        session_company = None
        user_company = None
    if session_company:
        user_orders_offered = Order.objects.order_by("-order_date").filter(user=user,company_info = user_company,
                                                                           offered=True,rejected=False,active=False)
    else: user_orders_offered = None
    print(user_orders_offered)
    context = {
        'user_orders_offered' : user_orders_offered,
        'session_company': session_company,
        'user_company': user_company
    }
    return HttpResponse(template.render(context, request))

def csrf_failure(request, reason=""):
    ctx = {'message': 'Виникла помилка. Перевірте, чи підключені cookies у вашому браузері або перезавантажте сторінку, або спробуйте увійти ще раз'}
    return render(request, 'insurance_app/csrf_failure.html', ctx)

def documents(request, IM_NUMIDENT):
    template = loader.get_template('insurance_app/documents.html')
    company_documents = Documents.objects.filter(company_info = IM_NUMIDENT).order_by("order_id")
    company_name = CompanyInfo.objects.get(IM_NUMIDENT = IM_NUMIDENT).IAN_FULL_NAME
    context = {
        'company_documents': company_documents,
        'company_name': company_name,
    }
    return HttpResponse(template.render(context, request))

def tryx(request):
    template = loader.get_template('insurance_app/try.html')
    return render(request, 'insurance_app/try.html')