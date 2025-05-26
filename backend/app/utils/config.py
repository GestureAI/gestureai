from __future__ import annotations
from datetime import timedelta

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Config:
    TF_MODEL_PATH: str
    DB_CONNECTION_STRING: str
    COOKIES_KEY_NAME: str
    SESSION_TIME: timedelta
    JWT_SALT: str

    @staticmethod
    def get_config() -> Config:
        model_path = getenv("TF_MODEL_PATH")
        db_con_str: str = getenv("DB_CONNECTION_STRING", "sqlite:///./app.db")
        cookies_key = getenv("COOKIES_KEY_NAME", "session")
        session_time_seconds = int(getenv("SESSION_TIME_SECONDS", 3600))
        session_time = timedelta(seconds=session_time_seconds)
        hash_salt = getenv("HASH_SALT", "default_salt")

        if model_path is None:
            raise ValueError("TF_MODEL_PATH is not set")

        return Config(model_path, db_con_str, cookies_key, session_time, hash_salt)


CONFIG = Config.get_config()
