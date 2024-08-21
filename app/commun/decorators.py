import logging

logger = logging.getLogger(__name__)


def safe_execution(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            return None

    return wrapper
