from typing import Annotated

from dishka.integrations.base import Depends

from webinar.application.interfaces.delete_message import TgDeleteMessage
from webinar.application.use_case.admin.read_admin_submit_user_question import ReadAdminSubmitUserQuestion
from webinar.application.use_case.homeworks.add_user_homework import AddUserHomeWork
from webinar.application.use_case.homeworks.read_user_homeworks import ReadUserHomeWorks
from webinar.application.use_case.homeworks.update_homework_status import UpdateHomeWorkStatus
from webinar.application.use_case.user.add_user import AddUserUseCase
from webinar.application.use_case.user.read_user_data import ReadUserData
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

ConfigDepends = Annotated[Config, Depends()]

TgDeleteMessageDepends = Annotated[TgDeleteMessage, Depends()]
