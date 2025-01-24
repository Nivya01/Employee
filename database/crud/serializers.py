from rest_framework import serializers
from .models import Employee, EmployeeChildren,validate_name,validate_child_age

class EmployeeChildrenSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeChildren
        fields = ['child_id','child_name', 'child_age']

class EmployeeSerializer(serializers.ModelSerializer):
    children = EmployeeChildrenSerializer(many=True, required=False)
    emp_name = serializers.CharField(validators=[validate_name])

    class Meta:
        model = Employee
        fields = ['emp_id','emp_name', 'emp_age', 'emp_gender', 'emp_email', 'children']
    
    def to_internal_value(self, data):
        if 'emp_gender' in data and isinstance(data['emp_gender'], str):
            data['emp_gender'] = data['emp_gender'].lower()
        return super().to_internal_value(data)
    
    def create(self, validated_data):
        children_data = validated_data.pop('children', [])
        employee = Employee.objects.create(**validated_data)
        
        for child_data in children_data:
            EmployeeChildren.objects.create(employee=employee, **child_data)
        return employee

    def update(self, instance, validated_data):
        children_data = validated_data.pop('children', [])
        instance.emp_name = validated_data.get('emp_name', instance.emp_name)
        instance.emp_age = validated_data.get('emp_age', instance.emp_age)
        instance.emp_gender = validated_data.get('emp_gender', instance.emp_gender)
        instance.emp_email = validated_data.get('emp_email', instance.emp_email)  
        instance.save()

        for child_data in children_data:
            child_id = child_data.get('child_id', None)
            if child_id:
                child = EmployeeChildren.objects.get(child_id=child_id, employee=instance)
                child.child_name = child_data.get('child_name', child.child_name)
                child.child_age = child_data.get('child_age', child.child_age)
                child.save()
            else:
                EmployeeChildren.objects.create(employee=instance, **child_data)
        
        return instance