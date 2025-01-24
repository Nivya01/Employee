from django.contrib import admin
from .models import Employee, EmployeeChildren

admin.site.register(EmployeeChildren)
admin.site.register(Employee)
