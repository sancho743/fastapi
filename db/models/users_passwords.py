from sqlalchemy import Table, Column, ForeignKey, Integer

from db.base_class import Base


user_password = Table(
    "user_password",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("password_id", Integer, ForeignKey("password.id"), primary_key=True),
)
