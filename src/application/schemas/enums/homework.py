from enum import Enum


class HomeWorkTypeEnum(str, Enum):
    ACCEPTED = 'accepted'
    UNDER_REVISION = 'under_revision'
    UNDER_INSPECTION = 'under_inspection'
