from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from apis.utils import OAuth2PasswordBearerWithCookie
from fastapi import Depends
from fastapi import APIRouter
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import status
from fastapi import HTTPException
from fastapi import Response
from schemas.tokens import AccessToken
from db.repository.users import get_user_by_username
from core.hashing import Hasher
from db.session import get_db
from core.config import settings
from datetime import timedelta
from core.security import create_access_token
from jose import JWTError, jwt

router = APIRouter()


def authenticate_user(
        username: str,
        password: str,
        db: Session = Depends(get_db)
):
    user = get_user_by_username(username=username, db=db)
    if not user:
        return False
    if not Hasher().verify_password(password, user.hashed_password):
        return False
    return user


@router.post("/token", response_model=AccessToken)
def login_for_access_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректное имя пользователя или пароль.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь заблокирован. Обратитесь к администратору сервиса, пожалуйста.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")


def get_current_user_from_token(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Сессия истекла. Авторизуйтесь, пожалуйста.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user
