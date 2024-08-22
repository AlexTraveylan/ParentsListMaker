from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, Integer
from sqlmodel import Field

from app.database.model_base import BaseSQLModel
from app.database.repository import Repository


class EmailConfirmationToken(BaseSQLModel, table=True):
    __tablename__ = "email_confirmation_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True)
    is_confirmed: bool = Field(default=False)
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    user_id: int = Field(
        sa_column=Field(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )


class EmailConfirmationTokenService(Repository[EmailConfirmationToken]):
    __model__ = EmailConfirmationToken


EMAIL_CONFIRMATION_TOKEN_SERVICE = EmailConfirmationTokenService()
