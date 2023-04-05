# from passlib.context import CryptContext
#
# pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
#
#
# class Hasher:
#     @staticmethod
#     def verify_password(plain_password, hashed_password):
#         return pwd_context.verify(plain_password, hashed_password)
#
#     @staticmethod
#     def get_password_hash(password):
#         return pwd_context.hash(password)

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import binascii

TIME_COST = 16
MEMORY_COST = 2 ** 15
PARALLELISM = 2
HASH_LEN = 32
SALT_LEN = 16


class Hasher(object):
    def __init__(self):
        self.hasher = PasswordHasher(
            time_cost=TIME_COST,
            memory_cost=MEMORY_COST,
            parallelism=PARALLELISM,
            hash_len=HASH_LEN,
            salt_len=SALT_LEN
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            verify_valid = self.hasher.verify(hashed_password, plain_password)
            return verify_valid
        except VerifyMismatchError as e:
            return False

    def get_password_hash(self, plain_password: str) -> str:
        return self.hasher.hash(plain_password)


# my_hash = Hasher().get_password_hash("password")
#
# print(my_hash)
#
# print(Hasher().verify_password("password1", my_hash))

