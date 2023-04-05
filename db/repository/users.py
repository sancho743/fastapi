from sqlalchemy.orm import Session

from core.hashing import Hasher

from datetime import datetime

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from sqlalchemy.exc import IntegrityError
from fastapi import status

from typing import List

from schemas.users import UserCreate
from schemas.users import UserUpdate

from db.models.users import User
from db.models.passwords import Password
from db.models.groups import Group

from core.password_generating import GeneratedPassword


def create_new_user(
        user: UserCreate,
        db: Session
):
    if not db.query(User).filter(User.username == user.username).first():
        user = User(
            username=user.username,
            hashed_password=Hasher().get_password_hash(user.master_password),
            is_superuser=user.is_superuser,
            is_blocked=user.is_blocked,
            need_to_change_password=user.need_to_change_password,
            password_update_date=datetime.utcnow(),
            groups=db.query(Group).filter(Group.id.in_(user.groups)).all(),
            available_passwords=db.query(Password).filter(Password.id.in_(user.available_passwords)).all()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь с именем '{user.username}' уже существует."
        )


def get_all_users(
        db: Session
):
    users = db.query(User).all()
    return users


def get_all_users_asc(
        db: Session
):
    users = db.query(User).order_by(User.username.asc()).all()
    return users


def get_nonadmin_users(
        db: Session
):
    all_users = db.query(User).all()
    nonadmin_users = [user for user in all_users if not user.is_superuser]
    return nonadmin_users


def get_nonadmin_users_asc(
        db: Session
):
    all_users = db.query(User).order_by(User.username.asc()).all()
    nonadmin_users = [user for user in all_users if not user.is_superuser]
    return nonadmin_users


def get_blocked_users(
        db: Session
):
    blocked_users = db.query(User).filter(User.is_blocked).all()
    return blocked_users


def get_blocked_users_asc(
        db: Session
):
    blocked_users = db.query(User).filter(User.is_blocked).order_by(User.username.asc()).all()
    return blocked_users


def get_user_by_username(
        username: str,
        db: Session
) -> User:
    user = db.query(User).filter(User.username == username).first()
    return user


def get_user_by_id(
        id: int,
        db: Session
):
    user = db.query(User).filter(User.id == id).first()
    return user


def update_user_by_username(
        username: str,
        db: Session
):
    user = get_user_by_username(username, db)
    if user is None:
        raise "User not found"


def update_user_by_id(
        id: int,
        user: UserUpdate,
        db: Session
):
    existing_user = db.query(User).filter(User.id == id).first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь с id={id} не найден."
        )
    try:
        if user.master_password is not None and user.master_password:
            existing_user.hashed_password = Hasher().get_password_hash(user.master_password)
        if user.is_superuser is not None:
            if existing_user.id == 1 and not user.is_superuser:
                return {"message": f"Невозможно забрать права администратора у главного администратора."}
            existing_user.is_superuser = user.is_superuser
        if user.is_blocked is not None:
            existing_user.is_blocked = user.is_blocked
        if user.need_to_change_password is not None:
            existing_user.need_to_change_password = user.need_to_change_password
        if user.groups:
            groups = [int(group) for group in user.groups]
            existing_user.groups = db.query(Group).filter(Group.id.in_(groups)).all()
        if user.groups is None:
            existing_user.groups.clear()
        if user.passwords:
            passwords = [int(password) for password in user.passwords]
            existing_user.available_passwords = db.query(Password).filter(Password.id.in_(passwords)).all()
        if user.passwords is None:
            existing_user.available_passwords.clear()
        db.add(existing_user)
        db.commit()
        return {"message": f"Информация пользователя с id={id} успешно обновлена."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка."
        )


def clear_user_passwords(
        user: User,
        db: Session
):
    user.available_passwords.clear()
    user.own_passwords.clear()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def clean_user_groups(
        user: User,
        db: Session
):
    user.groups.clear()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user_by_id(
        id: int,
        db: Session
):
    existing_user = db.query(User).filter(User.id == id).first()
    if not existing_user:
        return 1  # fix
    # existing_user.delete(synchronize_session=False)
    # db.commit()
    db.delete(existing_user)
    db.commit()
    return 0


def delete_user_by_username(username: str, db: Session):
    pass


def user_password_access(
        user_id: int,
        password_id: int,
        db: Session
):
    user = get_user_by_id(id=user_id, db=db)
    for password in user.available_passwords:
        if password.id == password_id:
            return True
    for group in user.groups:
        for password in group.passwords:
            if password.id == password_id:
                return True
    return False


def clear_attempts(
        id: int,
        db: Session
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return {"message": "user not found"}
    user.attempts = 0
    db.commit()
    db.refresh(user)
    return user


def add_attempt(
        id: int,
        db: Session
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return {"message": "user not found"}
    user.attempts += 1
    db.commit()
    db.refresh(user)
    return user


def block_user(
        id: int,
        db: Session
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return {"message": "user not found"}
    user.is_blocked = True
    user.attempts = 0
    db.commit()
    db.refresh(user)
    return user


def change_personal_password(
        id: int,
        db: Session,
        new_password: str
):
    recommendations = list()
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return {"message": "user not found",
                "recommendations": recommendations}
    new_hash = Hasher().get_password_hash(new_password)
    if new_hash == user.hashed_password:
        return {"message": "Новый пароль не может совпадать со старым.",
                "recommendations": recommendations}
    password = GeneratedPassword()
    password.set_password(new_password)
    recommendations = password.recommendations
    if recommendations:
        return {"message": "Пароль не удовлетворяет требованиям парольной политики.",
                "recommendations": recommendations}
    user.hashed_password = new_hash
    db.commit()
    db.refresh(user)
    return {"message": "Новый пароль успешно установлен.",
            "recommendations": recommendations}


def unblock_user(
        id: int,
        db: Session
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return {"message": f"Пользователь с id={id} не найден."}
    user.is_blocked = False
    db.commit()
    db.refresh(user)
    return {"message": f"Пользователь с id={id} успешно разблокирован."}
