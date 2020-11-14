from django.contrib import admin

from .models import *

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


# Определяем новый класс настроек для модели User
class UserAdmin(UserAdmin):
    inlines = (UserInline,)


# Перерегистрируем модель User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(Request)
admin.site.register(CompanyUser)
admin.site.register(CompanyInfo)
admin.site.register(Order)
