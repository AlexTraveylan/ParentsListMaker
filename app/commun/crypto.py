import base64
import secrets
import string
from datetime import datetime, timedelta, timezone
from random import choices

import jwt
from cryptography.fernet import Fernet
from passlib.context import CryptContext

from app.settings import AES_KEY, SECRET_KEY

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_confirmation_token() -> str:
    return secrets.token_urlsafe(nbytes=32)


def encrypt(string_to_encrypt: str, key: bytes = AES_KEY) -> str:
    frnt = Fernet(key)
    encrypted = frnt.encrypt(string_to_encrypt.encode())

    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt(string_to_decrypt: str, key: bytes = AES_KEY) -> str:
    frnt = Fernet(key)
    decrypted = frnt.decrypt(base64.urlsafe_b64decode(string_to_decrypt))

    return decrypted.decode()


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


def generate_password() -> str:
    at_least_one_upper = string.ascii_uppercase
    at_least_one_lower = string.ascii_lowercase
    at_least_one_digit = string.digits

    return (
        secrets.token_urlsafe(nbytes=4)
        + choices(at_least_one_upper)[0]
        + choices(at_least_one_lower)[0]
        + choices(at_least_one_digit)[0]
    )


def generate_password_reset_token(user_id: int) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    data = {"sub": str(user_id), "exp": expiration}
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")


def verify_password_reset_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
        return user_id
    except jwt.exceptions.InvalidTokenError:
        return None
