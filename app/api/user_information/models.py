from functools import cached_property
from typing import Optional

from pydantic import field_validator
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field

from app.commun.crypto import decrypt, encrypt
from app.commun.validator import validate_email, validate_username
from app.database.model_base import BaseSQLModel
from app.database.repository import Repository


class UserInformation(BaseSQLModel, table=True):
    __tablename__ = "user_informations"

    id: Optional[int] = Field(default=None, primary_key=True)
    encrypted_name: str = Field(max_length=64, min_length=2, alias="name")
    encrypted_first_name: str = Field(max_length=64, min_length=2, alias="first_name")
    encrypted_email: Optional[str] = Field(unique=True, default=None, alias="email")
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )

    @cached_property
    def email(self) -> str:
        return decrypt(self.encrypted_email)

    @cached_property
    def name(self) -> str:
        return decrypt(self.encrypted_name)

    @cached_property
    def first_name(self) -> str:
        return decrypt(self.encrypted_first_name)

    @field_validator("encrypted_email")
    def email_format(cls, value: str) -> str:
        value = validate_email(value)

        return encrypt(value)

    @field_validator("encrypted_name")
    def name_format(cls, value: str) -> str:
        value = validate_username(value)

        return encrypt(value)

    @field_validator("encrypted_first_name")
    def first_name_format(cls, value: str) -> str:
        value = validate_username(value)

        return encrypt(value)


class UserInformationService(Repository[UserInformation]):
    __model__ = UserInformation


USER_INFORMATION_SERVICE = UserInformationService()
