from sqlalchemy import Table, Integer, Column, ForeignKey

from db.base_class import Base


group_password = Table(
    "group_password",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("group.id"), primary_key=True),
    Column("password_id", Integer, ForeignKey("password.id"), primary_key=True)
)
