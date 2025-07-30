from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from recipe.decorators import validate_keys
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from recipe.models import CustomUser
from django.contrib.auth.hashers import make_password


# it is used to create the user and user can be creator or viewer
@api_view(['POST'])
@validate_keys(['name','email','password','role'])
def create_user(request):
    data = request.data

    email = data['email']

    try:
        validate_email(email)
    except DjangoValidationError:
        raise ValidationError({'message': 'Invalid email format.'})
    
    check = CustomUser.objects.filter(email=email).first()
    if check:
        return Response({'status': 'error', 'message': f'{email} is already registered.'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    name = data['name']
    password = data['password']
    role = data['role']
    
    if role not in ['creator', 'viewer']:
        return Response({'status': 'error', 'message': f'{role} field is invalid, options are creator or viewer.'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    CustomUser.objects.create(name=name, email=email, password=make_password(password), role=role)

    return Response({'message': 'success', 'message': 'Registration successful.'}, status=status.HTTP_201_CREATED)

