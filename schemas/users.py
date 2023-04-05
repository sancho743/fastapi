from pydantic import BaseModel
from typing import Optional, List, Union


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    master_password: str
    is_superuser: bool = False
    is_blocked: bool = False
    need_to_change_password: bool = False
    available_passwords: Optional[List[int]] = []
    groups: Optional[List[int]] = []


class UserUpdate(BaseModel):
    is_superuser: Optional[Union[bool, None]] = None
    is_blocked: Optional[Union[bool, None]] = None
    need_to_change_password: Optional[Union[bool, None]] = None
    master_password: Optional[str] = None
    passwords: Optional[List[int]] = None
    groups: Optional[List[int]] = None


class ShowUserRestricted(UserBase):
    id: int

    class Config:
        orm_mode = True
