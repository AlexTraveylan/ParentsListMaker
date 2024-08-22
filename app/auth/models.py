from functools import cached_property
from typing import Optional

from pydantic import field_validator
from sqlmodel import Field

from app.commun.crypto import decrypt, encrypt, get_password_hash
from app.commun.validator import validate_password, validate_username
from app.database.model_base import BaseSQLModel
from app.database.repository import Repository


class User(BaseSQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    encrypted_username: str = Field(unique=True, alias="username")
    hashed_password: str = Field(alias="password")

    @cached_property
    def username(self) -> str:
        return decrypt(self.encrypted_username)

    @field_validator("encrypted_username")
    def username_format(cls, value: str) -> str:
        value = validate_username(value)

        return encrypt(value)

    @field_validator("hashed_password")
    def password_format(cls, value: str) -> str:
        value = validate_password(value)

        return get_password_hash(value)


class UserService(Repository[User]):
    __model__ = User


USER_SERVICE = UserService()
