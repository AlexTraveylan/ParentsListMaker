import contextlib
import logging

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

from app.exceptions import (
    CannotCreateStillExistsException,
    ParentsListMakerException,
    UnauthorizedException,
)
from app.settings import DB_URL

logger = logging.getLogger(__name__)

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
        logger.exception(e)
        raise e
    except Exception as e:
        session.rollback()
        logger.exception(e)
        raise ValueError(f"Rolling back, cause : {str(e)}") from e
    finally:
        session.close()


@contextlib.contextmanager
def unit_api(attempt_message: str):
    session = Session(engine)
    try:
        yield session
        session.commit()

    except CannotCreateStillExistsException as e:
        session.rollback()
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{attempt_message} FAILED",
        )
    except UnauthorizedException as e:
        session.rollback()
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{attempt_message} FAILED",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        session.rollback()
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{attempt_message} FAILED",
        )
    finally:
        session.close()
