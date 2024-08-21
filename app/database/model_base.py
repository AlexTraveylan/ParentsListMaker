from pydantic import ConfigDict
from sqlmodel import SQLModel

# Modify sqlModel to force type validation


class BaseSQLModel(SQLModel):
    model_config = ConfigDict(validate_assignment=True)
