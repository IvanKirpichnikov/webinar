from dishka import provide, Provider, Scope

from webinar.application.use_case.admin.read_admin_submit_user_question import (
    ReadAdminSubmitUserQuestion,
    ReadAdminSubmitUserQuestionImpl,
)
from webinar.application.use_case.homeworks.add_user_homework import AddUserHomeWork, AddUserHomeWorkImpl
from webinar.application.use_case.homeworks.read_user_homeworks import ReadUserHomeWorks, ReadUserHomeWorksImpl
from webinar.application.use_case.homeworks.update_homework_status import UpdateHomeWorkStatus, UpdateHomeWorkStatusImpl
from webinar.application.use_case.user.add_user import AddUserUseCase, AddUserUseCaseImpl
from webinar.application.use_case.user.read_user_data import ReadUserData, ReadUserDataImpl
from webinar.application.use_case.webinars.get_pagination import GetPaginationWebinars, GetPaginationWebinarsImpl


class UseCaseProvider(Provider):
    scope = Scope.REQUEST
    
    add_user = provide(
        source=AddUserUseCaseImpl,
        provides=AddUserUseCase,
    )
    get_pagination_webinars = provide(
        source=GetPaginationWebinarsImpl,
        provides=GetPaginationWebinars,
    )
    read_user_homeworks = provide(
        source=ReadUserHomeWorksImpl,
        provides=ReadUserHomeWorks,
    )
    add_user_homework = provide(
        source=AddUserHomeWorkImpl,
        provides=AddUserHomeWork,
    )
    update_homework_status = provide(
        source=UpdateHomeWorkStatusImpl,
        provides=UpdateHomeWorkStatus,
    )
    read_user_data = provide(
        source=ReadUserDataImpl,
        provides=ReadUserData,
    )
    read_admin_submit_user_question = provide(
        source=ReadAdminSubmitUserQuestionImpl,
        provides=ReadAdminSubmitUserQuestion,
    )
