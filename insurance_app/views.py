from django.http import HttpResponse
from .classes import *
from .models import Company
from django.template import loader
from django.contrib import auth
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from .forms import UserProfileForm, UserUpdateForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def index(request):
    companies = Company.objects.all()
    template = loader.get_template('insurance_app/index.html')
    context = {
        'companies': companies,
    }
    return HttpResponse(template.render(context, request))

def accept_request(id):
    confirm_request = Request.objects.get(id=id)
    confirm_request.confirm=True
    confirm_request.save()

def admin_page(request):
    user = request.user
    admin = user.is_superuser
    requests = Request.objects.all()
    template = loader.get_template('insurance_app/admin_page.html')
    context = {
        'admin': admin,
        'requests': requests
    }
    return HttpResponse(template.render(context, request))

def add_company(request):
    user = request.user
    last_company = Company.objects.last()
    last_date = last_company.update_date
    companies = Company.objects.filter(update_date = last_date)
    template = loader.get_template('insurance_app/add_company.html')
    if request.method == "POST":
        form1 = UserUpdateForm(request.POST,instance=user)
        form2 = UserProfileForm(request.POST,instance=user.userprofile)
        form3 = PasswordChangeForm(data=request.POST, user=user)
        if form1.is_valid() and form2.is_valid() and form3.is_valid():
            post1 = form1.save(commit=False)
            post2 = form2.save(commit=False)
            post3 = form3.save(commit=False)
            post1.save()
            post2.save()
            post3.save()
            auth.login(request, user)
            return redirect('insurance_app:add_company')
    else:
        form1 = UserUpdateForm(instance=user)
        form2 = UserProfileForm(instance=user.userprofile)
        form3 = PasswordChangeForm(user=user)
    context = {
        'user' : user,
        'companies': companies,
        'form1': form1,
        'form2': form2,
        'form3': form3
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
def add_chosen_company(request):
    db_obj = DatabaseAccess()
    last_company = Company.objects.last()
    last_date = last_company.update_date
    rows = Company.objects.filter(update_date = last_date)
    choice_id = request.POST.get('choice_id')
    action = request.POST.get('action')
    current_company = Company.objects.get(id=choice_id)
    user = request.user
    # fromaddr = 'strahovka.work2020@gmail.com'
    # toaddr = auth_user.email
    # toaddr = current_company.email

    # username = 'strahovka.work2020@gmail.com'
    # password = 'cdnblpUYBvdlH8'
    # server = smtplib.SMTP('smtp.gmail.com:587')
    if action == 'add':
        db_obj.insert_request(user, current_company, action)
        print('Action "add" is added to requests table')
        # server.starttls()
        # server.login(username, password)
        # msg1 = 'Потвердите что вашу компанию обслуживает ' + str(site_user.first_name)
        # msg2 = 'Confirm that you want to add this company' + str(current_company.IAN_FULL_NAME) + str(
        #     current_company.IM_NUMIDENT)
        # server.sendmail(fromaddr, toaddr, msg2.encode("utf8"))
        # server.quit()
    elif action == 'delete':
        db_obj.insert_request(user, current_company, action)
        print('Action "delete" is added to requests table')
        # server.starttls()
        # msg3 = 'Confirm that you want to delete this company' + str(current_company.IAN_FULL_NAME) + str(
        #     current_company.IM_NUMIDENT)
        # server.login(username, password)
        # server.sendmail(fromaddr, toaddr, msg3.encode("utf8"))
        # server.quit()
    # form1 = Form(db.auth_user, auth_user, deletable=False, formstyle=FormStyleBulma)
    # form2 = Form(db.site_user, site_user, deletable=False, formstyle=FormStyleBulma)
    # logger.info('Add method OK')
    return JsonResponse({'context':'hi'})


def update_company(request):
    db_obj = DatabaseAccess()
    obj = Updates()
    modify_obj = DataModify()
    try:
        data = db_obj.get_update_data()
        now = datetime.datetime.now(datetime.timezone.utc)
        if (now - data).days > 7:
            print(1)
            tuple_obj = obj.parser()
            rows = Company.objects.filter(update_date = data)
            modify_obj.modify_company(tuple_obj[0])
            obj.compare(rows, tuple_obj[0])
            print(tuple_obj[0])
            print(db_obj.upload_companies(tuple_obj[0]) + '1')
        else: return HttpResponse("Not updated")
    except AttributeError:
        print(2)
        tuple_obj = obj.parser()
        modify_obj.modify_company(tuple_obj[0])
        print(db_obj.upload_companies(tuple_obj[0]) + '2')
    return HttpResponse("Updated")



def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('insurance_app:index')
        else:
            return render(request,'insurance_app/login.html',{'login_error':'User is not found'})
    else:
        return render(request, 'insurance_app/login.html')

def logout(request):
    auth.logout(request)
    return redirect('insurance_app:index')

def register(request):
    form=UserCreationForm()
    if request.method == 'POST':
        newuser_form = UserCreationForm(request.POST)
        if newuser_form.is_valid():
            newuser_form.save()
            auth.authenticate(username=newuser_form.cleaned_data['username'],password=newuser_form.cleaned_data['password2'])
            return redirect('insurance_app:index')
        else:
            form=newuser_form
    return render(request,'insurance_app/register.html',context={'form': form})