from enum import Enum


class HomeWorkStatusType(str, Enum):
    ACCEPTED = "accepted"  # Принят
    UNDER_REVISION = "under_revision"  # На доработке
    UNDER_INSPECTION = "under_inspection"  # Нв рассмотрении


class EvaluationType(str, Enum):
    OK = "хорошо"
    COOL = "отлично"
