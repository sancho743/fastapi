from typing import List
from typing import Optional

from fastapi import Request

from db.repository.passwords import password_exist

from db.session import get_db

from sqlalchemy.orm import Session

from fastapi import Depends


class GroupCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: Optional[List[str]] = []
        self.group_name: str = ""
        self.description: Optional[str] = ""
        self.users: Optional[List[int]] = []
        self.passwords: Optional[List[int]] = []

    async def load_data(self):
        form = await self.request.form()
        self.group_name = form.get("name")
        self.description = form.get("description")
        self.users = form.getlist("users")
        self.passwords = form.getlist("passwords")

    async def is_valid(self):
        if not self.group_name or len(self.group_name) < 2:
            self.errors.append("Имя группы должно состоять минимум из 2-х символов")
        if not self.errors:
            return True
        return False


class GroupUpdateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: Optional[List[str]] = []
        self.group_name: Optional[str] = None
        self.description: Optional[str] = None
        self.users: Optional[List[int]] = []
        self.passwords: Optional[List[int]] = []

    async def load_data(self):
        form = await self.request.form()
        self.group_name = form.get("name")
        self.description = form.get("description")
        self.users = form.getlist("users")
        self.passwords = form.getlist("passwords")

    async def is_valid(self):
        if self.group_name and len(self.group_name) < 2:
            self.errors.append("Некорректное имя группы.")
        if not self.errors:
            return True
        return False
