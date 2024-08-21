import contextlib

from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

from app.exceptions import ParentsListMakerException
from app.settings import DB_URL

# Create the database

engine = create_engine(DB_URL)
SQLModel.metadata.create_all(engine)


@contextlib.contextmanager
def unit():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except ParentsListMakerException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        raise ValueError(f"Rolling back, cause : {str(e)}") from e
    finally:
        session.close()
