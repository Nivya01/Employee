from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Employee, EmployeeChildren
from .serializers import EmployeeSerializer, EmployeeChildrenSerializer
from rest_framework.exceptions import ValidationError
from django.db.models import Max, Min

@api_view(['POST'])
def create_or_update_employee(request):
    data = request.data
    emp_id = data.get('emp_id', None)

    if emp_id:
        try:
            employee = Employee.objects.get(emp_id=emp_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        if 'emp_name' in data:
            employee.emp_name = data['emp_name']
        if 'emp_age' in data:
            employee.emp_age = data['emp_age']
        if 'emp_gender' in data:
            employee.emp_gender = data['emp_gender']
        if 'emp_email' in data:
            emp_email = data['emp_email'].lower()
            if emp_email != employee.emp_email:  
                existing_email = Employee.objects.exclude(emp_id=emp_id).filter(emp_email=emp_email).first()
                if existing_email:
                    return Response({'error': "Email iD is already exist and The Email ID must be an unique."}, status=status.HTTP_400_BAD_REQUEST)
            employee.emp_email = emp_email
        employee.save()
    else:
        employee_serializer = EmployeeSerializer(data=data)
        if employee_serializer.is_valid():
            employee = employee_serializer.save()
        else:
            return Response(employee_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if 'children' in data:
        for child_data in data['children']:
            child_id = child_data.get('child_id', None)
            if child_id:
                try:
                    child = EmployeeChildren.objects.get(child_id=child_id, employee=employee)
                except EmployeeChildren.DoesNotExist:
                    return Response({'error': 'Child with this ID is not found for this employee'}, status=status.HTTP_404_NOT_FOUND)

                if 'child_name' in child_data:
                    child.child_name = child_data['child_name']
                    
                if 'child_age' in child_data:
                    child.child_age = child_data['child_age']
                child.save()  
            else:
                existing_child = EmployeeChildren.objects.filter(employee=employee, child_name=child_data['child_name'], child_age=child_data['child_age']).first()
                if not existing_child:
                    child_serializer = EmployeeChildrenSerializer(data=child_data)
                    if child_serializer.is_valid():
                        child_serializer.save(employee=employee)
                    else:
                        return Response(child_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
                    
    employee_serializer = EmployeeSerializer(employee)
    return Response(employee_serializer.data)

VALID_SORT_FIELDS = ['emp_name', 'emp_age', 'children__child_name', 'children__child_age']
VALID_FILTER_FIELDS = ['children_age', 'children_count', 'emp_name', 'children_name', 'emp_email', 'emp_gender']
VALID_CONDITIONS = ['eq', 'startswith', 'contains', 'lt', 'gte', 'gt'] 
VALID_SORT_ORDERS = ['asc', 'desc']

def validate_sorting_and_filters(filters):
    sort_by = filters.get('sort_by', {})
    filter_fields = {key: value for key, value in filters.items() if key != 'sort_by'}

    for key, conditions in filter_fields.items():
        if key not in VALID_FILTER_FIELDS:
            raise ValidationError(f"Invalid filter field: '{key}'. Valid fields are {VALID_FILTER_FIELDS}.")
        
        if isinstance(conditions, dict):
            for condition, value in conditions.items():
                if key in ['emp_name', 'emp_email', 'children_name'] and condition in ['gte', 'gt', 'lt']:
                    raise ValidationError(f"Invalid condition: '{condition}' for filter field '{key}'. Conditions 'startswith', 'contains', and 'eq' are only allowed for this field.")
                if key in ['children_age', 'children_count'] and condition in ['startswith', 'contains']:
                    raise ValidationError(f"Invalid condition: '{condition}' for filter field '{key}'. Conditions 'gte', 'lt', 'gt' and 'eq' are only allowed for this field.")
                if condition not in VALID_CONDITIONS:
                    raise ValidationError(f"Invalid condition: '{condition}' for filter field '{key}'. Valid conditions are {VALID_CONDITIONS}.")
                if key == "emp_gender" and value not in ["male", "female"]:
                    raise ValidationError("Invalid value for 'emp_gender'. Allowed values are 'male' and 'female'.")
            
        elif isinstance(conditions, str):
            if key == "emp_gender" and conditions not in ["male", "female"]:
                raise ValidationError("Invalid value for 'emp_gender'. Allowed values are 'male' and 'female'.")
        else:
            raise ValidationError(f"Invalid filter value for '{key}'. Must be a string or dictionary.")

    if sort_by:
        for field, order in sort_by.items():
            if field not in VALID_SORT_FIELDS:
                raise ValidationError(f"Invalid sort field: '{field}'. Valid fields are {VALID_SORT_FIELDS}.")
            if order not in VALID_SORT_ORDERS:
                raise ValidationError(f"Invalid sort order: '{order}'. Valid orders are {VALID_SORT_ORDERS}.")

@api_view(['POST'])
def filter_employees(request):
    data = request.data
    sort_by = data.get('sort_by', {})
    filters = data.get('filters', {})

    try:
        validate_sorting_and_filters({'sort_by': sort_by, **filters})
    except ValidationError as e:
        return Response({"error": str(e)}, status=400)

    filter_map = {
        "children_age": {
            "eq": "children__child_age",
            "gte": "children__child_age__gte",
            "lt": "children__child_age__lt",
            "gt": "children__child_age__gt",
        },
        "children_count": {
            "eq": "child_count",
            "gte": "child_count__gte",
            "lt": "child_count__lt",
            "gt": "child_count__gt",
        },
        "emp_name": {
            "startswith": "emp_name__istartswith",
            "eq": "emp_name__exact",
            "contains": "emp_name__icontains",
        },
        "emp_email": {
            "startswith": "emp_email__istartswith",
            "contains": "emp_email__icontains",
            "eq": "emp_email__exact",
        },
        "children_name": {
            "startswith": "children__child_name__istartswith",
            "eq": "children__child_name__exact",
            "contains": "children__child_name__icontains",
        },
    }

    employees = Employee.objects.annotate(
        child_count=Count('children', distinct=True),
        max_child_age=Max('children__child_age'),
        min_child_age=Min('children__child_age'),
    )

    for key, conditions in filters.items():
        if key in filter_map:
            for condition, value in conditions.items():
                field = filter_map[key].get(condition)
                if field:
                    employees = employees.filter(**{field: value})
        elif key == "emp_gender":
            employees = employees.filter(emp_gender=conditions)

    if sort_by:
        sorting = []
        for field, direction in sort_by.items():
            if field not in VALID_SORT_FIELDS:
                return Response(
                    {"error": f"Invalid sort field: '{field}'. Valid fields are {VALID_SORT_FIELDS}."}, status=400)
            if direction.lower() not in VALID_SORT_ORDERS:
                return Response(
                    {"error": f"Invalid sort order: '{direction}'. Valid orders are {VALID_SORT_ORDERS}."}, status=400)

            if field == "children__child_age":
                sorting.append(f"-max_child_age" if direction.lower() == "desc" else "max_child_age")
            else:
                sorting.append(f"-{field}" if direction.lower() == "desc" else field)

        employees = employees.order_by(*sorting)

    employees = employees.distinct()

    employee_serializer = EmployeeSerializer(employees, many=True)
    return Response(employee_serializer.data)
