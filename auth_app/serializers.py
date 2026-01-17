from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Role, BusinessElement, AccessRule
from django.contrib.auth.password_validation import validate_password
import bcrypt

class UserSerializer(serializers.ModelSerializer):
    # Сериализатор для модели Юзера
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only = True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email','first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'email':{'required':True},
            'first_name':{'required':True},
            'last_name':{'required':True},
        }

    def validate(self,attrs):
        # проверка паролей

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password":"Пароли не совпадают"})
        return attrs
    
    def create(self,validated_data):
        # создание пользователя с хэшированием пароля
        validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        # хэширование пароля с помощью bcrypt
        password = validated_data['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password,bcrypt.gensalt())

        # сохр хэш пароля 
        user.set_password(hashed_password.decode('utf-8'))
        user.save()

        return user
    

class UserProfileSerializer(serializers.ModelSerializer):
    # Сериализатор для профился пользователя
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),
        source='user',
        write_only=True
    )
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'user','user_id','middle_name','role','role_name','is_deleted','deleted_at','created_at')


class RoleSerializer(serializers.ModelSerializer):
    # сериализатор для ролей
    class Meta:
        model = Role
        fields = ('id','name','description','created_at')
        read_only_fields = ('created_at',)

class BusinessElementSerializer(serializers.ModelSerializer):
    # сериализатор для бизнес-проектов
    class Meta:
        model = BusinessElement
        fields = ('id', 'name', 'description', 'created_at')
        read_only_fields = ('created_at',)


class AccessRuleSerializer(serializers.ModelSerializer):
    # сериализатор для правил доступа
    role_name = serializers.CharField(source='role.name', read_only=True)
    element_name = serializers.CharField(source='element.name', read_only=True)

    class Meta:
        model=AccessRule
        fields = ('id', 'role', 'role_name', 'element', 'element_name',
                  'can_read', 'can_read_all', 'can_create', 
                  'can_update', 'can_update_all', 'can_delete', 'can_delete_all',
                  'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class LoginSerializer(serializers.ModelSerializer):
    # сериализатор для того чтоб залогиниться
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email=attrs.get('email')
        password=attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Неверный email или пароль')
        
        # проверка пароля с помоьщю bcrypt
        password_bytes = password.encode('utf-8')
        stored_password = user.password.encode('utf-8') if isinstance(user.password,str) else user.password

        if not bcrypt.checkpw(password_bytes,stored_password):
            raise serializers.ValidationError('Неверный email или пароль')
        
        if not user.is_active:
            raise serializers.ValidationError(('Ваш аккаунт был деактивирован'))

        attrs['user'] = user
        return attrs


    
class UpdateProfileSerializer(serializers.ModelSerializer):
    # сериализатор для обновления профиля
    email = serializers.EmailField(source='user.email',required=False)
    first_name = serializers.CharField(source='user.first_name',required=False)
    last_name = serializers.CharField(source='user.last_name',required=False)

    class Meta:
        model = UserProfile
        fields=('middle_name', 'email', 'first_name', 'last_name')

    def update(self,instance,validated_data):
        # обновление данных юзера
        user_data = validated_data.pop('user',{})
        user=instance.user


        if 'email' in user_data:
            user.email = user_data['email']
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']

        user.save()

        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.save()

        return instance
            


