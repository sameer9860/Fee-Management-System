from django.contrib import admin
from school.models import School, Grade, Fee, TempCSVFile


admin.site.register(School)
admin.site.register(Grade)
admin.site.register(Fee)
admin.site.register(TempCSVFile)
