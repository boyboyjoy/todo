from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def data_validation(request):
    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    try:
        validate_email(email)
    except ValidationError:
        return 'Incorrect email format'
    try:
        validate_password(password)
    except ValidationError:
        return 'Password is simple'
