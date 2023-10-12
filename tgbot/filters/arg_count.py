from typing import List

from telebot import AdvancedCustomFilter, logger
from telebot.types import Message

from tgbot.models import UserRole, User
from tgbot.utils.database import Database
from tgbot.utils.text_utils import extract_arg


class ArgCount(AdvancedCustomFilter):

    key = 'num_args'

    @staticmethod
    def check(message: Message, num_args: int):
        return len(extract_arg(message.text)) == num_args
