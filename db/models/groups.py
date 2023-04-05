from sqlalchemy import Column, Integer, Text, String
from sqlalchemy.orm import relationship

from db.base_class import Base

from db.models.users_groups import user_group
from db.models.groups_passwords import group_password


class Group(Base):
    id = Column(Integer, primary_key=True)
    group_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    users = relationship("User", secondary=user_group, back_populates="groups")
    passwords = relationship("Password", secondary=group_password, back_populates="groups")

    def __repr__(self):
        return f"<Group: {self.group_name}>"
