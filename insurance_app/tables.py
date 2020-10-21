import django_tables2 as tables
from .models import Company

class CompanyTable(tables.Table):
    class Meta:
        model = Company
        template_name = "django_tables2/bootstrap.html"
        fields = ("IAN_FULL_NAME", "FIN_TYPE", "IM_NUMIDENT", "IAN_RO_SERIA", "IAN_RO_CODE", "IAN_RO_DT", "DIC_NAME" )