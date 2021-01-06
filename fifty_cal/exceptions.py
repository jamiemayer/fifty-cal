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
