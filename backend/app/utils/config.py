from __future__ import annotations
from datetime import timedelta

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Config:
    TF_MODEL_NAME: str
    DB_CONNECTION_STRING: str
    COOKIES_KEY_NAME: str
    SESSION_TIME: timedelta
    JWT_SALT: str

    @staticmethod
    def _get_env_variable(name: str) -> str:
        value = getenv(name)
        if value is None:
            raise ValueError(f"{name} environment variable is not set")
        return value

    @staticmethod
    def get_config() -> Config:
        model_name = Config._get_env_variable("TF_MODEL_NAME")
        db_con_str: str = Config._get_env_variable("DB_CONNECTION_STRING")
        cookies_key = Config._get_env_variable("COOKIES_KEY")
        jwt_salt = Config._get_env_variable("JWT_SALT")

        session_time_seconds = int(Config._get_env_variable("SESSION_TIME_SECONDS"))
        session_time = timedelta(seconds=session_time_seconds)

        return Config(model_name, db_con_str, cookies_key, session_time, jwt_salt)


CONFIG = Config.get_config()
