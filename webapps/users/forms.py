from typing import List
from typing import Optional

from fastapi import Request

from db.repository.passwords import password_exist

from db.session import get_db

from sqlalchemy.orm import Session

from fastapi import Depends

from db.models.users import User
from schemas.shows import ShowUser


class UserCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: Optional[List[str]] = []
        self.username: str = ""
        self.master_password: str = ""
        self.is_superuser: bool = False
        self.is_blocked: bool = False
        self.need_to_change_password: bool = False
        self.passwords: Optional[List[int]] = None
        self.groups: Optional[List[int]] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.master_password = form.get("password")
        self.is_superuser = form.get("superuser")
        self.is_blocked = form.get("blocked")
        self.need_to_change_password = form.get("need_to_change_password")
        self.passwords = form.getlist("passwords")
        self.groups = form.getlist("groups")

    async def is_valid(self):
        if not self.username or not len(self.username) >= 3:
            self.errors.append("Имя пользователя должно быть длиннее 3-х символов.")
        if len(self.username) > 30:
            self.errors.append("Имя пользователя не может быть длиннее 30-ти символов.")
        if not self.master_password or not len(self.master_password) >= 8:
            self.errors.append("Пароль должен быть длиннее 8-ми символов.")
        if self.is_superuser is None:
            self.is_superuser = False
        if self.is_blocked is None:
            self.is_blocked = False
        if self.need_to_change_password is None:
            self.need_to_change_password = False
        if not self.errors:
            return True
        return False


class UserUpdateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: Optional[List[str]] = []
        self.master_password: Optional[str] = None
        self.is_superuser: Optional[bool] = None
        self.is_blocked: Optional[bool] = None
        self.need_to_change_password: Optional[bool] = None
        self.passwords: Optional[List[int]] = []
        self.groups: Optional[List[int]] = []

    async def load_data(self):
        form = await self.request.form()
        self.master_password = form.get("password")
        self.is_superuser = form.get("superuser")
        self.is_blocked = form.get("blocked")
        self.need_to_change_password = form.get("need_to_change_password")
        self.passwords = form.getlist("passwords")
        self.groups = form.getlist("groups")

    async def is_valid(self):
        if self.master_password and not len(self.master_password) >= 8:
            self.errors.append("Пароль должен быть длиннее 8-ми символов.")
        # if self.is_blocked is None:
        #     self.is_blocked = False
        # if self.need_to_change_password is None:
        #     self.need_to_change_password = False
        # if self.is_superuser - ? add or not?
        if not self.errors:
            return True
        return False
