from datetime import datetime

from db.repository.passwords import create_new_password
from db.session import get_db

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi import Form
from fastapi.templating import Jinja2Templates

from schemas.passwords import PasswordCreate, PasswordUpdate

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.repository.passwords import get_password_by_id
from db.repository.passwords import get_all_passwords
from db.repository.passwords import update_password_by_id
from db.repository.passwords import get_all_passwords_by_user_id
from db.repository.passwords import get_expired_passwords

from fastapi.security.utils import get_authorization_scheme_param

from apis.version1.route_login import get_current_user_from_token

from db.models.users import User

from db.repository.groups import get_all_groups
from db.repository.groups import get_all_groups_asc

from db.repository.users import get_all_users
from db.repository.users import get_nonadmin_users
from db.repository.users import get_nonadmin_users_asc
from db.repository.users import get_all_users_asc
from db.repository.users import user_password_access

from db.repository.passwords import get_all_passwords
from db.repository.passwords import get_all_passwords_asc
from db.repository.passwords import create_new_personal_password
from db.repository.passwords import reencryption_group_passwords

from webapps.passwords.forms import PasswordCreateForm
from webapps.passwords.forms import PasswordChangeForm
from webapps.passwords.forms import PasswordReencryptForm

from apis.version1.route_passwords import generate_password

from db.repository.users import change_personal_password

from webapps.passwords.forms import PasswordGenerateForm, PasswordUpdateForm

from core.hashing import Hasher

from core.config import password_parameters

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
def all_passwords(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    try:
        current_user: User = get_current_user_from_token(token=param, db=db)
        if not current_user.is_superuser:
            available_passwords = list()
            available_passwords.extend(current_user.available_passwords)
            group_passwords = list()
            for group in current_user.groups:
                group_passwords.extend(group.passwords)
            if not available_passwords and not group_passwords:
                return templates.TemplateResponse(
                    "endpoints/passwords/no-passwords.html",
                    {
                        "request": request,
                        "current_user": current_user,
                        "msg": "Пароли не найдены."
                    }
                )
            return templates.TemplateResponse(
                "endpoints/passwords/all-passwords-nonadmin.html",
                {
                    "request": request,
                    "available_passwords": available_passwords,
                    "group_passwords": group_passwords,
                    "header": "Список паролей",
                    "current_user": current_user
                }
            )
        single_passwords = get_all_passwords(db)
        if not single_passwords:
            return templates.TemplateResponse(
                "endpoints/passwords/no-passwords.html",
                {
                    "request": request,
                    "current_user": current_user
                }
            )
        return templates.TemplateResponse(
            "endpoints/passwords/all-passwords.html",
            {
                "request": request,
                "single_passwords": single_passwords,
                "header": "Список паролей",
                "current_user": current_user
            }
        )
    except Exception as e:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )


@router.get("/generate")
def get_password_generator(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return templates.TemplateResponse(
            "endpoints/passwords/password-generate.html",
            {
                "request": request,
                "header": "Генератор паролей"
            }
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    current_user: User = get_current_user_from_token(token=param, db=db)
    return templates.TemplateResponse(
        "endpoints/passwords/password-generate.html",
        {
            "request": request,
            "header": "Генератор паролей",
            "current_user": current_user
        }
    )


@router.post("/generate")
async def post_password_generator(
        request: Request
):
    form = PasswordGenerateForm(request)
    await form.load_data()
    if await form.is_valid():
        password, recommendations = generate_password(
            form.length,
            form.lowercase,
            form.uppercase,
            form.digits,
            form.math,
            form.underscore,
            form.punctuation,
            form.brackets,
            form.other_special
        )
        return templates.TemplateResponse(
            "endpoints/passwords/password-generate.html",
            {
                "request": request,
                "header": "Генератор паролей",
                "password": password,
                "recommendations": recommendations,
                "errors": form.errors
            }
        )
    else:
        return templates.TemplateResponse(
            "endpoints/passwords/password-generate.html",
            {
                "request": request,
                "header": "Генератор паролей",
                "errors": form.errors
            }
        )


@router.get("/create")
def create_password(
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
        return templates.TemplateResponse(
            "/endpoints/passwords/create-password.html",
            {
                "request": request,
                "current_user": current_user,
                "msg": msg
            }
        )
    return templates.TemplateResponse(
        "/endpoints/passwords/create-password.html",
        {
            "request": request,
            "users": get_nonadmin_users_asc(db),
            "groups": get_all_groups_asc(db),
            "current_user": current_user,
            "msg": msg
        }
    )


@router.post("/create")
async def create_password(
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
    form = PasswordCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        password = PasswordCreate(
            service_name=form.service_name,
            service_address=form.service_address,
            password_type=form.password_type,
            description=form.description,
            users=form.users,
            groups=form.groups,
            login=form.login,
            value=form.value
        )
        try:
            if password.password_type == 1:
                create_new_password(password=password, db=db, current_user_id=current_user.id)
            else:
                create_new_personal_password(password=password, db=db, current_user=current_user)
            return responses.RedirectResponse(
                "/passwords/create/?msg=Новый пароль успешно создан.",
                status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            form.__dict__.get("errors").append(e.__dict__.get("detail"))
            return templates.TemplateResponse(
                "/endpoints/passwords/create-password.html/",
                {
                    "request": request,
                    "current_user": current_user,
                    "errors": form.errors,
                    "users": get_nonadmin_users_asc(db=db),
                    "groups": get_all_groups_asc(db=db),
                }
            )
    return templates.TemplateResponse(
        "/endpoints/passwords/create-password.html/",
        {
            "request": request,
            "current_user": current_user,
            "errors": form.errors,
            "users": get_nonadmin_users(db=db),
            "groups": get_all_groups_asc(db=db),
        }
    )


@router.get("/detail/{id}")
def show_password_detail(
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
    password = get_password_by_id(id=id, db=db, user=current_user)
    if not password:
        return templates.TemplateResponse(
            "endpoints/passwords/no-password.html",
            {
                "request": request,
                "id": id,
                "current_user": current_user
            }
        )
    if current_user.id != password.owner_id and not (current_user.is_superuser and password.password_type == 1):
        some_error = "Недостаточно прав для просмотра этой страницы."
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
    return templates.TemplateResponse(
        "endpoints/passwords/detail-password.html",
        {
            "request": request,
            "password": password,
            "id": id,
            "current_user": current_user,
            "expired": bool((datetime.utcnow() - password.date_created).days > 90)
        }
    )


@router.get("/edit/{id}")
def edit_password(
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
    password = get_password_by_id(id=id, db=db, user=current_user)
    if current_user.id != password.owner_id and not (current_user.is_superuser and password.password_type == 1):
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
    if not password:
        return templates.TemplateResponse(
            "endpoints/passwords/no-password.html",
            {
                "request": request,
                "id": id,
                "current_user": current_user
            }
        )
    return templates.TemplateResponse(
        "endpoints/passwords/edit-password.html",
        {
            "request": request,
            "password": password,
            "id": id,
            "current_user": current_user,
            "users": get_nonadmin_users(db=db),
            "groups": get_all_groups(db=db),
            "expired": bool((datetime.utcnow() - password.date_created).days > 90)
        }
    )


@router.put("/edit/{id}")
async def edit_password(
        id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token)
):
    password = get_password_by_id(id=id, db=db, user=current_user)
    if current_user.id != password.owner_id and not (current_user.is_superuser and password.password_type == 1):
        return {"message": "Недостаточно прав для выполнения данной операции."}
    form = PasswordUpdateForm(request)
    await form.load_data()
    if await form.is_valid():
        password = PasswordUpdate(
            service_name=form.service_name,
            service_address=form.service_address,
            description=form.description,
            users=form.users,
            groups=form.groups,
            login=form.login,
            value=form.value
        )
        try:
            message = update_password_by_id(id=id, password=password, db=db)
            return {"message": message["message"]}
        except Exception as e:
            form.__dict__.get("errors").append(e.__dict__.get("detail"))
            return {"message": form.__dict__.get("errors")}
    return {"message": form.__dict__.get("errors")}


@router.get("/personal")
def get_personal_passwords(
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
    try:
        current_user: User = get_current_user_from_token(token=param, db=db)
        if current_user.is_superuser:
            passwords = get_all_passwords(db=db)
        else:
            passwords = get_all_passwords_by_user_id(user=current_user, db=db)
        if not passwords:
            return templates.TemplateResponse(
                "endpoints/passwords/no-passwords.html",
                {
                    "request": request,
                    "passwords": passwords,
                    "header": "!!!Список паролей!!!",
                    "current_user": current_user
                }
            )
        return templates.TemplateResponse(
            "endpoints/passwords/personal-passwords.html",
            {
                "request": request,
                "passwords": passwords,
                "header": "Список паролей",
                "current_user": current_user
            }
        )
    except Exception as e:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )


@router.get("/by-groups")
def passwords_by_groups(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    try:
        current_user: User = get_current_user_from_token(token=param, db=db)
        if not current_user.is_superuser:
            some_error = "Недостаточно прав для просмотра этой страницы"
            return responses.RedirectResponse(
                f"/?error={some_error}",
                status_code=status.HTTP_302_FOUND
            )
        groups = get_all_groups(db=db)
        if not groups:
            return templates.TemplateResponse(
                "endpoints/groups/no-groups.html",
                {
                    "request": request,
                    "current_user": current_user
                }
            )
        return templates.TemplateResponse(
            "endpoints/passwords/passwords-by-groups.html",
            {
                "request": request,
                "groups": groups,
                "header": "Список паролей по группам",
                "current_user": current_user
            }
        )
    except Exception as e:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )


@router.get("/need-to-change")
def passwords_to_change(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    try:
        current_user: User = get_current_user_from_token(token=param, db=db)
        if not current_user.is_superuser:
            some_error = "Недостаточно прав для просмотра этой страницы"
            return responses.RedirectResponse(
                f"/?error={some_error}",
                status_code=status.HTTP_302_FOUND
            )
        passwords = get_expired_passwords(db=db)
        if not passwords:
            return templates.TemplateResponse(
                "endpoints/passwords/no-expired-passwords.html",
                {
                    "request": request,
                    "current_user": current_user
                }
            )
        return templates.TemplateResponse(
            "endpoints/passwords/passwords-to-change.html",
            {
                "request": request,
                "passwords": passwords,
                "header": "Список паролей, требующих изменений.",
                "current_user": current_user
            }
        )
    except Exception as e:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )


@router.get("/change-personal-password")
def change_password(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    try:
        current_user: User = get_current_user_from_token(token=param, db=db)
        need_to_change = False
        if current_user.need_to_change_password or (datetime.utcnow() - current_user.password_update_date).days > 180:
            need_to_change = True
        return templates.TemplateResponse(
            "endpoints/passwords/change-personal-password.html",
            {
                "request": request,
                "current_user": current_user,
                "need_to_change": need_to_change,
                "parameters": password_parameters
            }
        )
    except Exception as e:
        # print(e)
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )


@router.post("/change-personal-password")
async def change_password(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    try:
        current_user: User = get_current_user_from_token(token=param, db=db)
        form = PasswordChangeForm(request)
        await form.load_data()
        if await form.is_valid():
            if not Hasher().verify_password(form.current_password, current_user.hashed_password):
                form.errors.append("Текущий пароль введен некорректно.")
                return templates.TemplateResponse(
                    "/endpoints/passwords/change-personal-password.html/",
                    {
                        "request": request,
                        "current_user": current_user,
                        "errors": form.errors
                    }
                )
            else:
                result = change_personal_password(id=current_user.id, db=db, new_password=form.new_password)
                message, recommendations = result["message"], result["recommendations"]
                return templates.TemplateResponse(
                    "/endpoints/passwords/change-personal-password.html/",
                    {
                        "request": request,
                        "current_user": current_user,
                        "errors": form.errors,
                        "message": message,
                        "recommendations": recommendations
                    }
                )
        else:
            return templates.TemplateResponse(
                "/endpoints/passwords/change-personal-password.html/",
                {
                    "request": request,
                    "current_user": current_user,
                    "errors": form.errors
                }
            )
    except Exception as e:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )


@router.get("/reencryption")
def change_password(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    try:
        current_user: User = get_current_user_from_token(token=param, db=db)
        if not current_user.is_superuser:
            some_error = "Недостаточно прав для просмотра этой страницы"
            return responses.RedirectResponse(
                f"/?error={some_error}",
                status_code=status.HTTP_302_FOUND
            )

        return templates.TemplateResponse(
            "endpoints/passwords/reencryption-passwords.html",
            {
                "request": request,
                "current_user": current_user
            }
        )
    except Exception as e:
        # print(e)
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )


@router.post("/reencryption")
async def change_password(
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )
    scheme, param = get_authorization_scheme_param(
        token
    )
    try:
        current_user: User = get_current_user_from_token(token=param, db=db)
        if not current_user.is_superuser:
            some_error = "Недостаточно прав для просмотра этой страницы"
            return responses.RedirectResponse(
                f"/?error={some_error}",
                status_code=status.HTTP_302_FOUND
            )
        form = PasswordReencryptForm(request)
        await form.load_data()
        if await form.is_valid():
            if not Hasher().verify_password(form.password, current_user.hashed_password):
                form.errors.append("Пароль введен некорректно. Изменения не применены.")
                return templates.TemplateResponse(
                    "/endpoints/passwords/reencryption-passwords.html/",
                    {
                        "request": request,
                        "current_user": current_user,
                        "errors": form.errors
                    }
                )
            else:
                result = reencryption_group_passwords(db=db)
                message = result["message"]
                return templates.TemplateResponse(
                    "/endpoints/passwords/reencryption-passwords.html/",
                    {
                        "request": request,
                        "current_user": current_user,
                        "errors": form.errors,
                        "message": message
                    }
                )
        else:
            return templates.TemplateResponse(
                "/endpoints/passwords/reencryption-passwords.html/",
                {
                    "request": request,
                    "current_user": current_user,
                    "errors": form.errors
                }
            )
    except Exception as e:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_302_FOUND
        )
