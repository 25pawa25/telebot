from typing import List

from telebot import AdvancedCustomFilter, logger
from telebot.types import Message

from tgbot.models import UserRole, User
from tgbot.utils.database import Database


class HasRole(AdvancedCustomFilter):

    key = 'roles'

    @staticmethod
    def check(message: Message, roles: List[UserRole]):

        db: Database = Database.get_instance()
        try:
            with db.session.begin() as session:
                return session.query(User)\
                    .filter(User.user_name == message.from_user.username, User.user_role.in_(roles))\
                    .one_or_none() is not None
        except Exception as e:
            logger.error(f'Can\'t check user role. {e}')
            return False
