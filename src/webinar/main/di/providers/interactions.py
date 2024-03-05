from dishka import provide, Provider, Scope

from webinar.application.interactions.admin.read_admin_by_letters_range import (
    ReadAdminByLettersRange,
    ReadAdminByLettersRangeImpl,
)
from webinar.application.interactions.admin.read_random_admin import ReadRandomAdmin, ReadRandomAdminImpl


class InteractionsProvider(Provider):
    scope = Scope.REQUEST
    
    read_admin_by_letters_range = provide(
        source=ReadAdminByLettersRangeImpl,
        provides=ReadAdminByLettersRange
    )
    read_random_admin = provide(
        source=ReadRandomAdminImpl,
        provides=ReadRandomAdmin
    )
