import factory
from factory.alchemy import SQLAlchemyModelFactory
from sqlmodel import Session

from app.api.links.models import ListLink
from app.api.parents_list.models import ParentsList
from app.api.school.models import School
from app.auth.models import User

TEST_PASSWORD = "Password123*"


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    username: str = factory.Faker("name")
    hashed_password: str = factory.LazyAttribute(lambda _: TEST_PASSWORD)


def get_user_factory(session: Session, **kwargs) -> User:
    UserFactory._meta.sqlalchemy_session = session

    return UserFactory(**kwargs)


class SchoolFactory(SQLAlchemyModelFactory):
    class Meta:
        model = School
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    school_name: str = factory.Faker("name")
    city: str = factory.Faker("city")
    zip_code: str = factory.Faker("postcode")
    country: str = factory.Faker("country")
    adress: str = factory.Faker("address")


def get_school_factory(session: Session, **kwargs) -> School:
    SchoolFactory._meta.sqlalchemy_session = session

    return SchoolFactory(**kwargs)


class ParentsListFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ParentsList
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    list_name: str = factory.Faker("name")
    holder_length: int = factory.Faker("random_int", min=1, max=15)
    school_id: int = factory.Sequence(lambda n: n)


def get_parents_list_factory(session: Session, **kwargs) -> ParentsList:
    ParentsListFactory._meta.sqlalchemy_session = session

    return ParentsListFactory(**kwargs)


class ListLinkFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ListLink
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    list_id: int = factory.Sequence(lambda n: n)
    is_admin: bool = factory.Faker("boolean")
    status: str = factory.LazyAttribute(lambda _: "waiting")
    user_id: int = factory.Sequence(lambda n: n)
    school_relation: str = factory.LazyAttribute(lambda _: "parent")
    school_id: int = factory.Sequence(lambda n: n)


def get_list_link_factory(session: Session, **kwargs) -> ListLink:
    ListLinkFactory._meta.sqlalchemy_session = session

    return ListLinkFactory(**kwargs)
