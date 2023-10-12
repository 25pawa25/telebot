from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, registry, sessionmaker
from telebot import logger

import tgbot.config as config

from tgbot.models.base import Base


class Database:
    """
    Database utils class
    """

    __instance = None

    def __init__(self):
        self.engine = create_engine(
            f'postgresql+psycopg2://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}/{config.POSTGRES_DATABASE}',
            echo=True
        )
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)

    @classmethod
    def get_instance(cls):
        """Return instance of Database class

        Returns:
            instance: _description_
        """
        if not cls.__instance:
            cls.__instance = Database()
        return cls.__instance

