from pydantic import BaseModel

from app.api.list_link.models import SchoolRelation


class SchoolSchemaIn(BaseModel):
    school_name: str
    city: str
    zip_code: str
    country: str
    adress: str
    school_relation: SchoolRelation


class SchoolSchemaOut(BaseModel):
    id: int
    school_name: str
    city: str
    zip_code: str
    country: str
    adress: str
