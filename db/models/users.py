from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from datetime import datetime

from db.base_class import Base

from db.models.users_groups import user_group
from db.models.users_passwords import user_password


class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_superuser = Column(Boolean(), default=False)
    is_blocked = Column(Boolean(), default=False)
    need_to_change_password = Column(Boolean(), default=True)
    password_update_date = Column(DateTime, default=datetime.utcnow())
    groups = relationship("Group", secondary=user_group, back_populates="users")
    available_passwords = relationship("Password", secondary=user_password, back_populates="users")
    own_passwords = relationship("Password")
    # rename_to_login_attempts
    attempts = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<User: {self.username}>"
