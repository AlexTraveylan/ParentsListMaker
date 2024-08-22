from pydantic import BaseModel, field_validator

from app.commun.validator import validate_email


class EmailSchema(BaseModel):
    email: str

    @field_validator("email")
    def email_format(cls, value: str) -> str:
        return validate_email(value)
