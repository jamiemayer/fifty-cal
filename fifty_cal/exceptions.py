class FiftyCalException(Exception):
    """
    Base Exception.
    """


class SessionException(FiftyCalException):
    """
    Exceptions relating to the user session.
    """


class UnableToLogoutException(SessionException):
    """
    Unable to log out of the current session.
    """


class CalendarException(FiftyCalException):
    """
    Base Exception for uploading/downloading calendar file.
    """


class UnauthorizedException(CalendarException):
    """
    Access Denied - Auth.

    Thrown when a http 403 status code is returned.
    """


class NotFoundException(CalendarException):
    """
    Resource not found.

    Thrown when a HTTP status code of 404 returned
    """


class ServerErrorException(CalendarException):
    """
    Server side error.

    Thrown when a HTTP status of code 500 is returned
    """


class HttpErrorException(CalendarException):
    """
    Catch all for HTTP Response codes that do not have explicit exceptions defined.
    """


class ArgumentConflictException(CalendarException):
    """
    Optional arguments passed to Command conflict.
    """