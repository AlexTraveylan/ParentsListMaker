from pydantic import BaseModel


class SchoolSchemaIn(BaseModel):
    school_name: str
    city: str
    zip_code: str
    country: str
    adress: str


class SchoolSchemaOut(BaseModel):
    id: int
    school_name: str
    city: str
    zip_code: str
    country: str
    adress: str
