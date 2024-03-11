from typing import Annotated

from dishka.integrations.base import Depends

from webinar.application.interfaces.delete_message import TgDeleteMessage
from webinar.application.use_case.admin.create import CreateAdmin
from webinar.application.use_case.admin.read_admin_submit_user_question import \
    ReadAdminSubmitUserQuestion
from webinar.application.use_case.admin.read_all_by_direction_training import \
    ReadAllAdminByDirectionTraining
from webinar.application.use_case.admin.read_data_by_tg_user_id import ReadAdminDataByTgUserId
from webinar.application.use_case.homeworks.add_user_homework import AddUserHomeWork
from webinar.application.use_case.homeworks.read_and_user_info_by_db_id import \
    ReadHomeworkAndUserInfoByDBId
from webinar.application.use_case.homeworks.read_for_pagination import \
    ReadUserHomeworksForPagination
from webinar.application.use_case.homeworks.read_user_homeworks import ReadUserHomeWorks
from webinar.application.use_case.homeworks.update_assessment_and_status import \
    UpdateHomeworkEvolutionAndStatus
from webinar.application.use_case.homeworks.update_homework_status import UpdateHomeWorkStatus
from webinar.application.use_case.user.add_user import AddUserUseCase
from webinar.application.use_case.user.read_user_data import ReadUserData
from webinar.application.use_case.webinars.create import CreateWebinar
from webinar.application.use_case.webinars.get_pagination import GetPaginationWebinars
from webinar.config import Config


# --> UseCase Depends <--
AddUserUseCaseDepends = Annotated[AddUserUseCase, Depends()]
AddUserHomeWorkDepends = Annotated[AddUserHomeWork, Depends()]
GetPaginationWebinarsDepends = Annotated[GetPaginationWebinars, Depends()]
ReadUserHomeWorksDepends = Annotated[ReadUserHomeWorks, Depends()]
UpdateHomeWorkStatusDepends = Annotated[UpdateHomeWorkStatus, Depends()]
ReadUserDataDepends = Annotated[ReadUserData, Depends()]
ReadAdminSubmitUserQuestionDepends = Annotated[ReadAdminSubmitUserQuestion, Depends()]
ReadAllAdminByDirectionTrainingDepends = Annotated[ReadAllAdminByDirectionTraining, Depends()]
CreateAdminDepends = Annotated[CreateAdmin, Depends()]
CreateWebinarDepends = Annotated[CreateWebinar, Depends()]
ReadAdminDataByTgUserIdDepends = Annotated[ReadAdminDataByTgUserId, Depends()]
ReadUserHomeworksForPaginationDepends = Annotated[ReadUserHomeworksForPagination, Depends()]
ReadHomeworkAndUserInfoByDBIdDepends = Annotated[ReadHomeworkAndUserInfoByDBId, Depends()]
UpdateHomeworkEvolutionAndStatusDepends = Annotated[UpdateHomeworkEvolutionAndStatus, Depends()]

ConfigDepends = Annotated[Config, Depends()]

TgDeleteMessageDepends = Annotated[TgDeleteMessage, Depends()]
