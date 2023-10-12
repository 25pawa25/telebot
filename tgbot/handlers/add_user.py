import json
from typing import Dict

from telebot import TeleBot, logger
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from tgbot.decorator import log_message
from tgbot.handlers.dto.callback_data_dto import CallbackDataDto, CallbackDataType
from tgbot.handlers.dto.user_add_dto import UserAddDto
from tgbot.models import UserRole
from tgbot.models.dao.tmp_dao import TmpDao
from tgbot.models.dao.user_dao import UserDao
from tgbot.utils.text_utils import extract_arg, describe_user_role

import jsonpickle as jp
from base64 import b85encode, b85decode

CALLBACK_SEPARATOR = '|'


def register_user_add_handler(bot: TeleBot):
    bot.register_message_handler(add_user,
                                 commands=['addUser', 'newUser', 'user'],
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])
    bot.register_callback_query_handler(add_user_callback,
                                        func=callback_filter,
                                        pass_bot=True)


def callback_filter(call: CallbackQuery) -> bool:
    if not call.data:
        return False
    try:
        callback_data = json.loads(call.data)
        return callback_data['type'] == CallbackDataType.USER_ADD.value
    except Exception as e:
        logger.error(e)
        return False


@log_message
def add_user(message: Message, bot: TeleBot):
    args = extract_arg(message.text)
    markup = InlineKeyboardMarkup(row_width=2)
    keyboard = []
    for role in UserRole:
        callback_data = {
            'type': CallbackDataType.USER_ADD.value,
            'data': TmpDao().add_data(UserAddDto(args[0], role))
        }
        keyboard.append(InlineKeyboardButton(describe_user_role(role),
                                             callback_data=json.dumps(callback_data)))
    markup.add(*keyboard)
    bot.reply_to(message, 'Выберите роль:', reply_markup=markup)


def add_user_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: Dict = json.loads(call.data)
    if callback_data.get('data') is None:
        logger.error(f'Can\'t get tmp data for {call.from_user.username} from callback!')
        bot.edit_message_text('Что-то пошло не так!', call.message.chat.id, call.message.id, reply_markup=None)
        return

    data = TmpDao().get(callback_data.get('data'))
    if data is None:
        logger.error(f'Can\'t get tmp data for {call.from_user.username} request! TmpData id: {callback_data.get("data")}')
        bot.edit_message_text('Что-то пошло не так!', call.message.chat.id, call.message.id, reply_markup=None)
        return

    user_dto: UserAddDto = jp.loads(data.data)
    if UserDao().get_by_username(user_dto.username) is not None:
        bot.edit_message_text(f'Пользователь {user_dto.username} уже есть в базе!',
                              call.message.chat.id,
                              call.message.id,
                              reply_markup=None)
        return

    UserDao().add_user(user_dto.username, UserRole.value_of(user_dto.role))
    bot.edit_message_text('Пользователь добавлен!', call.message.chat.id, call.message.id, reply_markup=None)
