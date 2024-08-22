from typing import Optional

from pydantic import BaseModel


class UserInformationSchemaIn(BaseModel):
    name: str
    first_name: str
    email: Optional[str]


class UserInformationSchemaOut(BaseModel):
    name: str
    first_name: str
    is_email: bool
