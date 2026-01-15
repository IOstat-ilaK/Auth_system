from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Role(models.Model):
    # Роли пользователей
    name = models.CharField(max_length=50,unique=True)
    description = models.TextField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


class BusinessElement(models.Model):
    # Бизнес-объект
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Бизнес-элемент'
        verbose_name_plural = 'Бизнес-элементы'

class AccessRule(models.Model):
    # Правила доступа роли к бизнес-элементу
    role = models.ForeignKey(Role,on_delete=models.CASCADE, related_name='access_rules')
    element = models.ForeignKey(BusinessElement,on_delete=models.CASCADE, related_name='access_rules')

    # Чтение
    can_read = models.BooleanField(default=False)
    can_read_all = models.BooleanField(default=False)

    # Создание
    can_create = models.BooleanField(default=False)
    
    # Изменение
    can_update = models.BooleanField(default=False)
    can_update_all = models.BooleanField(default=False)

    # Удаление

    can_delete = models.BooleanField(default=False)
    can_delete_all = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['role', 'element']
        verbose_name = "Правило доступа"
        verbose_name_plural = "Правила доступа"

    def __str__(self):
        return f"{self.role.name} -> {self.element.name}"
    
class UserProfile(models.Model):
    # Расширенная версия профиля пользователя
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def soft_delete(self):
        # МЯГккое удаление юзера
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

        # деактив
        self.user.is_active = False
        self.user.save()

    def restore(self):
        # Восстановление пользователя
        self.is_deleted = False
        self.deleted_at = None
        self.save()

        # актив
        self.user.is_active = True
        self.user.save()

    def __str__(self):
        return f"{self.user.email} ({self.role.name if self.role else 'No role'})"

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'




