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


