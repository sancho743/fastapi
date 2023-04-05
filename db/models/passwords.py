from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, LargeBinary, String
from sqlalchemy.orm import relationship
from datetime import datetime

from db.base_class import Base

from db.models.users_passwords import user_password
from db.models.groups_passwords import group_password


class Password(Base):
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    password_type = Column(Integer, nullable=False)
    service_name = Column(String(100), nullable=False)
    service_address = Column(String(100), nullable=False)
    description = Column(Text)
    date_created = Column(DateTime, default=datetime.utcnow())
    users = relationship("User", secondary=user_password, back_populates="available_passwords")
    groups = relationship("Group", secondary=group_password, back_populates="passwords")
    login = Column(String(100), nullable=False)
    value = Column(LargeBinary, nullable=False)

    def __repr__(self):
        return f"<Password: {self.service_name}>"
