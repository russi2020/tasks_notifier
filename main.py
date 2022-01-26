import logging.config
import logging
from os import path

from aiogram.utils.executor import Executor

from bot_app.start_bot import init_bot, start_bot
from bot_app.conversation.handlers.init_handlers import init_handlers
from bot_app.dialogs.buttons import DbButtons, NotifierButtons
from bot_app.tools.text_handler import UserTextParser

from db.db_data_handler import DbDataHandler
from db.db_functions import DbFunctions

from environment import init_environment
from redis_repository.redis import init_redis
from redis_repository.redis_repository import RedisRepository


def start_app():
    log_file_path = path.join(path.dirname(path.abspath("__file__")), 'logging.ini')
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.info("Starting app")

    environment = init_environment()
    bot, dispatcher = init_bot(environment)
    executor = Executor(dispatcher)

    async def on_startup(*_, **__):

        db = DbFunctions()
        db_buttons = DbButtons(dbf=db)
        notifier_buttons = NotifierButtons()
        ut_parser = UserTextParser()
        db_data_handler = DbDataHandler(db=db)
        redis = await init_redis(environment=environment)
        redis_repository = RedisRepository(redis=redis)
        init_handlers(dp=dispatcher, db=db, redis_repository=redis_repository,
                      _env=environment, db_buttons=db_buttons, db_data_handler=db_data_handler,
                      ut_parser=ut_parser, notifier_buttons=notifier_buttons)

    async def on_shutdown(*_, **__):
        pass

    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)
    start_bot(executor=executor, environment=environment)


if __name__ == '__main__':
    start_app()
