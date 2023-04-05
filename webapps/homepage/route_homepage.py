from fastapi import APIRouter
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi import Depends
from sqlalchemy.orm import Session
from db.session import get_db
from fastapi.templating import Jinja2Templates
from fastapi.security.utils import get_authorization_scheme_param
from db.repository.users import User
from apis.version1.route_login import get_current_user_from_token

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
def get_homepage(
        request: Request,
        error: str = None,
        db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if token is None:
        return templates.TemplateResponse(
            "endpoints/home/homepage.html",
            {
                "request": request,
                "error": error
            }
        )
        # return responses.RedirectResponse(
        #     "/login",
        #     status_code=status.HTTP_302_FOUND
        # )
    scheme, param = get_authorization_scheme_param(
        token
    )
    try:
        current_user: User = get_current_user_from_token(token=param, db=db)
        if error and len(error) > 100:
            return templates.TemplateResponse(
                "endpoints/home/homepage.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "error": "Не надо пытаться сломать сайт, пожалуйста :)"
                }
            )
        return templates.TemplateResponse(
            "endpoints/home/homepage.html",
            {
                "request": request,
                "current_user": current_user,
                "error": error
            }
        )
    except Exception as e:
        return responses.RedirectResponse(
            "/login",
        )

    # if not current_user.is_superuser:
    #     some_error = "Недостаточно прав для просмотра этой страницы"
    #     return responses.RedirectResponse(
    #         f"/?error={some_error}",
    #         status_code=status.HTTP_302_FOUND
    #     )
