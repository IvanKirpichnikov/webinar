from dishka import provide, Provider, Scope

from webinar.application.use_case.admin.create import CreateAdmin, CreateAdminImpl
from webinar.application.use_case.admin.read_admin_submit_user_question import (
    ReadAdminSubmitUserQuestion,
    ReadAdminSubmitUserQuestionImpl,
)
from webinar.application.use_case.admin.read_all_by_direction_training import \
    (
    ReadAllAdminByDirectionTraining, ReadAllAdminByDirectionTrainingImpl,
)
from webinar.application.use_case.admin.read_data_by_tg_user_id import (
    ReadAdminDataByTgUserId,
    ReadAdminDataByTgUserIdImpl,
)
from webinar.application.use_case.get_stats import GetStats, GetStatsImpl
from webinar.application.use_case.homeworks.add_user_homework import AddUserHomeWork, AddUserHomeWorkImpl
from webinar.application.use_case.homeworks.delete_by_db_id import (
    DeleteHomeworkByDbId,
    DeleteHomeworkByDbIdImpl,
)
from webinar.application.use_case.homeworks.read_and_user_info_by_db_id import \
    (
    ReadHomeworkAndUserInfoByDBId, ReadHomeworkAndUserInfoByDBIdImpl,
)
from webinar.application.use_case.homeworks.read_for_pagination import \
    (
    ReadUserHomeworksForPagination, ReadUserHomeworksForPaginationImpl,
)
from webinar.application.use_case.homeworks.read_user_homeworks import ReadUserHomeWorks, ReadUserHomeWorksImpl
from webinar.application.use_case.homeworks.update_assessment_and_status import \
    (
    UpdateHomeworkEvolutionAndStatus, UpdateHomeworkEvolutionAndStatusImpl,
)
from webinar.application.use_case.homeworks.update_homework_status import UpdateHomeWorkStatus, UpdateHomeWorkStatusImpl
from webinar.application.use_case.homeworks.update_homework_type_and_comment import \
    (
    UpdateHomeWorkTypeAndComment, UpdateHomeWorkTypeAndCommentImpl,
)
from webinar.application.use_case.user.add_user import AddUserUseCase, AddUserUseCaseImpl
from webinar.application.use_case.user.delete_user import DeleteUserByEmail, DeleteUserByEmailImpl
from webinar.application.use_case.user.exists import UserIsExists, UserIsExistsImpl
from webinar.application.use_case.user.is_admin import UserIsAdmin, UserIsAdminImpl
from webinar.application.use_case.user.read_user_data import ReadUserData, ReadUserDataImpl
from webinar.application.use_case.webinars.create import CreateWebinar, CreateWebinarImpl
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
    read_admins_by_dt = provide(
        source=ReadAllAdminByDirectionTrainingImpl,
        provides=ReadAllAdminByDirectionTraining,
    )
    create_admin = provide(
        source=CreateAdminImpl,
        provides=CreateAdmin,
    )
    create_webinar = provide(
        source=CreateWebinarImpl,
        provides=CreateWebinar
    )
    read_admin_data_by_tg_user_id = provide(
        source=ReadAdminDataByTgUserIdImpl,
        provides=ReadAdminDataByTgUserId,
    )
    read_homeworks_for_pagination = provide(
        source=ReadUserHomeworksForPaginationImpl,
        provides=ReadUserHomeworksForPagination
    )
    read_homework__and_user_info_by_db_id = provide(
        source=ReadHomeworkAndUserInfoByDBIdImpl,
        provides=ReadHomeworkAndUserInfoByDBId
    )
    update_homework_en = provide(
        source=UpdateHomeworkEvolutionAndStatusImpl,
        provides=UpdateHomeworkEvolutionAndStatus
    )
    update_homework_type_and_comm = provide(
        source=UpdateHomeWorkTypeAndCommentImpl,
        provides=UpdateHomeWorkTypeAndComment
    )
    get_stats = provide(
        source=GetStatsImpl,
        provides=GetStats
    )
    user_is_admin = provide(
        source=UserIsAdminImpl,
        provides=UserIsAdmin
    )
    user_exists = provide(
        source=UserIsExistsImpl,
        provides=UserIsExists
    )
    delete_user_by_email = provide(
        source=DeleteUserByEmailImpl,
        provides=DeleteUserByEmail
    )
    delete_homework_by_db_id = provide(
        source=DeleteHomeworkByDbIdImpl,
        provides=DeleteHomeworkByDbId
    )
