from typing import List
from typing import Optional

from fastapi import Request

from db.repository.passwords import password_exist

from db.session import get_db

from sqlalchemy.orm import Session

from fastapi import Depends


class PasswordCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: Optional[List[str]] = []
        self.service_name: str = ""
        self.service_address: str = ""
        self.password_type: int = 0
        self.description: Optional[str] = ""
        self.users: Optional[List[int]] = []
        self.groups: Optional[List[int]] = []
        self.login: str = ""
        self.value: str = ""

    async def load_data(self):
        form = await self.request.form()
        self.service_name = form.get("name")
        self.service_address = form.get("address")
        self.password_type = form.get("password_type")
        self.users = form.getlist("users")
        self.groups = form.getlist("groups")
        self.login = form.get("login")
        self.value = form.get("password")

    async def is_valid(self):
        if not self.service_name or len(self.service_name) < 2:
            self.errors.append("Длина имени сервиса должна состоять как минимум из 2-х символов.")
        if not self.service_address or len(self.service_address) < 2:
            self.errors.append("Длина адреса сервиса должна состоять как минимум из 2-х символов.")
        if not self.login:
            self.errors.append("Логин не может быть пустым.")
        #  place for check password for security
        if not self.value:
            self.errors.append("Пароль не может быть пустым.")
        if not self.errors:
            return True
        return False


class PasswordGenerateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: Optional[List[str]] = []
        self.length: int = 12
        self.lowercase: bool = False
        self.uppercase: bool = False
        self.digits: bool = False
        self.math: bool = False
        self.underscore: bool = False
        self.punctuation: bool = False
        self.brackets: bool = False
        self.other_special: bool = False

    async def load_data(self):
        form = await self.request.form()
        self.length = form.get("length")
        self.uppercase = form.get("lowercase")
        self.lowercase = form.get("uppercase")
        self.digits = form.get("digits")
        self.math = form.get("math")
        self.underscore = form.get("underscore")
        self.punctuation = form.get("punctuation")
        self.brackets = form.get("brackets")
        self.other_special = form.get("other_special")

    async def is_valid(self):
        try:
            float(self.length)
        except ValueError:
            self.errors.append("Ошибка: некорректное значение длины пароля.")
        if self.errors:
            return False
        return True


class PasswordUpdateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: Optional[List[str]] = []
        self.service_name: Optional[str] = None
        self.service_address: Optional[str] = None
        self.description: Optional[str] = ""
        self.users: Optional[List[int]] = []
        self.groups: Optional[List[int]] = []
        self.login: Optional[str] = None
        self.value: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.service_name = form.get("service_name")
        self.service_address = form.get("service_address")
        self.description = form.get("description")
        self.users = form.getlist("users")
        self.groups = form.getlist("groups")
        self.login = form.get("login")
        self.value = form.get("password")

    async def is_valid(self):
        if self.service_name and len(self.service_name) < 2:
            self.errors.append("Длина имени сервиса должна состоять как минимум из 2-х символов.")
        if self.service_address and len(self.service_address) < 2:
            self.errors.append("Длина адреса сервиса должна состоять как минимум из 2-х символов.")
        #  place for check password for security
        if self.value and len(self.value) < 3:
            self.errors.append("Пароль должен быть длиннее 3-х символов.")
        if not self.errors:
            return True
        return False


class PasswordChangeForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: Optional[List[str]] = []
        self.current_password: str = ""
        self.new_password: str = ""
        self.repeat_new_password: str = ""

    async def load_data(self):
        form = await self.request.form()
        self.current_password = form.get("current_password")
        self.new_password = form.get("new_password")
        self.repeat_new_password = form.get("repeat_new_password")

    async def is_valid(self):
        if not self.current_password:
            self.errors.append("Текущий пароль не может быть пустым.")
        if not self.new_password:
            self.errors.append("Новый пароль не может быть пустым.")
        elif not self.repeat_new_password:
            self.errors.append("Введите новый пароль 2 раза.")
        if self.new_password != self.repeat_new_password:
            self.errors.append("Новые пароли не совпадают.")
        if self.errors:
            return False
        return True


class PasswordReencryptForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: Optional[List[str]] = []
        self.password: str = ""
        self.confirm: bool = False

    async def load_data(self):
        form = await self.request.form()
        self.password = form.get("password")
        self.confirm = form.get("confirm")

    async def is_valid(self):
        if not self.confirm:
            self.errors.append("Необходимо подтвердить перешифрование паролей.")
        if not self.errors:
            return True
        return False
