from functools import cached_property
from typing import Optional

from pydantic import field_validator
from sqlmodel import Field

from app.api.school.schemas import SchoolSchemaOut
from app.commun.crypto import decrypt, encrypt
from app.commun.validator import validate_string
from app.database.model_base import BaseSQLModel
from app.database.repository import Repository


class School(BaseSQLModel, table=True):
    __tablename__ = "schools"

    id: Optional[int] = Field(default=None, primary_key=True)
    encrypted_school_name: str = Field(alias="school_name")
    encrypted_city: str = Field(alias="city")
    encrypted_zip_code: str = Field(alias="zip_code")
    encrypted_country: str = Field(alias="country")
    encrypted_adress: str = Field(alias="adress")

    @cached_property
    def school_name(self) -> str:
        return decrypt(self.encrypted_school_name)

    @cached_property
    def city(self) -> str:
        return decrypt(self.encrypted_city)

    @cached_property
    def zip_code(self) -> str:
        return decrypt(self.encrypted_zip_code)

    @cached_property
    def country(self) -> str:
        return decrypt(self.encrypted_country)

    @cached_property
    def adress(self) -> str:
        return decrypt(self.encrypted_adress)

    @field_validator("encrypted_school_name")
    def school_name_format(cls, value: str) -> str:
        value = validate_string(value)

        return encrypt(value)

    @field_validator("encrypted_city")
    def city_format(cls, value: str) -> str:
        value = validate_string(value)

        return encrypt(value)

    @field_validator("encrypted_zip_code")
    def zip_code_format(cls, value: str) -> str:
        value = validate_string(value)

        return encrypt(value)

    @field_validator("encrypted_country")
    def country_format(cls, value: str) -> str:
        value = validate_string(value)

        return encrypt(value)

    @field_validator("encrypted_adress")
    def adress_format(cls, value: str) -> str:
        value = validate_string(value)

        return encrypt(value)

    def to_decrypted(self) -> SchoolSchemaOut:
        return SchoolSchemaOut(
            id=self.id,
            school_name=self.school_name,
            city=self.city,
            zip_code=self.zip_code,
            country=self.country,
            adress=self.adress,
        )


class SchoolService(Repository[School]):
    __model__ = School


SCHOOL_SERVICE = SchoolService()
