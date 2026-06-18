class BaseAuthServiceError(Exception):
    pass


class UserAlreadyExistsError(BaseAuthServiceError):
    pass


class UserNotFoundError(BaseAuthServiceError):
    pass


class InvalidCredentialsError(BaseAuthServiceError):
    pass


class InvalidTokenOrExpiredTokenError(BaseAuthServiceError):
    pass


class RoleNotFoundError(BaseAuthServiceError):
    pass


class UserOrRoleNotFoundError(BaseAuthServiceError):
    pass


class RoleAlreadyAssignedError(BaseAuthServiceError):
    pass


class RoleAlreadyExistsError(BaseAuthServiceError):
    pass


class AccessDeniedError(BaseAuthServiceError):
    pass
