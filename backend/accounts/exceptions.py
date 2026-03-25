from rest_framework.exceptions import APIException


class UnauthorizedException(APIException):
    status_code = 401
    default_detail = "Unauthorized."
    default_code = "unauthorized"


class ForbiddenException(APIException):
    status_code = 403
    default_detail = "Forbidden."
    default_code = "forbidden"


class InvalidCredentialsException(APIException):
    status_code = 401
    default_detail = "Invalid credentials."
    default_code = "invalid_credentials"


class UserAlreadyExistsException(APIException):
    status_code = 409
    default_detail = "User already exists."
    default_code = "user_already_exists"

