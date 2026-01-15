from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from auth_app.models import Role, BusinessElement, AccessRule, UserProfile
from django.utils import timezone


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('Создание тестовых данных...')

        # 1. Создание ролей
        roles_data = [
            {'name': 'admin', 'description': 'Полный доступ ко всему'},
            {'name': 'manager', 'description': 'Доступ к управлению контентом'},
            {'name': 'user', 'description': 'Обычный пользователь'},
            {'name': 'guest', 'description': 'Гость (только чтение)'},
        ]
        
        roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            roles[role.name] = role
            self.stdout.write(f'Роль {role.name} создана')

        # 2. Создание бизнес-элементов
        elements_data = [
            {'name': 'users', 'description': 'Пользователи системы'},
            {'name': 'products', 'description': 'Товары/услуги'},
            {'name': 'orders', 'description': 'Заказы'},
            {'name': 'access_rules', 'description': 'Правила доступа'},
        ]
        
        elements = {}
        for element_data in elements_data:
            element, created = BusinessElement.objects.get_or_create(
                name=element_data['name'],
                defaults={'description': element_data['description']}
            )
            elements[element.name] = element
            self.stdout.write(f'Элемент {element.name} создан')

        # 3. Создание правил доступа для админа
        admin_role = roles['admin']
        for element in elements.values():
            AccessRule.objects.get_or_create(
                role=admin_role,
                element=element,
                defaults={
                    'can_read': True,
                    'can_read_all': True,
                    'can_create': True,
                    'can_update': True,
                    'can_update_all': True,
                    'can_delete': True,
                    'can_delete_all': True,
                }
            )
        self.stdout.write('Правила доступа для админа созданы')

        # 4. Создание правила для пользователя (user)
        user_role = roles['user']
        AccessRule.objects.get_or_create(
            role=user_role,
            element=elements['products'],
            defaults={
                'can_read': True,
                'can_read_all': True,
                'can_create': False,
                'can_update': False,
                'can_update_all': False,
                'can_delete': False,
                'can_delete_all': False,
            }
        )
        self.stdout.write('Правила доступа для пользователя созданы')

        # 5. Создание тестовых пользователей
        # Администратор
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'first_name': 'Иван',
                'last_name': 'Админов',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'middle_name': 'Админович',
                    'role': admin_role,
                }
            )
            self.stdout.write('Администратор создан: admin@example.com / admin123')

        # Обычный пользователь
        regular_user, created = User.objects.get_or_create(
            email='user@example.com',
            defaults={
                'username': 'user',
                'first_name': 'Петр',
                'last_name': 'Пользователев',
                'is_active': True,
            }
        )
        if created:
            regular_user.set_password('user123')
            regular_user.save()
            UserProfile.objects.get_or_create(
                user=regular_user,
                defaults={
                    'middle_name': 'Петрович',
                    'role': user_role,
                }
            )
            self.stdout.write('Пользователь создан: user@example.com / user123')

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))