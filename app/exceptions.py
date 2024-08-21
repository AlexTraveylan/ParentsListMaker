# Général Exception


class ParentsListMakerException(Exception):
    pass


# Database Exception


class DatabaseException(ParentsListMakerException):
    pass


class NotUniqueException(DatabaseException):
    pass


class NotFoundException(DatabaseException):
    pass
