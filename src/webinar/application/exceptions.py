class BaseAppError(Exception):
    pass


class NotFoundError(BaseAppError):
    pass


class NotFoundAdmin(NotFoundError):
    pass


class NotFoundUser(BaseAppError):
    pass


class NotFoundUsers(NotFoundUser):
    pass


class AdminCreated(BaseAppError):
    pass


class DuplicateWebinar(BaseAppError):
    pass
