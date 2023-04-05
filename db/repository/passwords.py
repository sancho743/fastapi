from sqlalchemy.orm import Session

from datetime import datetime

from typing import List

from fastapi import HTTPException
from fastapi import status

from db.models.passwords import Password
from db.models.users import User
from db.models.groups import Group

from core.encrypting import cipher
from core.encrypting import AESCipher

from core.config import settings
from core.config import Settings

from schemas.passwords import PasswordCreate, PasswordUpdate


def create_new_password(
        password: PasswordCreate,
        db: Session,
        current_user_id: int
):
    password = Password(
        owner_id=current_user_id,
        password_type=password.password_type,
        service_name=password.service_name,
        service_address=password.service_address,
        description=password.description,
        date_created=datetime.utcnow(),
        users=db.query(User).filter(User.id.in_(password.users)).all(),
        groups=db.query(Group).filter(Group.id.in_(password.groups)).all(),
        login=password.login,
        value=cipher.encrypt(password.value)
    )
    db.add(password)
    db.commit()
    db.refresh(password)
    return password


def create_new_personal_password(
        password: PasswordCreate,
        db: Session,
        current_user: User
):
    my_cipher = AESCipher(key=current_user.hashed_password)
    password = Password(
        owner_id=current_user.id,
        password_type=password.password_type,
        service_name=password.service_name,
        service_address=password.service_address,
        description=password.description,
        date_created=datetime.datetime.utcnow(),
        users=db.query(User).filter(User.id.in_(password.users)).all(),
        groups=db.query(Group).filter(Group.id.in_(password.groups)).all(),
        login=password.login,
        value=my_cipher.encrypt(password.value)
    )
    db.add(password)
    db.commit()
    db.refresh(password)
    return password


def get_all_passwords(
        db: Session
):
    passwords = db.query(Password).filter(Password.password_type == 1).all()
    for password in passwords:
        password.value = cipher.decrypt(password.value)
    return passwords


def get_all_passwords_by_user_id(
        user: User,
        db: Session
):
    passwords = db.query(Password).filter(Password.owner_id == user.id).all()
    my_cipher = AESCipher(key=user.hashed_password)
    for password in passwords:
        password.value = my_cipher.decrypt(password.value)
    return passwords


def get_all_passwords_asc(
        db: Session,
) -> List[Password]:
    passwords = db.query(Password).filter(Password.password_type == 1).order_by(Password.service_name).all()
    for password in passwords:
        password.value = cipher.decrypt(password.value)
    return passwords


# def get_passwords_by_service_name(
#         username: str,
#         db: Session
# ) -> List[Password]:
#     passwords = db.query(Password).filter(Password.username == username).all()
#     for password in passwords:
#         password.value = cipher.decrypt(password.value)
#     return passwords


def get_password_by_id(
        id: int,
        db: Session,
        user: User = None
):
    password = db.query(Password).filter(Password.id == id).first()
    if not password:
        return None
    if password.password_type == 1:
        password.value = cipher.decrypt(password.value)
    elif password.password_type == 2:
        my_cipher = AESCipher(key=user.hashed_password)
        password.value = my_cipher.decrypt(password.value)
    return password


def password_exist(
        id: int,
        db: Session
):
    if not db.query(Password).filter(Password.id == id).first():
        return False
    return True


def get_passwords_by_group(
        id: int,
        db: Session
) -> List[Password]:
    pass


def get_passwords_by_user(
        id: int,
        db: Session
) -> List[Password]:
    pass


# def get_passwords_by_service(
#         service_name: str,
#         db: Session
# ):
#     passwords = db.query(Password).filter(Password.service_name == service_name).all()
#     if not passwords:
#         return {"msg": f"there is no data by service_name {service_name}"}
#     for password in passwords:
#         password.value = cipher.decrypt(password.value)
#     return passwords


def delete_password_by_id(
        id: int,
        db: Session
):
    existing_password = db.query(Password).filter(Password.id == id).first()
    if not existing_password:
        return 1
    db.delete(existing_password)
    db.commit()
    return 0


def update_password_by_id(
        id: int,
        password: PasswordUpdate,
        db: Session
):
    existing_password = db.query(Password).filter(Password.id == id).first()
    if not existing_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пароль с id={id} не найден."
        )
    try:
        if password.service_name is not None and len(password.service_name) > 3:
            existing_password.service_name = password.service_name
        if password.service_address is not None and len(password.service_address) > 3:
            existing_password.service_address = password.service_address
        if password.users is not None:
            existing_password.users = db.query(User).filter(User.id.in_(password.users)).all()
        else:
            existing_password.users.clear()
        if password.groups is not None:
            existing_password.groups = db.query(Group).filter(Group.id.in_(password.groups)).all()
        else:
            existing_password.groups.clear()
        if password.login is not None:
            existing_password.login = password.login
        if password.value is not None:
            existing_password.value = cipher.encrypt(password.value)
            existing_password.date_created = datetime.utcnow()
        if password.description:
            existing_password.description = password.description
        else:
            existing_password.description = ""
        db.add(existing_password)
        db.commit()
        return {"message": f"Информация пароля с id={id} успешно обновлена."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Какая-то ошибка"
        )


def get_expired_passwords(
        db: Session
):
    passwords = db.query(Password).filter(Password.password_type == 1).all()
    sort_passwords = [password for password in passwords if
                      (datetime.utcnow() - password.date_created).days > 180]
    for password in sort_passwords:
        password.value = cipher.decrypt(password.value)
    return sort_passwords


def reencryption_group_passwords(
        db: Session
):
    if Settings.AES_SECRET_KEY == Settings.AES_NEW_SECRET_KEY:
        return {"message": "Убедитесь, что новый ключ шифрования не идентичен текущему."}
    passwords = db.query(Password).filter(Password.password_type == 1).all()
    new_cipher = AESCipher(key=settings.AES_NEW_SECRET_KEY)
    try:
        for password in passwords:
            plain_password = cipher.decrypt(password.value)
            password.value = new_cipher.encrypt(plain_password)
            print(password.value)
            db.commit()
            db.refresh(password)
        return {"message": "Пароли успешно перешифрованы."}
    except Exception as e:
        # print(e)
        return {"message": "Возникла неизвестная ошибка..."}
