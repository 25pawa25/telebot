from telebot import TeleBot
from telebot.types import Message

from tgbot.decorator import log_message
from tgbot.models import UserRole
from tgbot.models.dao.state_dao import StateDao


def add_reset_handler(bot: TeleBot):
    bot.register_message_handler(reset_state,
                                 commands=['reset'],
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])
    bot.register_message_handler(show_state,
                                 commands=['state'],
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])


@log_message
def reset_state(message: Message, bot: TeleBot):
    StateDao().reset_state(message.chat.id)
    bot.reply_to(message, 'Цепочка команд отменена!')


@log_message
def show_state(message: Message, bot: TeleBot):
    current_state = StateDao().get_by_chat_id(message.chat.id)
    if current_state is None:
        bot.reply_to(message, 'Состояние чата не установлено!')
        return
    bot.reply_to(message, f'Текущее состояние {current_state.state.name}, шаг {current_state.step}')
