from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from db.repository.users import (
    create_new_user,
    get_all_users,
    get_user_by_id,
    get_user_by_username
)

from schemas.shows import ShowUser
from schemas.users import UserCreate

from db.session import get_db

from typing import List

from db.models.users import User

from apis.version1.route_login import get_current_user_from_token

from db.repository.users import clear_user_passwords
from db.repository.users import clean_user_groups
from db.repository.users import delete_user_by_id
from db.repository.users import unblock_user


router = APIRouter()


@router.get("/api-all", response_model=List[ShowUser])  # add feature to hide/unhide inactive users
def read_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    if not users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"there is no data")
    return users


@router.post("/api-create", response_model=ShowUser)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user = create_new_user(user=user, db=db)
    return user


@router.get("/api-info/{id}", response_model=ShowUser)  # need to enable auth
def get_user_via_id(id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(id=id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"user with id {id} does not exist")
    # if current_user.is_superuser:
    return user


@router.get("/api-info/{username}", response_model=ShowUser)
def get_user_via_username(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"user with username {username} does not exist")
    # if current_user.is_superuser:
    return user


# @router.delete("/api-delete/{id}")  # deleting sudoer by sudoer
# def delete_user(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
#     user = get_user_by_id(id=id, db=db)
#     if not user:
#         return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with {id} does not exist")
#     if current_user.id == user.id:
#         return {"msg": "You can't remove current user."}
#         # raise f"You can't remove current user."
#     if current_user.is_superuser:
#         delete_user_by_id(id=id, db=db)
#         return {"msg": "Successfully deleted."}
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                         detail=f"You are not permitted!")


@router.delete("/api-delete/{id}")
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    user_to_delete = get_user_by_id(id=id, db=db)
    if not user_to_delete:
        return {"message": f"Пользователь с id={id} не найден."}
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND, # bad request I guess
        #     detail=f"Пользователь с id={id} не существует.",
        # )
    if user_to_delete.is_superuser:
        return {"message": "Невозможно удалить пользователя с правами администратора."}
    if current_user.is_superuser:
        clear_user_passwords(user=user_to_delete, db=db)
        clean_user_groups(user=user_to_delete, db=db)
        delete_user_by_id(id=id, db=db)
        return {"message": f"Пользователь с id={id} успешно удален."}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недостаточно прав для выполнения данного действия."
    )


@router.put("/api-unblock/{id}")
def unblock_user_api(  # name?
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    user_to_unblock = get_user_by_id(id=id, db=db)
    if not user_to_unblock:
        return {"message": f"Пользователь с id={id} не найден."}
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     detail=f"Пользователь с id={id} не существует.",
        # )
    if current_user.is_superuser:
        result = unblock_user(id=id, db=db)
        return {"message": result["message"]}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недостаточно прав для выполнения данного действия."
    )


# @router.put("/api-edit/{id}")
# def edit_user(
#         id: int,
#         password=Form(),
#         is_superuser=Form(),
#         passwords=Form()
#         groups=Form(),
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user_from_token),
# ):
#     return {"message": password}
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Недостаточно прав для выполнения данного действия."
#         )
#     message = update_user_by_id(id=id, user=user, db=db)
#     return {"message": message}


# @router.put("/api-edit/{id}")
# def edit_user(
#         id: int,
#         groups: list = Form(),
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user_from_token),
# ):
#     return groups
