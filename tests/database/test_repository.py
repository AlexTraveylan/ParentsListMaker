from typing import Optional

import factory
import pytest
from factory.alchemy import SQLAlchemyModelFactory
from sqlmodel import Field, Session, SQLModel, select

from app.database.repository import Repository
from app.exceptions import NotFoundException


class TestModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int


class TestModelFactory(SQLAlchemyModelFactory):
    class Meta:
        model = TestModel
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    age = factory.Faker("random_int", min=18, max=90)


def get_test_model_factory(session: Session, **kwargs):
    TestModelFactory._meta.sqlalchemy_session = session

    return TestModelFactory(**kwargs)


@pytest.fixture
def repositorytest():
    class RepositoryTest(Repository[TestModel]):
        __model__ = TestModel

    return RepositoryTest()


def test_create(repositorytest: Repository[TestModel], session: Session):
    item = TestModel(name="test", age=1)
    item = repositorytest.create(session, item)

    items_in_db = session.exec(select(TestModel)).all()

    assert len(items_in_db) == 1

    assert item.name == "test"


def test_get_or_raise(repositorytest: Repository[TestModel], session: Session):
    get_test_model_factory(session, name="test")

    item = repositorytest.get_or_raise(session, name="test")

    assert item.name == "test"


def test_get_or_raise_not_found(
    repositorytest: Repository[TestModel], session: Session
):
    with pytest.raises(NotFoundException):
        repositorytest.get_or_raise(session, name="test")


def test_get_all(repositorytest: Repository[TestModel], session: Session):
    get_test_model_factory(session)
    get_test_model_factory(session)
    get_test_model_factory(session)

    items = repositorytest.get_all(session)

    assert len(items) == 3


def test_delete(repositorytest: Repository[TestModel], session: Session):
    item = get_test_model_factory(session)

    assert repositorytest.delete(session, item.id) is True


def test_delete_not_found(repositorytest: Repository[TestModel], session: Session):
    item = get_test_model_factory(session)

    assert repositorytest.delete(session, item.id + 1) is False


def test_update(repositorytest: Repository[TestModel], session: Session):
    item = get_test_model_factory(session, name="test")
    item = repositorytest.update(session, item.id, name="test2")
    assert item.name == "test2"


class TestModel2(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    other_field: str


class TestModel2Factory(SQLAlchemyModelFactory):
    class Meta:
        model = TestModel2
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    other_field = factory.Faker("name")


def get_test_model2_factory(session: Session, **kwargs):
    TestModel2Factory._meta.sqlalchemy_session = session

    return TestModel2Factory(**kwargs)


@pytest.fixture
def repositorytest2():
    class RepositoryTest(Repository[TestModel2]):
        __model__ = TestModel2

    return RepositoryTest()


def test_get_or_raise_with_different_model(
    repositorytest: Repository[TestModel],
    repositorytest2: Repository[TestModel2],
    session: Session,
):
    get_test_model_factory(session, name="test")
    get_test_model2_factory(session, other_field="test")

    item = repositorytest.get_or_raise(session, name="test")
    item2 = repositorytest2.get_or_raise(session, other_field="test")

    assert item.name == "test"
    assert item2.other_field == "test"
