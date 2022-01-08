from environs import Env


class Environment:

    def __init__(self, _env: Env):
        self.telegram_token = _env("TELEGRAM_TOKEN")
        self.redis_host = _env.str('REDIS_HOST', 'localhost')
        self.redis_port = _env.str('REDIS_PORT', '6379')
        self.re_for_date_text_parse = _env('RE_FOR_DATE_LETTERS', '')

    @property
    def redis_uri(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"


def init_environment() -> Environment:
    env = Env()
    env.read_env()
    return Environment(_env=env)
