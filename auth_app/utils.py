import jwt
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import bcrypt
from decouple import config
from django.conf import settings


 
class JWTManager:
    # Менеджер для работы с JWT ТОКЕНАМИ

    SECRET_KEY = config('SECRET_KEY')
    ALGORITHM = 'HS256'

    @staticmethod
    def create_token(user, expires_delta_hours=24):
            # создание токена
            payload = {
                  'user_id':user.id,
                  'email':user.email,
                  'exp':datetime.utcnow()+timedelta(hours=expires_delta_hours),
                  'iat':datetime.utcnow()  
            }

            token = jwt.encode(payload, JWTManager.SECRET_KEY,algorithm=JWTManager.ALGORITHM)
            return token
    
    @staticmethod
    def decode_token(token):
        # декодинг токена

        try:
            payload = jwt.decode(token,JWTManager.SECRET_KEY, algorithms=[JWTManager.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
             raise ValueError('Токен истёк')
        except jwt.InvalidTokenError:
             raise ValueError('Неверный токен')
        
    @staticmethod
    def get_user_from_token(token):
        #  получение пользователя по токену
        try:
             payload = JWTManager.decode_token(token)
             user_id = payload.get('user_id')
             user = User.objects.get(id=user_id,is_active=True)
             return user
        except (ValueError, User.DoesNotExist):
             return None
        

class PasswordHasher:
    #  класс для раблоты с паролями:
    @staticmethod
    def hash_password(password):
        #  хэширование пароля
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes,salt)
        return hashed.decode('utf-8')


    @staticmethod
    def check_password(password, hashed_password):
        #  Проверка пароля
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes,hashed_bytes)