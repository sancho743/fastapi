from db.repository.passwords import create_new_password
from db.session import get_db

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import Response
from fastapi import responses
from fastapi import status
from fastapi import HTTPException
from fastapi.templating import Jinja2Templates

from schemas.passwords import PasswordCreate

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.repository.passwords import get_password_by_id
from db.repository.passwords import get_all_passwords

from webapps.auth.forms import LoginForm

from apis.version1.route_login import login_for_access_token

from fastapi.security.utils import get_authorization_scheme_param

from core.security import (
    create_access_token  # ,
    # create_refresh_token
)

from db.repository.users import get_user_by_username
from db.repository.users import add_attempt
from db.repository.users import block_user
from db.repository.users import clear_attempts

from core.hashing import Hasher

from jose import jwt

from core.config import settings

from apis.version1.route_login import get_current_user_from_token

from db.repository.users import User

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/login")
def login(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return templates.TemplateResponse(
            "endpoints/login/login.html",
            {
                "request": request
            }
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    try:
        current_user: User = get_current_user_from_token(token=param, db=db)
        if current_user:
            return responses.RedirectResponse(
                "/",
                status_code=status.HTTP_302_FOUND
            )
        return templates.TemplateResponse(
            "endpoints/login/login.html",
            {
                "request": request
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "endpoints/login/login.html",
            {
                "request": request,
                "error": e.__getattribute__("detail")
            }
        )


# @router.post("/login")
# async def login(request: Request, db: Session = Depends(get_db)):
#     form = LoginForm(request)
#     await form.load_data()
#     if await form.is_valid():
#         try:
#             form.__dict__.update(msg="Вход выполнен успешно")
#             response = templates.TemplateResponse(
#                 "endpoints/home/homepage.html", form.__dict__,
#             )
#             login_for_access_token(response=response, form_data=form, db=db)
#             return response
#         except HTTPException:
#             form.__dict__.update(msg="")
#             form.__dict__.get("errors").append("Неверный логин и пароль")
#             return templates.TemplateResponse("endpoints/login/login.html", form.__dict__)
#     return templates.TemplateResponse("endpoints/login/login.html", form.__dict__)


@router.get("/logout")
async def logout():
    response = responses.RedirectResponse(
        "/",
        status_code=status.HTTP_302_FOUND
    )
    response.delete_cookie(
        key="access_token"
    )
    return response


@router.post("/login")
async def login(
        request: Request,
        db: Session = Depends(get_db)
):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            user = get_user_by_username(username=form.username, db=db)
            if user and (user.attempts >= 5 or user.is_blocked):
                if not user.is_blocked:
                    block_user(id=user.id, db=db)
                form.errors.append(f"Пользователь '{user.username}' заблокирован. Превышено количество попыток входа. "
                                   f"Обратитесь к системному администратору.")
                return templates.TemplateResponse(
                    "endpoints/login/login.html",
                    {
                        "request": request,
                        "errors": form.errors
                    }
                )
            if not user:
                form.errors.append(f"Пользователь с именем '{form.username}' не существует.")
                return templates.TemplateResponse(
                    "endpoints/login/login.html",
                    {
                        "request": request,
                        "errors": form.errors
                    }
                )
            else:
                response = responses.RedirectResponse(
                    '/',
                    status_code=status.HTTP_302_FOUND
                )
                login_for_access_token(response=response, form_data=form, db=db)
                clear_attempts(id=user.id, db=db)
                return response
        except Exception as e:
            form.errors.append(e.__getattribute__("detail"))
            user = get_user_by_username(username=form.username, db=db)
            if not user.is_blocked:
                add_attempt(id=user.id, db=db)
            return templates.TemplateResponse(
                "endpoints/login/login.html",
                {
                    "request": request,
                    "errors": form.errors
                }
            )
    return templates.TemplateResponse(
        "endpoints/login/login.html",
        {
            "request": request,
            "errors": form.errors
        }
    )
