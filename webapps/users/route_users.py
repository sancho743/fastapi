from db.session import get_db

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi import HTTPException

from fastapi.templating import Jinja2Templates

from fastapi.security.utils import get_authorization_scheme_param

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.repository.users import get_user_by_id
from db.repository.users import get_all_users
from db.repository.users import create_new_user
from db.repository.users import update_user_by_id
from db.repository.users import get_blocked_users
from db.repository.users import get_blocked_users_asc

from db.repository.passwords import get_all_passwords

from db.repository.groups import get_all_groups
from db.repository.groups import get_group_by_id

from db.models.users import User
from db.models.passwords import Password

from schemas.users import UserCreate

from sqlalchemy.exc import IntegrityError

from webapps.users.forms import UserCreateForm
from webapps.users.forms import UserUpdateForm

from schemas.users import UserUpdate


import asyncio

from apis.version1.route_login import get_current_user_from_token


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/detail/{id}")
def show_user_detail(
        id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login/",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    current_user: User = get_current_user_from_token(token=param, db=db)
    if not current_user.is_superuser:
        some_error = "Недостаточно прав для просмотра этой страницы"
        return responses.RedirectResponse(
            f"/?error={some_error}",
            status_code=status.HTTP_302_FOUND
        )
    try:
        float(id)
        if id < 1 or id > 100000:
            raise ValueError
    except ValueError:
        return responses.RedirectResponse(
            f"/?error=Некорректные входные данные.",
            status_code=status.HTTP_302_FOUND
        )
    user = get_user_by_id(id=id, db=db)
    if not user:
        return templates.TemplateResponse(
            "endpoints/users/no-user.html",
            {
                "request": request,
                "id": id,
                "current_user": current_user
            }
        )
    return templates.TemplateResponse(
        "endpoints/users/detail-user.html",
        {
            "request": request,
            "user": user,
            "id": id,
            "current_user": current_user
        }
    )


@router.get("/edit/{id}")
def update_user_by_id1(
        id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login/",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    current_user: User = get_current_user_from_token(token=param, db=db)
    if not current_user.is_superuser:
        some_error = "Недостаточно прав для просмотра этой страницы"
        return responses.RedirectResponse(
            f"/?error={some_error}",
            status_code=status.HTTP_302_FOUND
        )
    user_for_edit = get_user_by_id(id=id, db=db)
    return templates.TemplateResponse(
        "endpoints/users/edit-user.html",
        {
            "request": request,
            "current_user": current_user,
            "user": user_for_edit,
            "id": id,
            "groups": get_all_groups(db),
            "passwords": get_all_passwords(db)
        }
    )


@router.put("/edit/{id}")
async def edit_user(
        id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token)
):
    if not current_user.is_superuser:
        return {"message": "Недостаточно прав для выполнения данной операции."}
    form = UserUpdateForm(request)
    await form.load_data()
    if await form.is_valid():
        user = UserUpdate(
            is_superuser=form.is_superuser,
            is_blocked=form.is_blocked,
            need_to_change_password=form.need_to_change_password,
            master_password=form.master_password,
            passwords=form.passwords,
            groups=form.groups
        )
        try:
            message = update_user_by_id(id=id, user=user, db=db)
            return {"message": message["message"]}
        except Exception as e:
            form.__dict__.get("errors").append(e.__dict__.get("detail"))
            return {"message": form.__dict__.get("errors")}
    return {"message": form.__dict__.get("errors")}


@router.get("/create")
def create_user(
        request: Request,
        db: Session = Depends(get_db),
        msg: str = None
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login/",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    current_user: User = get_current_user_from_token(token=param, db=db)
    if not current_user.is_superuser:
        some_error = "Недостаточно прав для просмотра этой страницы"
        return responses.RedirectResponse(
            f"/?error={some_error}",
            status_code=status.HTTP_302_FOUND
        )
    return templates.TemplateResponse(
        "/endpoints/users/create-user.html",
        {
            "request": request,
            "passwords": get_all_passwords(db),
            "groups": get_all_groups(db),
            "current_user": current_user,
            "msg": msg
        }
    )


@router.post("/create")
async def create_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login/",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    current_user: User = get_current_user_from_token(token=param, db=db)
    if not current_user.is_superuser:
        return responses.RedirectResponse(
            f"/?error=Недостаточно прав для просмотра этой страницы.",
            status_code=status.HTTP_302_FOUND
        )
    form = UserCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        user = UserCreate(
            username=form.username,
            is_superuser=form.is_superuser,
            is_blocked=form.is_blocked,
            master_password=form.master_password,
            available_passwords=form.passwords,
            groups=form.groups
        )
        print(user.is_blocked)
        try:
            create_new_user(user=user, db=db)
            return templates.TemplateResponse(
                "/endpoints/users/create-user.html/",
                {
                    "request": request,
                    "current_user": current_user,
                    "errors": form.errors,
                    "passwords": get_all_passwords(db),
                    "groups": get_all_groups(db),
                    "msg": f"Новый пользователь '{user.username}' успешно создан."
                }
            )
            # return responses.RedirectResponse(
            #     "/users/create/?msg=Новый пользователь успешно создан.",
            #     status_code=status.HTTP_302_FOUND
            # )
        except Exception as e:
            form.__dict__.get("errors").append(e.__dict__.get("detail"))
            # form.__dict__.get("errors").append("Введенное имя пользователя уже существует.")
    return templates.TemplateResponse(
        "/endpoints/users/create-user.html/",
        {
            "request": request,
            "current_user": current_user,
            "errors": form.errors,
            "passwords": get_all_passwords(db),
            "groups": get_all_groups(db),
        }
    )


@router.get("/")
def all_users(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login/",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    current_user: User = get_current_user_from_token(token=param, db=db)
    if not current_user.is_superuser:
        some_error = "Недостаточно прав для просмотра этой страницы"
        return responses.RedirectResponse(
            f"/?error={some_error}",
            status_code=status.HTTP_302_FOUND
        )
    users = get_all_users(db=db)
    if not users:
        return templates.TemplateResponse(
            "endpoints/users/no-users.html",
            {
                "request": request,
                "users": users,
                "current_user": current_user
            }
        )
    return templates.TemplateResponse(
        "endpoints/users/all-users.html",
        {
            "request": request,
            "users": users,
            "header": "Список пользователей",
            "current_user": current_user
        }
    )


@router.get("/blocked")
def get_blocked_users(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login/",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    current_user: User = get_current_user_from_token(token=param, db=db)
    if not current_user.is_superuser:
        some_error = "Недостаточно прав для просмотра этой страницы"
        return responses.RedirectResponse(
            f"/?error={some_error}",
            status_code=status.HTTP_302_FOUND
        )
    blocked_users = get_blocked_users_asc(db=db)
    if not blocked_users:
        return templates.TemplateResponse(
            "endpoints/users/no-users.html",
            {
                "request": request,
                "current_user": current_user
            }
        )
    return templates.TemplateResponse(
        "endpoints/users/blocked-users.html",
        {
            "request": request,
            "users": blocked_users,
            "header": "Список заблокированных пользователей",
            "current_user": current_user
        }
    )
