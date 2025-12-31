class AuthException(Exception):
    pass


class InvalidCredentialsException(AuthException):
    pass


class TokenExpiredException(AuthException):
    pass


class TokenInvalidException(AuthException):
    pass


class UserAlreadyExistsException(AuthException):
    pass


class UserNotFoundException(AuthException):
    pass


class InvalidInstrumentCodeError(Exception):
    pass