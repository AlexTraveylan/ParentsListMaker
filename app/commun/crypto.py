import base64
import secrets

from cryptography.fernet import Fernet
from passlib.context import CryptContext

from app.settings import AES_KEY

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
