from bs4 import BeautifulSoup
import requests
import re
from fake_useragent import UserAgent
from .models import *
from django.utils import timezone
from .forms import UserProfileForm

class Updates:

    def gai(self,number):
        url = "https://baza-gai.com.ua/nomer/" + number
        r = requests.get(url, headers={"Accept": "application/json"})
        data = r.json()
        context = {}
        print(data)
        for operation in data['operations']:
            if operation['isLast'] and not data['stolen']:
                context['engine_capacity'] = operation['notes'].split(',')[-1].strip()
                context['model_year'] = operation['modelYear']
                context['brand'] = operation['vendor']
                context['model'] = operation['model']
                context['address'] = operation['address']
        return context

    def parser(self):
        rows = Company.objects.all()
        last_row = rows.last()
        try:
            last_id = last_row.id
        except AttributeError:
            last_id = 0

        companies_info=[]
        licenses = []
        id = last_id + 1
        headers = {'user-agent': UserAgent().random}
        r = requests.post(
            'https://kis.bank.gov.ua/?__VIEWSTATE=%2FwEPDwUKMjA0NDA5OTAxN2RkYp6DC6WJ1c7OZ5ZQtR%2FzO%2BgjVTw%3D&p_EDRPOU='
            '&p_REGNO=&p_FULLNAME=&p_IM_ST=%25null%25&p_IRL_FT=3&p_NFS=0&p_SVIDOTSTVO_SERIES=&p_SVIDOTSTVO_NO=&p_ACTDATE'
            '_FROM=&p_ACTDATE_TO=&p_ILD_NUMBER=&search=1&pagenum=-1&__VIEWSTATEGENERATOR=EC5CD28C', headers = headers)

        html = r.text
        soup = BeautifulSoup(html,'lxml')

        table = soup.find('table', class_='grid zebra')
        tr_list = table.find_all('tr')

        for tr in tr_list:
            if tr.find_all('td'):
                td_list=tr.find_all('td')
                dict_company = {'id':id}
                for td in td_list:
                    if td.find('a') and 'Детально' in td.text:
                         abbreviation,position=self.get_details(td.find('a').get('href'))
                         dict_company['abbreviation'] = abbreviation.strip()
                         director = director.replace(abbreviation.lower().strip(), ' ')
                         director_title=director.title()
                         dict_company['K_NAME'] = director_title
                         director=director.strip()
                         position = position.replace(',', ' ')
                         position = position.replace('-', ' ')
                         position = position.lower().replace(director, ' ')
                         dict_company['position'] = position.title()
                    elif td.get('headers')[0]=="K_NAME":
                        td.text.lower()
                        posada=['генеральний директор','виконуючий обов`язки голови правління','в.о. голови правління','директор',
                                'голова правління','гол. правління','президент']
                        director=td.text.lower()
                        for i in posada:
                            if i in director:
                                director=director.replace(i,' ')
                        director = director.replace('-', ' ')
                        director = director.replace(',', ' ')
                        dict_company['K_NAME'] = director
                    elif td.find('a') and 'Ліцензії' in td.text:
                        licenses=self.get_license(td.find('a').get('href'),id,licenses)
                    elif td.get('headers')[0]=="FILIALS":
                        continue
                    else:
                        dict_company[td.get('headers')[0]] = td.text
                companies_info.append(dict_company)
                id += 1
        return (companies_info,licenses)

    def get_details(self,url):
        new_url = 'https://kis.bank.gov.ua' + url
        headers = {'user-agent': UserAgent().random}

        r = requests.get(new_url,headers=headers)
        html = r.text
        soup = BeautifulSoup(html, 'lxml')

        abbreviation=soup.find(text='Скорочене найменування заявника (з установчих документів, у разі наявності)').parent.findNext('td').contents[0]
        position=soup.find(text="Прізвище, і'мя та по батькові і найменування посади керівника").parent.findNext('td').contents[0]
        return abbreviation,position

    def get_license(self,url,id,table_info):
        names = []
        just_names = []

        new_url = 'https://kis.bank.gov.ua' + url
        headers = {'user-agent': UserAgent().random}
        r = requests.get(new_url, headers=headers)
        html = r.text
        soup = BeautifulSoup(html, 'lxml')

        table = soup.find('table', class_='grid zebra')
        try:
            tr_list = table.find_all('tr')
            index = 0
            for tr in tr_list:
                if tr.find_all('th'):
                    th_list=tr.find_all('th')
                    for th in th_list:
                        names.append({th.get('id'):th.text})
                        just_names.append(th.get('id'))
                else:
                    td_list=tr.find_all('td')
                    dict_company = {}
                    for td in td_list:
                        if td.get('a'):
                            dict_company[just_names[index]] = td.find('a').get('href')
                        else:
                            dict_company[just_names[index]] = td.text
                        index += 1
                    dict_company['company_id']=id
                    table_info.append(dict_company)
                    index = 0
        except: pass
        return table_info

    def compare(self,rows,companies):
        changes = None
        keys = ['id','IAN_RO_DT','changes','IM_NUMIDENT','update_date']
        for row in rows:
            for company in companies:
                if int(row.IM_NUMIDENT) == int(company['IM_NUMIDENT']):
                    for key in company:
                        if str(getattr(row, key)) != str(company[key]) and key not in keys:
                            if changes == None:
                                changes = ''
                            changes += str(key) + ','
                        else:
                            continue
                    company['changes'] = changes
                    changes = None
                else: continue

class DataModify:

    def modify_company(self, companies):
        keys=['IAN_FULL_NAME','DIC_NAME','K_NAME','abbreviation','IND_OBL','position','F_ADR']
        for company in companies:
            for key in company:
                if 'IM_NUMIDENT' in key or 'IAN_RO_CODE' in key:
                    code = company[key]
                    match = re.findall(r'[!()_*&?.,><@A-Za-zА-Яа-я]', code)
                    for i in match:
                        code = code.replace(i, '')
                    try:
                        code_len = len(code.strip())
                        if 'IM_NUMIDENT' in key and code_len != 8:
                            code = None
                    except ValueError:
                        code = None
                    if code == '' or code == ' ':
                        code = None
                    company[key] = code
                elif 'IAN_RO_DT' in key:
                    date = company['IAN_RO_DT']
                    date_time_obj = datetime.datetime.strptime(date, '%d.%m.%Y %H:%M:%S')
                    company['IAN_RO_DT'] = date_time_obj
                # elif key in keys:
                #     company[key]=company[key].replace("'",'`')
                #     company[key]=company[key].replace('"','``')
            company['update_date']=str(timezone.now())[0:19]

    def modify_license(self,licenses):
        keys=['NFS_NAME','LT_NNR2','LT_NAME','IL_NAME','LT_NNR_DUPL','LT_NNR_REREG',
                        'LT_NNR_SUSPEND','LT_NNR_RESUME','IL_APPOINTMENT','IL_TERM']
        for license in licenses:
            for key in license:
                if 'DATE' in key:
                    data = license[key]
                    match = re.findall(r'[!(-)_*&?,><@]', data)
                    for i in match:
                        data = data.replace(i, '')
                    data = data.strip()
                    try:
                        date_time_obj = datetime.datetime.strptime(data, '%d.%m.%Y')
                    except ValueError:
                        date_time_obj = ''
                    license[key] = date_time_obj
                elif 'NFS_CODE' in key:
                    nfs_code=license[key]
                    try:
                        float_nfs_code=float(nfs_code)
                    except ValueError:
                        float_nfs_code=None
                    license[key] = float_nfs_code
                # elif key in keys:
                #     license[key] = license[key].replace("'", '`')
                #     license[key] = license[key].replace('"', '``')
            license['update_date'] = str(datetime.datetime.now())[0:19]

class DatabaseAccess:

    def get_user(self,id):
        user=db(db.site_user.auth_user == id).select().first()
        return user

    def get_auth_user(self,id):
        auth_user=db(db.auth_user.id == id).select().first()
        return auth_user

    def add_company_user(self,user,company_info):
        new_cu = CompanyUser(user=user, company_info=company_info)
        new_cu.save()

    def delete_company_user(self,user,company_info):
        CompanyUser.objects.get(user=user, company_info=company_info).delete()

    def change_company_info(self, IM_NUMIDENT, address,bank_props,position,pib,action_base):
        ci = CompanyInfo.objects.get(IM_NUMIDENT = IM_NUMIDENT)
        ci.info_address = address
        ci.bank_props = bank_props
        ci.position = position
        ci.pib = pib
        ci.action_base = action_base
        ci.save()

    def get_codes(self, identifier):
        data=[]
        rows = db(db.company).select()
        for row in rows:
            for key in row.keys():
                if str(identifier) in str(row[key]) and row.IM_NUMIDENT not in data:
                    data.append(row.IM_NUMIDENT)
                    break

        return data

    def get_full_name(self,code):

        rows = db(db.company.IM_NUMIDENT == code).select()
        name = rows[0].IAN_FULL_NAME

        return name

    def get_address(self,code):

        rows = db(db.company.IM_NUMIDENT == code).select()
        address = rows[0].F_ADR

        return address

    def get_director(self,code):

        rows = db(db.company.IM_NUMIDENT == code).select()
        director_name = rows[0].K_NAME

        return director_name

    def get_update_data(self):
        row = Company.objects.last()
        data = row.update_date
        return data

    def upload_companies(self, company_list):

        for i in range(len(company_list)):
            add_company = Company(**company_list[i])
            add_company.save()

        return "OK_company"

    def upload_licenses(self, license_list):

        for i in range(len(license_list)):
            db['license'].insert(**license_list[i])

        return "OK_license"

    def check_company(self, company_info, current_user, action):
        try:
            row = CompanyUser.objects.get(user=current_user, company_info = company_info)
            if action == 'add':
                return False
            elif action == 'delete' or action == 'change':
                return True
        except:
            if action == 'add':
                return True
            elif action == 'delete' or action == 'change':
                return False

    def create_company_info(self, IM_NUMIDENT, IAN_FULL_NAME):
        tmp = CompanyInfo(IM_NUMIDENT = IM_NUMIDENT, IAN_FULL_NAME = IAN_FULL_NAME)
        tmp.save()

    def insert_request(self, user, company_info, action):

        tmp = Request(user = user, company_info = company_info, action = action)
        tmp.save()

    def insert_change_request(self, user, company_info, address, bank_props, position, pib, action_base):

        tmp = Request(user = user, company_info = company_info, address = address,
                      bank_props = bank_props, position = position, pib = pib, action_base = action_base, action = 'change')
        tmp.save()

    def update_company_user(self):
        rows = Request.objects.all()
        for reqst in rows:
            if reqst.action == 'add' and reqst.confirm == True:
                check = self.check_company(reqst.company_info, reqst.user, 'add')
                if check:
                    self.add_company_user(reqst.user, reqst.company_info)
                Request.objects.get(id = reqst.id).delete()
            elif reqst.action == 'delete' and reqst.confirm == True:
                check = self.check_company(reqst.company_info, reqst.user, 'delete')
                print(check)
                if check:
                    print("JJJJJJJJJJJJJ")
                    self.delete_company_user(reqst.user, reqst.company_info)
                Request.objects.get(id = reqst.id).delete()
            elif reqst.action == 'change' and reqst.confirm == True:
                check = self.check_company(reqst.company_info, reqst.user, 'change')
                print(check)
                if check:
                    print("JJJJJJJJJJJJJ")
                    self.change_company_info(reqst.company_info.IM_NUMIDENT, reqst.address ,
                                             reqst.bank_props, reqst.position, reqst.pib, reqst.action_base)
                Request.objects.get(id = reqst.id).delete()

    def insert_name(self,name):

        db['name'].insert(name = name)

    def insert_order(self, user, company_info, reporting_date, calc_type):
        tmp = Order(user=user, company_info=company_info, reporting_date=reporting_date,
                    calc_type=calc_type, active=True,order_date = datetime.datetime.now())
        tmp.save()
        return tmp

    def find_order(self, user, company_info, reporting_date, calc_type):
        try:
            tmp = Order.objects.get(user=user, company_info=company_info, reporting_date=reporting_date, calc_type=calc_type, active=True)
            found = tmp
        except:
            found = None
        return found

    def find_offered_order(self, user, company_info, reporting_date, calc_type):
        print('x')
        try:
            print('z')
            tmp = Order.objects.get(user=user, company_info=company_info, reporting_date=reporting_date,
                                    calc_type=calc_type, offered=True)
            tmp.offered = False
            tmp.rejected = False
            tmp.active = True
            tmp.order_date = datetime.datetime.now()
            tmp.save()
            new_calc_type = True
            order_id = tmp.id
        except:
            new_calc_type = False
            order_id = None
        return new_calc_type,order_id



