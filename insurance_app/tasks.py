# celery -A insurance worker -l INFO
# celery -A insurance beat -l INFO --max-interval=600

from celery import shared_task
from insurance.celery import celery_app
from .classes import DatabaseAccess,Updates,DataModify
import datetime
from .models import *
from django.utils import timezone

@celery_app.task
def adding_task():
    db_obj = DatabaseAccess()
    obj = Updates()
    modify_obj = DataModify()
    try:
        data = db_obj.get_update_data()
        now = timezone.now()
        if (now - data).days > 7:
            tuple_obj = obj.parser()
            rows = Company.objects.filter(update_date = data)
            modify_obj.modify_company(tuple_obj[0])
            obj.compare(rows, tuple_obj[0])
            print(db_obj.upload_companies(tuple_obj[0]) + '1')
            return 'updated1'
        else:
            return "not updated"
    except AttributeError:
        tuple_obj = obj.parser()
        modify_obj.modify_company(tuple_obj[0])
        print(db_obj.upload_companies(tuple_obj[0]) + '2')
    return 'updated2'
