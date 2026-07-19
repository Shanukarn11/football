from django.http import JsonResponse
from .utils import decode_jwt

def jwt_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            try:
                token_type, token = auth_header.split(' ')
                if token_type.lower() == 'bearer':
                    decoded = decode_jwt(token)
                    if decoded:
                        request.jwt_payload = decoded
                        return view_func(request, *args, **kwargs)
            except ValueError:
                pass
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    return _wrapped_view
