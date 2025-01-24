from django.urls import path
from . import views

urlpatterns = [
    path('employee/', views.create_or_update_employee, name='create_or_update_employee'),
    path('filter_employees/', views.filter_employees, name='filter_employees'),
]
