import factory
from factory.alchemy import SQLAlchemyModelFactory
from sqlmodel import Session

from app.auth.models import User
from app.commun.crypto import encrypt

TEST_PASSWORD = "Password123*"


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    username: str = factory.Faker("name")
    hashed_password: str = encrypt(TEST_PASSWORD)


def get_user_factory(session: Session, **kwargs) -> User:
    UserFactory._meta.sqlalchemy_session = session

    return UserFactory(**kwargs)
