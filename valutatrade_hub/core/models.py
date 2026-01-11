import hashlib
import uuid
from datetime import datetime

class User:
    '''
    user_id: int — уникальный идентификатор пользователя.
    username: str — имя пользователя.
    hashed_password: str — пароль в зашифрованном виде.
    salt: str — уникальная соль для пользователя.
    registration_date: datetime — дата регистрации пользователя.
    '''
    
    def __init__(
        self,
        user_id: int,
        username: str,
        password: str,
        hashed_password: str,
        salt: str,
        registration_date: datetime
    ):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date


    @property
    def user_id(self) -> int:
        return self._user_id
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def hashed_password(self) -> str:
        return self._hashed_password
    
    @property
    def salt(self) -> str:
        return self._salt
    
    @property
    def registration_date(self) -> datetime:
        return self._registration_date
    
    @username.setter
    def username(self, value: str):
        if not value or not value.strip():
            raise ValueError("Имя не может быть пустым")
        self._username = value.strip()
    
    def get_user_info(self):
        """
        Выводит информацию о пользователе (без пароля)
        """
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }
    
    def change_password(self, new_password: str):
        """
        Изменяет пароль пользователя, с хешированием нового пароля
        """
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        hash_object = hashlib.sha256()
        salted_password = new_password + self._salt
        hash_object.update(salted_password.encode('utf-8'))
        self._hashed_password = hash_object.hexdigest()
    
    def verify_password(self, password: str):
        """
        Проверяет введённый пароль на совпадение
        """
        hash_object = hashlib.sha256()
        salted_password = password + self._salt
        hash_object.update(salted_password.encode('utf-8'))
        return hash_object.hexdigest() == self._hashed_password
