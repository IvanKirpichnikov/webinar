class BaseAppError(Exception):
    pass


class NotFoundError(BaseAppError):
    pass


class NotFoundAdmin(NotFoundError):
    pass


class NotFoundHomeworks(BaseAppError):
    pass


class NotFoundUser(NotFoundError):
    pass


class NotFoundUsers(NotFoundUser):
    pass


class NotFoundWebinars(NotFoundError):
    pass


class AdminCreated(BaseAppError):
    pass


class DuplicateWebinar(BaseAppError):
    pass
