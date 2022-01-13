from aiogram.dispatcher import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from bot_app.conversation.handlers.authorization_handler import init_common_handlers
from bot_app.conversation.handlers.aim_create_handler import init_aim_create_handler
from bot_app.conversation.handlers.task_create_handler import init_task_create_handler
from bot_app.conversation.handlers.notifier_handler import init_notifier_handler
from bot_app.dialogs.buttons import DbButtons, NotifierButtons
from db.db_functions import DbFunctions
from db.db_data_handler import DbDataHandler
from bot_app.tools.text_handler import UserTextParser

from redis_repository.redis_repository import RedisRepository
from middlewares.authentication import AuthenticationMiddleware
from environment import Environment


def init_handlers(dp: Dispatcher, db: DbFunctions, db_data_handler: DbDataHandler,
                  db_buttons: DbButtons, ut_parser: UserTextParser, notifier_buttons: NotifierButtons,
                  redis_repository: RedisRepository, _env: Environment):

    dp.middleware.setup(LoggingMiddleware())
    dp.middleware.setup(AuthenticationMiddleware(redis_repository=redis_repository))

    init_common_handlers(dp=dp, db=db, _env=_env, redis=redis_repository)
    init_aim_create_handler(dp=dp, db=db, db_data_handler=db_data_handler)
    init_task_create_handler(dp=dp, db=db, db_data_handler=db_data_handler,
                             db_buttons=db_buttons, ut_parser=ut_parser)
    init_notifier_handler(dp=dp, db=db, db_buttons=db_buttons, db_data_handler=db_data_handler)
