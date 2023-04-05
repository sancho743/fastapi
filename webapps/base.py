from fastapi import APIRouter

from webapps.users import route_users
from webapps.passwords import route_passwords
from webapps.auth import router_auth
from webapps.homepage import route_homepage
from webapps.groups import route_groups
from webapps.logs import route_logs


api_router = APIRouter()

api_router.include_router(route_users.router, prefix="/users")
api_router.include_router(route_passwords.router, prefix="/passwords")
api_router.include_router(route_groups.router, prefix="/groups")

api_router.include_router(router_auth.router)
api_router.include_router(route_homepage.router)
api_router.include_router(route_logs.router, prefix="/logs")

