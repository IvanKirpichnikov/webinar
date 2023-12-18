from aiogram import Router

from .user import routing as user
from .admin import routing as admin
from ..filtering.check_user_is_admin import CheckUserIsAdminRegisteringFilterImpl


route = Router()
a_r = admin.route
f = CheckUserIsAdminRegisteringFilterImpl()
a_r.message.filter(f)
a_r.callback_query.filter(f)

route.include_routers(user.route, a_r)
