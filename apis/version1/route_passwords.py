from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import status

from schemas.shows import ShowPassword

from sqlalchemy.orm import Session

from db.session import get_db

from db.repository.passwords import get_all_passwords
from db.repository.passwords import get_password_by_id
from db.repository.passwords import delete_password_by_id

from typing import List

from core.password_generating import GeneratedPassword

from db.models.users import User

from apis.version1.route_login import get_current_user_from_token


router = APIRouter()


@router.get("/api-all", response_model=List[ShowPassword])
def read_passwords(db: Session = Depends(get_db)):
    passwords = get_all_passwords(db)
    if not passwords:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"there is no data")
    return passwords


@router.post("/api-password-generate")
def generate_password(
        length: int = Form(),
        lowercase: bool = Form(),
        uppercase: bool = Form(),
        digits: bool = Form(),
        math: bool = Form(),
        underscore: bool = Form(),
        punctuation: bool = Form(),
        brackets: bool = Form(),
        other_special: bool = Form()
):
    try:
        float(length)
        password = GeneratedPassword(int(length), bool(lowercase), bool(uppercase), bool(digits), bool(math),
                                     bool(underscore), bool(punctuation), bool(brackets), bool(other_special))
        password.accumulate_alphabet_by_conditions()
        password.generate_password_by_conditions()
        return password.get_password(), password.get_recommendations()
    except ValueError:
        return {"error": "NoneType"}


@router.get("/api-secure-password")
def get_secure_password():
    return {"message": GeneratedPassword().generate_password()}


# @router.post("/api-create", response_model=ShowPassword)
# def create_password(password: PasswordCreate, db: Session = Depends(get_db)):
#     password = create_new_password(password=password, db=db)
#     return password


@router.get("/api-info/{id}", response_model=ShowPassword)
def get_password(
        id: int,
        db: Session = Depends(get_db)
):
    password = get_password_by_id(id=id, db=db)
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"password with id {id} does not exist"
        )
    return password


@router.delete("/api-delete/{id}")
def delete_password(
        id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token)
):
    password_to_delete = get_password_by_id(id=id, db=db, user=current_user)
    if not password_to_delete:
        return {"message": f"Пароль с id={id} не найден."}
    if current_user.id == password_to_delete.owner_id:
        if password_to_delete.password_type == 1:
            password_to_delete.users.clear()
            password_to_delete.groups.clear()
        delete_password_by_id(id=id, db=db)
        return {"message": f"Пароль с id={id} успешно удален."}
    else:
        return {"message": f"Недостаточно прав для выполнения данного действия"}
    # raise HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Недостаточно прав для выполнения данного действия."
    # )

