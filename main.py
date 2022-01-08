import logging

from aiogram.utils.executor import Executor

from bot_app.start_bot import init_bot, start_bot
from bot_app.conversation.handlers.init_handlers import init_handlers
from bot_app.dialogs.buttons import DbButtons
from bot_app.tools.text_handler import UserTextParser

from db.db_data_handler import DbDataHandler
from db.db_functions import DbFunctions

from environment import init_environment
from redis_repository.redis import init_redis
from redis_repository.redis_repository import RedisRepository


def start_app():
    logging.basicConfig(level=20, format='[%(asctime)s: %(name)s: %(levelname)s] %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    environment = init_environment()
    bot, dispatcher = init_bot(environment)
    executor = Executor(dispatcher)

    async def on_startup(*_, **__):

        db = DbFunctions()
        db_buttons = DbButtons(dbf=db)
        ut_parser = UserTextParser()
        db_data_handler = DbDataHandler(db=db)
        redis = await init_redis(environment=environment)
        redis_repository = RedisRepository(redis=redis)
        init_handlers(dp=dispatcher, db=db, redis_repository=redis_repository,
                      _env=environment, db_buttons=db_buttons, db_data_handler=db_data_handler,
                      ut_parser=ut_parser)

    async def on_shutdown(*_, **__):
        pass

    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)
    start_bot(executor=executor, environment=environment)


if __name__ == '__main__':
    start_app()
