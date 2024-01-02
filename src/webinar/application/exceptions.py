class BaseAppError(Exception):
    pass


class DuplicateWebinar(BaseAppError):
    pass


class NotFoundAdmin(BaseAppError):
    pass


class NotFoundHomeworks(BaseAppError):
    pass


class NotFoundWebinars(BaseAppError):
    pass


class NotFoundUsers(BaseAppError):
    pass


class AdminCreated(BaseAppError):
    pass
