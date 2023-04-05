from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.config import settings

from apis.base import api_router
from webapps.base import api_router as web_app_router

from db.session import engine

from db.base import Base

# from db.primary_fill.primary_fill import primary_fill_user


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def include_router(app):
    app.include_router(api_router)
    app.include_router(web_app_router)


def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None
    )
    include_router(app)
    create_tables()
    configure_static(app)
    # primary_fill_user()
    return app


app = start_application()


# @app.on_event("startup")
# async def app_startup():
#     await check_db_connected()
#
#
# @app.on_event("shutdown")
# async def app_shutdown():
#     await check_db_disconnected()
