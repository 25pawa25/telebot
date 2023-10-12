import sys
from functools import wraps
from telebot import logger
from telebot.types import Message


def log_message(func):
    @wraps(func)
    def log_decorator_wrapper(message: Message, *args, **kwargs):
        logger.info(f'User {message.from_user.username} called "{func.__name__}" ')
        try:
            value = func(message, *args, **kwargs)
        except:
            logger.error(f"Exception: {str(sys.exc_info()[1])}")
            raise

        return value

    return log_decorator_wrapper
