import os

from dotenv import load_dotenv, find_dotenv

from string import ascii_uppercase
from string import ascii_lowercase
from string import digits

# from pathlib import Path
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

load_dotenv(find_dotenv())


class Settings:
    PROJECT_NAME: str = "Password Manager"
    PROJECT_VERSION: str = "0.9.5"

    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    DB_DRIVER: str = os.getenv("DB_DRIVER")

    DATABASE_URL: str = f'{DB_DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}'

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

    AES_SECRET_KEY: str = os.getenv("AES_SECRET_KEY")
    AES_NEW_SECRET_KEY: str = os.getenv("AES_NEW_SECRET_KEY")


class PasswordParameters:
    ROCKYOU_PATH: str = os.getenv("")

    UPPER_CASE: str = ascii_uppercase
    LOWER_CASE: str = ascii_lowercase
    DIGITS: str = digits
    MATH: str = '+*/-='
    UNDERSCORE: str = '_'
    PUNCTUATION: str = ',.:;"!?'
    SPECIAL: str = '''@#$%^&'\`|~'''
    BRACKETS: str = '()[]{}<>'

    SPECIAL_EXTRA: str = MATH + UNDERSCORE + PUNCTUATION + SPECIAL + BRACKETS

    RECOMMENDED_LENGTH: int = int(os.getenv("RECOMMENDED_LENGTH"))
    RECOMMENDED_NUMBER_OF_UPPER_CASE: int = int(os.getenv("RECOMMENDED_NUMBER_OF_UPPER_CASE"))
    RECOMMENDED_NUMBER_OF_LOWER_CASE: int = int(os.getenv("RECOMMENDED_NUMBER_OF_LOWER_CASE"))
    RECOMMENDED_NUMBER_OF_DIGITS: int = int(os.getenv("RECOMMENDED_NUMBER_OF_DIGITS"))
    RECOMMENDED_NUMBER_OF_SPECIAL: int = int(os.getenv("RECOMMENDED_NUMBER_OF_SPECIAL"))

    PASSWORD_UPDATE_PERIOD: int = int(os.getenv("PASSWORD_UPDATE_PERIOD"))


settings = Settings()

password_parameters = PasswordParameters()
