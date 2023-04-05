from sqlalchemy.orm import Session

from typing import List

from db.models.passwords import Password
from db.models.users import User
from db.models.groups import Group

from schemas.groups import GroupCreate
from schemas.groups import GroupUpdate

from fastapi import HTTPException

from fastapi import status


def create_new_group(
        group: GroupCreate,
        db: Session
):
    if not db.query(Group).filter(Group.group_name == group.group_name).first():
        group = Group(
            group_name=group.group_name,
            description=group.description,
            users=db.query(User).filter(User.id.in_(group.users)).all(),
            passwords=db.query(Password).filter(Password.id.in_(group.passwords)).all()
        )
        db.add(group)
        db.commit()
        db.refresh(group)
        return group
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Группа с именем '{group.group_name}' уже существует."
        )


def get_all_groups(
        db: Session
):
    groups = db.query(Group).all()
    return groups


def get_all_groups_asc(db: Session):
    groups = db.query(Group).order_by(Group.group_name).all()
    return groups


def get_group_by_group_name(
        group_name: str,
        db: Session
):
    group = db.query(Group).filter(Group.group_name == group_name).first()
    return group


def get_group_by_id(
        id: int,
        db: Session
):
    group = db.query(Group).filter(Group.id == id).first()
    return group


def clear_group_users(
        group: Group,
        db: Session
):
    group.users.clear()
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def clear_group_passwords(
        group: Group,
        db: Session
):
    group.passwords.clear()
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def delete_group_by_id(
        id: int,
        db: Session
):
    existing_group = db.query(Group).filter(Group.id == id).first()
    if not existing_group:
        return 1
    db.delete(existing_group)
    db.commit()
    return 0


def update_group_by_id(
        id: int,
        group: GroupUpdate,
        db: Session
):
    existing_group = db.query(Group).filter(Group.id == id).first()
    if not existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Группа с id={id} не найден."
        )
    try:
        if group.description is None:
            existing_group.description = ""
        else:
            existing_group.description = group.description
        if group.users is None:
            existing_group.users.clear()
        else:
            existing_group.users = db.query(User).filter(User.id.in_(group.users)).all()
        if group.passwords is None:
            existing_group.passwords.clear()
        else:
            existing_group.passwords = db.query(Password).filter(Password.id.in_(group.passwords)).all()
        if group.group_name is not None:
            existing_group.group_name = group.group_name
        db.add(existing_group)
        db.commit()
        return {"message": f"Информация группы с id={id} успешно обновлена."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка."
        )
