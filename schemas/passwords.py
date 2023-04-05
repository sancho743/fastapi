from pydantic import BaseModel
from typing import List, Optional


class PasswordBase(BaseModel):
    service_name: str


class PasswordCreate(PasswordBase):
    service_address: str
    password_type: int
    users: Optional[List[int]] = []
    groups: Optional[List[int]] = []
    description: Optional[str]
    login: str
    value: str


class PasswordUpdate(BaseModel):
    service_name: Optional[str] = None
    service_address: Optional[str] = None
    users: Optional[List[int]] = None
    groups: Optional[List[int]] = None
    description: Optional[str] = None
    login: Optional[str] = None
    value: Optional[str] = None


class ShowPasswordRestricted(PasswordBase):
    id: int

    class Config:  # to convert non dict obj to json
        orm_mode = True
