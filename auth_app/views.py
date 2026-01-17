from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import UserProfile, Role, BusinessElement, AccessRule
from .serializers import UserSerializer, UserProfileSerializer, LoginSerializer, UpdateProfileSerializer, RoleSerializer, BusinessElementSerializer, AccessRuleSerializer
from .utils import JWTManager, PasswordHasher
from django.utils import timezone


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            
            default_role = Role.objects.get(name='user')  
            UserProfile.objects.create(
                user=user,
                middle_name=request.data.get('middle_name', ''),
                role=default_role
            )
            
           
            token = JWTManager.create_token(user)
            
            return Response({
                'message': 'Регистрация успешна',
                'user': UserSerializer(user).data,
                'token': token
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    # логин
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            token = JWTManager.create_token(user)
            
            user.last_login = timezone.now()
            user.save()
            
            return Response({
                'message': 'Вход выполнен успешно',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'token': token,
                'role': user.profile.role.name if hasattr(user, 'profile') and user.profile.role else None
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    
    def post(self, request):
        return Response({
            'message': 'Выход выполнен успешно. Удалите токен на клиенте.'
        }, status=status.HTTP_200_OK)



class ProfileView(APIView):
    
    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Профиль не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def put(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Профиль не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UpdateProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Профиль обновлен',
                'profile': UserProfileSerializer(profile).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    
    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Профиль не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        profile.soft_delete()
        
        return Response({
            'message': 'Аккаунт успешно удален (мягкое удаление)'
        }, status=status.HTTP_200_OK)



class IsAdminPermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if hasattr(request.user, 'profile') and request.user.profile.role:
            return request.user.profile.role.name == 'admin'
        return False


class RoleListView(generics.ListCreateAPIView):
    """Список и создание ролей (только для админов)"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminPermission]


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали, обновление и удаление роли (только для админов)"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminPermission]


class BusinessElementListView(generics.ListCreateAPIView):
    """Список и создание бизнес-элементов (только для админов)"""
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAdminPermission]


class BusinessElementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали, обновление и удаление бизнес-элемента (только для админов)"""
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAdminPermission]


class AccessRuleListView(generics.ListCreateAPIView):
    """Список и создание правил доступа (только для админов)"""
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAdminPermission]


class AccessRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали, обновление и удаление правила доступа (только для админов)"""
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAdminPermission]


class MockUsersView(APIView):
    """Mock API для тестирования доступа к ресурсу 'users'"""
    
    def get(self, request):
        return Response({
            'message': 'Доступ к ресурсу "Пользователи" разрешен',
            'data': [
                {'id': 1, 'name': 'Иван Иванов', 'email': 'ivan@example.com'},
                {'id': 2, 'name': 'Петр Петров', 'email': 'petr@example.com'},
            ]
        })


class MockProductsView(APIView):
    """Mock API для тестирования доступа к ресурсу 'products'"""
    
    def get(self, request):
        return Response({
            'message': 'Доступ к ресурсу "Товары" разрешен',
            'data': [
                {'id': 1, 'name': 'Ноутбук', 'price': 50000},
                {'id': 2, 'name': 'Смартфон', 'price': 30000},
            ]
        })

class MockOrdersView(APIView):
    """Mock API для тестирования доступа к ресурсу 'orders'"""
    
    def get(self, request):
        return Response({
            'message': 'Доступ к ресурсу "Заказы" разрешен',
            'data': [
                {'id': 1, 'order_number': 'ORD-001', 'total': 80000},
                {'id': 2, 'order_number': 'ORD-002', 'total': 30000},
            ]
        })