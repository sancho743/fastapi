from schemas.users import UserBase, ShowUserRestricted

from schemas.passwords import PasswordBase, ShowPasswordRestricted

from schemas.groups import GroupBase, ShowGroupRestricted

from typing import List, Optional


class ShowUser(UserBase):
    id: int
    is_superuser: bool
    passwords: Optional[List[ShowPasswordRestricted]] = []
    groups: Optional[List[ShowGroupRestricted]] = []

    class Config:
        orm_mode = True


class ShowPassword(PasswordBase):
    id: int
    service_address: str
    users: Optional[List[ShowUserRestricted]] = []
    groups: Optional[List[ShowGroupRestricted]] = []
    login: str
    value: str

    class Config:
        orm_mode = True


class ShowGroup(GroupBase):
    id: int
    users: Optional[List[ShowUserRestricted]] = []
    passwords: Optional[List[ShowPasswordRestricted]] = []

    class Config:
        orm_mode = True
