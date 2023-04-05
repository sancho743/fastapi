from pydantic import BaseModel
from typing import List, Optional


class GroupBase(BaseModel):
    group_name: str


class GroupCreate(GroupBase):
    description: Optional[str]
    users: Optional[List[int]] = []
    passwords: Optional[List[int]] = []


class GroupUpdate(BaseModel):
    group_name: Optional[str] = None
    description: Optional[str]
    users: Optional[List[int]] = None
    passwords: Optional[List[int]] = None


class ShowGroupRestricted(GroupBase):
    id: int

    class Config:
        orm_mode = True
