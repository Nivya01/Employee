from django.db import models
from django.core.exceptions import ValidationError
import re

def validate_name(value):
    if not re.match("^[A-Za-z ]+$", value):
        raise ValidationError("Name must only contain alphabets and spaces.")

def validate_emp_age(value):
    if not (18 <= value <= 65):
        raise ValidationError("Age must be between 18 to 65.")

def validate_child_age(value, employee):
    if not (0 <= value <= 50):
        raise ValidationError("Child age must be between 0 and 50.")

    if value >= employee.emp_age:
        raise ValidationError("Child age must be less than employee age.")
    
def validate_emp_gender(value):
    if value not in ['male', 'female']:
        raise ValidationError("Employee gender must be male or female.") 

class Employee(models.Model): 
    emp_id = models.AutoField(primary_key=True)
    emp_name = models.CharField(max_length=100, validators=[validate_name])
    emp_age = models.IntegerField(validators=[validate_emp_age])
    emp_gender = models.CharField(max_length=10, validators=[validate_emp_gender])
    emp_email = models.EmailField(unique=True)
    def save(self, *args, **kwargs):
        if self.emp_name:
            self.emp_name = self.emp_name.capitalize()
        if self.emp_email:
            self.emp_email = self.emp_email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.emp_name

class EmployeeChildren(models.Model):
    child_id = models.AutoField(primary_key=True)
    child_name = models.CharField(max_length=100, validators=[validate_name])
    child_age = models.IntegerField(validators=[validate_child_age])
    employee = models.ForeignKey(Employee, related_name="children", on_delete=models.CASCADE)

    def __str__(self):
        return self.child_name





