from db.session import get_db

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status

from fastapi.templating import Jinja2Templates

from fastapi.security.utils import get_authorization_scheme_param

from sqlalchemy.orm import Session

from db.models.users import User

from apis.version1.route_login import get_current_user_from_token

from db.repository.groups import get_all_groups
from db.repository.groups import get_all_groups_asc
from db.repository.groups import get_group_by_id

from db.repository.users import get_all_users
from db.repository.users import get_all_users_asc

from db.repository.passwords import get_all_passwords
from db.repository.passwords import get_all_passwords_asc

from webapps.groups.forms import GroupCreateForm
from webapps.groups.forms import GroupUpdateForm

from schemas.groups import GroupCreate
from schemas.groups import GroupUpdate

from db.repository.groups import create_new_group
from db.repository.groups import update_group_by_id


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
def all_groups(
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
        some_error = "Недостаточно прав для просмотра этой страницы."
        return responses.RedirectResponse(
            f"/?error={some_error}",
            status_code=status.HTTP_302_FOUND
        )
    groups = get_all_groups(db)
    if not groups:
        return templates.TemplateResponse(
            "endpoints/groups/no-groups.html",
            {
                "request": request,
                "current_user": current_user
            }
        )
    return templates.TemplateResponse(
        "endpoints/groups/all-groups.html",
        {
            "request": request,
            "groups": groups,
            "header": "Список групп",
            "current_user": current_user
        }
    )


@router.get("/create")
def create_group(
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
        return responses.RedirectResponse(
            f"/?error=Недостаточно прав для просмотра этой страницы.",
            status_code=status.HTTP_302_FOUND
        )
    return templates.TemplateResponse(
        "/endpoints/groups/create-group.html",
        {
            "request": request,
            "passwords": get_all_passwords_asc(db),
            "users": get_all_users_asc(db),
            "current_user": current_user,
            "msg": msg
        }
    )


@router.post("/create")
async def create_group(request: Request, db: Session = Depends(get_db)):
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
    form = GroupCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        group = GroupCreate(
            group_name=form.group_name,
            description=form.description,
            users=form.users,
            passwords=form.passwords
        )
        try:
            create_new_group(group=group, db=db)
            return responses.RedirectResponse(
                "/groups/create/?msg=Новая группа успешно создана.",
                status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            form.__dict__.get("errors").append(e.__dict__.get("detail"))
    return templates.TemplateResponse(
        "/endpoints/groups/create-group.html/",
        {
            "request": request,
            "current_user": current_user,
            "errors": form.errors,
            "passwords": get_all_passwords_asc(db),
            "users": get_all_users_asc(db),
        }
    )


@router.get("/detail/{id}")
def show_group_detail(id: int, request: Request, db: Session = Depends(get_db)):
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
    group = get_group_by_id(id=id, db=db)
    if not group:
        return templates.TemplateResponse(
            "endpoints/groups/no-group.html",
            {
                "request": request,
                "id": id,
                "current_user": current_user
            }
        )
    return templates.TemplateResponse(
        "endpoints/groups/detail-group.html",
        {
            "request": request,
            "group": group,
            "id": id,
            "current_user": current_user,
        }
    )


@router.get("/edit/{id}")
def update_group(
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
    group_for_edit = get_group_by_id(id=id, db=db)
    return templates.TemplateResponse(
        "endpoints/groups/edit-group.html",
        {
            "request": request,
            "current_user": current_user,
            "group": group_for_edit,
            "id": id,
            "users": get_all_users(db),
            "passwords": get_all_passwords(db)
        }
    )


@router.put("/edit/{id}")
async def update_group(
        id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token)
):
    if not current_user.is_superuser:
        return {"message": "Недостаточно прав для выполнения данной операции."}
    form = GroupUpdateForm(request)
    await form.load_data()
    if await form.is_valid():
        group = GroupUpdate(
            group_name=form.group_name,
            description=form.description,
            users=form.users,
            passwords=form.passwords
        )
        try:
            message = update_group_by_id(id=id, group=group, db=db)
            return {"message": message["message"]}
        except Exception as e:
            form.__dict__.get("errors").append(e.__dict__.get("detail"))
            return {"message": 123}
    return {"message": form.__dict__.get("errors")}
