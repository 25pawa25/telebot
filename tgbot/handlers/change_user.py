from telebot import TeleBot, logger
import base64
from telebot.types import Message, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardButton, CallbackQuery

from tgbot.decorator import log_message
from tgbot.handlers.dto.callback_data_dto import CallbackDataType
from tgbot.models import UserRole, Project, ChatState, TmpData, ProjectLink, ProjectState
from tgbot.models.dao.project_dao import ProjectDao
from tgbot.models.dao.state_dao import StateDao
from tgbot.models.dao.tmp_dao import TmpDao
from tgbot.models.dao.user_dao import UserDao
from tgbot.models.dao.participant_dao import ParticipantDao
from tgbot.utils.bot import state_step_check_callback_message, state_step_check_callback_query
from tgbot.utils.text_utils import extract_arg, describe_user_role
from tgbot.handlers.dto.change_user_dto import ChangeUserDto
from tgbot.models.user import User
import jsonpickle as jp
import json


CALLBACK_DATA = {
    'type': CallbackDataType.CHANGE_USER.value,
    'step': 1,
    'data': ''
}


def change_user_handler(bot: TeleBot):
    bot.register_message_handler(add_inline_roles,
                                 commands=['changeUser', 'ChangeUser', 'changeU'],
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])

    bot.register_callback_query_handler(add_inline_candidates,
                                        func=state_step_check_callback_query(ChatState.CHANGE_USER_STATE, 1),
                                        pass_bot=True,
                                        roles=[UserRole.ADMIN])

    bot.register_callback_query_handler(change_user,
                                        func=state_step_check_callback_query(ChatState.CHANGE_USER_STATE, 2),
                                        pass_bot=True,
                                        roles=[UserRole.ADMIN])


@log_message
def add_inline_roles(message: Message, bot: TeleBot):
    args = extract_arg(message.text)
    code = args[0]
    project = ProjectDao().get_by_code(code)

    if project is None:
        bot.reply_to(message, text='Такого проекта не найдено!')
        return

    if project.current_state.state == ProjectState.READY:
        bot.reply_to(message, text='Проект завершен!')
        return

    markup = InlineKeyboardMarkup(row_width=1)
    keyboard = []
    for user_role in UserRole:
        if user_role != UserRole.ADMIN:
            callback_data = {
                'type': CallbackDataType.CHANGE_USER.value,
                'data': TmpDao().add_data(ChangeUserDto(user_role))
            }
            keyboard.append(InlineKeyboardButton(describe_user_role(user_role),
                                                 callback_data=json.dumps(callback_data)))

    markup.add(*keyboard)

    StateDao().set_state(message.chat.id, ChatState.CHANGE_USER_STATE, 1, [TmpData(project)])
    bot.reply_to(message, 'Выберите роль:', reply_markup=markup)


def add_inline_candidates(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    state = StateDao().get_by_chat_id(call.message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(call.message, text='Что-то пошло не так %F0%9F%98%93')
        return

    tmp: TmpData = state.tmp_data[0]
    project = tmp.parsed_data

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

    user_dto: ChangeUserDto = jp.loads(data.data)
    old_participant = ParticipantDao().participants_filtered_by_role(user_dto.user_role, project.id).user
    candidates = UserDao().get_all_by_role([user_dto.user_role])
    markup = InlineKeyboardMarkup(row_width=1)
    keyboard = []

    if len(candidates) == 1:
        StateDao().reset_state(call.message.chat.id)
        bot.reply_to(call.message,
                     text='Пользователей не найдено.\nДля продолжения добавьте пользователя с данной ролью в систему')
        return

    for candidate in candidates:
        if candidate.user_name != old_participant.user_name:
            keyboard.append(InlineKeyboardButton(candidate.user_name,
                                                 callback_data=base64.b64encode(candidate.user_name.
                                                                                encode('utf-8')).decode('utf-8')))
    markup.add(*keyboard)
    StateDao().set_state(call.message.chat.id, ChatState.CHANGE_USER_STATE, 2, [TmpData(old_participant),
                                                                                TmpData(project)])
    bot.reply_to(call.message, 'Выберите кандидата:', reply_markup=markup)


def change_user(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    state = StateDao().get_by_chat_id(call.message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(call.message, text='Что-то пошло не так %F0%9F%98%93')
        return

    tmp: TmpData = state.tmp_data[0]
    old_participant = tmp.parsed_data
    temp: TmpData = state.tmp_data[1]
    project = temp.parsed_data
    new_participant = UserDao().get_by_username(base64.b64decode(call.data).decode('utf-8'))
    UserDao().change_participant(old_participant, new_participant, project)

    bot.edit_message_text('Участник изменен!', call.message.chat.id, call.message.id, reply_markup=None)
    StateDao().reset_state(call.message.chat.id)
