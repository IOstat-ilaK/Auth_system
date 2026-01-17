from django.utils.deprecation import MiddlewareMixin
from .utils import JWTManager
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
import re


class JWTAuthenticationMiddleware(MiddlewareMixin):
    
    #  URL не требующиe аутентификации
    PUBLIC_URLS = [
        r'^/api/auth/register/$',
        r'^/api/auth/login/$',
        r'^/admin/',
        r'^/admin/login/',
        r'^/api/docs/',
    ]
    
    def process_request(self, request):
        
        path = request.path_info
        
        for pattern in self.PUBLIC_URLS:
            if re.match(pattern, path):
                request.user = AnonymousUser()
                return None
        
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return JsonResponse(
                {'error': 'Требуется аутентификация'}, 
                status=401)
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse(
                {'error': 'Неверный формат токена. Используйте: Bearer <token>'}, 
                status=401)
        
        token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else None
        
        if not token:
            return JsonResponse(
                {'error': 'Токен не предоставлен'}, 
                status=401)
        
        user = JWTManager.get_user_from_token(token)
        
        if not user:
            return JsonResponse(
                {'error': 'Неверный или просроченный токен'}, 
                status=401)
        
        request.user = user
        return None