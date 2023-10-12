from telebot import TeleBot
from telebot.types import Message

from tgbot.decorator import log_message
from tgbot.utils.database import Database


@log_message
def admin_user(message: Message, bot: TeleBot):
    """
    You can create a function and use parameter pass_bot.
    """

    db: Database = Database.get_instance()
    bot.send_message(message.chat.id, "Hello, admin!")