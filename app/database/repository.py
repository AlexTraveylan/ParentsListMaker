from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from app.exceptions import DatabaseException, NotFoundException


class Repository[T]:
    __model__: type[T]

    @staticmethod
    def create(session: Session, item: T) -> T:
        try:
            session.add(item)
            session.flush()
            session.refresh(item)
        except Exception as e:
            raise DatabaseException from e

        return item

    def update(self, session: Session, id_: int, **kwargs) -> T:
        try:
            bd_item = session.get_one(self.__model__, id_)
        except Exception as e:
            raise DatabaseException from e

        for key, value in kwargs.items():
            setattr(bd_item, key, value)

        session.flush()
        session.refresh(bd_item)

        return bd_item

    def get_or_raise(self, session: Session, **kwargs) -> T:
        filter_kwargs = [
            getattr(self.__model__, key) == value for key, value in kwargs.items()
        ]

        statement = select(self.__model__).where(*filter_kwargs)
        item = session.exec(statement)

        first_item = item.first()

        if first_item is None:
            raise NotFoundException("No item found")

        return first_item

    def get_all(self, session: Session) -> list[T]:
        return session.exec(select(self.__model__)).all()

    def delete(self, session: Session, id_: int) -> bool:
        try:
            item = session.get_one(self.__model__, id_)
        except NoResultFound:
            return False

        session.delete(item)

        return True
