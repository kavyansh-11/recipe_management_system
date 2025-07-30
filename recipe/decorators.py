from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def validate_keys(required_keys):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            for key in required_keys:
                if key not in request.data:
                    return Response({'message': f'{key} is missing'}, status=status.HTTP_400_BAD_REQUEST)
                if request.data.get(key) in [None, '', (), {}, []]:
                    return Response({'message': f'{key} value is missing'}, status=status.HTTP_400_BAD_REQUEST)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator