from envparse import Env
from kw.structlog_config.config import configure_stdlib_logging, configure_structlog

env = Env()

DEBUG = env("DEBUG", default=False, cast=bool)

configure_structlog(DEBUG, timestamp_format="iso")
configure_stdlib_logging(DEBUG, timestamp_format="iso")

DATABASE_URL = env("DATABASE_URL")
SECRET_KEY = env("SECRET_KEY", default="lobobo-bobo-koko")
