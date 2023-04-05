from typing import List
from typing import Optional

from fastapi import Request


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: str = ""
        self.password: str = ""

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")

    async def is_valid(self):
        if not self.username:
            self.errors.append("Некорректный имя пользователя или пароль.")
        if not self.password:
            self.errors.append("Некорректный имя пользователя или пароль.")
        if not self.errors:
            return True
        return False
