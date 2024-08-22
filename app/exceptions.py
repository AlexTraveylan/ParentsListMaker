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


# API Exception


class APIException(ParentsListMakerException):
    pass


class UnauthorizedException(APIException):
    pass


class CannotCreateStillExistsException(APIException):
    pass


class RessourceNotFoundException(APIException):
    pass
