from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils.translation import gettext_lazy as _

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,blank=True)
    mobile_phone = models.CharField(max_length=200, blank=True)
    work_phone = models.CharField(max_length=200, blank=True)
    email2 = models.EmailField(max_length=200, blank=True)

    def __unicode__(self):
        return self.user

    def set_user(self, user):
        self.user = user

class Company(models.Model):
    IAN_FULL_NAME = models.CharField(max_length=200)
    FIN_TYPE = models.CharField(max_length=200)
    IM_NUMIDENT = models.CharField(max_length=8,null=False)
    IAN_RO_SERIA = models.CharField(max_length=200,null=True,blank=True)
    IAN_RO_CODE = models.CharField(max_length=8,null=True,blank=True)
    IAN_RO_DT = models.DateTimeField(null=True,blank=True)
    DIC_NAME = models.CharField(max_length=200,null=True,blank=True)
    F_ADR = models.CharField(max_length=300,null=True,blank=True)
    IA_PHONE_CODE = models.CharField(max_length=200,null=True,blank=True)
    IA_PHONE = models.CharField(max_length=200,null=True,blank=True)
    IA_EMAIL = models.CharField(max_length=200,null=True,blank=True)
    IND_OBL = models.CharField(max_length=200,null=True,blank=True)
    K_NAME = models.CharField(max_length=200,null=True,blank=True)
    abbreviation = models.CharField(max_length=200,null=True,blank=True)
    position = models.CharField(max_length=200,null=True,blank=True)
    update_date = models.DateTimeField(null=True,blank=True)
    changes = models.CharField(max_length=800,null=True,blank=True)

class CompanyInfo(models.Model):
    IM_NUMIDENT = models.CharField(max_length=8,null=False, primary_key=True)
    IAN_FULL_NAME = models.CharField(max_length=200)
    info_address = models.CharField(max_length=200, blank=True)
    bank_props = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=200, blank=True)
    pib = models.CharField(max_length=200, blank=True)
    action_base = models.CharField(max_length=200, blank=True)

class CompanyUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_info = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE)

class Documents(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_info = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE)
    type_of_contract = models.CharField(max_length=200)
    order_id = models.IntegerField(null=True)
    file_location_sended = models.CharField(max_length=200,blank=True)
    file_location_received = models.CharField(max_length=200, blank=True)
    full_payment_amount = models.FloatField(null=True)
    current_payment_amount = models.FloatField(null=True)
    paid_in_full = models.BooleanField(default=False)
    signed_by_us = models.BooleanField(default=False)
    signed_by_client = models.BooleanField(default=False)
    sended = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_info = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, blank=True)
    bank_props = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=200, blank=True)
    pib = models.CharField(max_length=200, blank=True)
    action_base = models.CharField(max_length=200, blank=True)
    action = models.CharField(max_length=200)
    request_date = models.DateTimeField(default=datetime.datetime.now())
    confirm = models.BooleanField(default=False)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_info = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE)
    reporting_date = models.DateField()
    calc_type = models.CharField(max_length=200)
    order_date = models.DateTimeField(default=datetime.datetime.now())
    offered = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    enough_data = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    result_file = models.CharField(max_length=200, null=True)
    accepted = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    payment = models.BooleanField(default=False)