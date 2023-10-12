from telebot import TeleBot, logger
import base64
import jsonpickle as jp
import json
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
from tgbot.utils.text_utils import extract_arg, describe_project_state
from tgbot.handlers.dto.change_state_dto import ChangeStateDto


CALLBACK_DATA = {
    'type': CallbackDataType.PROJECT_ADD.value,
    'step': 1,
    'data': ''
}


def change_project_state_handler(bot: TeleBot):

    bot.register_message_handler(add_inline_states,
                                 commands=['changeState', 'changeS'],
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN, UserRole.DESIGNER, UserRole.DEVELOPER])

    bot.register_callback_query_handler(change_state,
                                        func=state_step_check_callback_query(ChatState.PROJECT_CHANGE_STATE, 1),
                                        pass_bot=True,
                                        roles=[UserRole.ADMIN, UserRole.DESIGNER, UserRole.DEVELOPER])


def callback_filter(call: CallbackQuery) -> bool:
    if not call.data:
        return False
    try:
        callback_data = json.loads(call.data)
        return callback_data['type'] == CallbackDataType.CHANGE_STATE.value
    except Exception as e:
        logger.error(e)
        return False


def change_next_state(message: Message, bot, project, current):
    states = list(ProjectState)
    for state in range(len(states)):
        if states[state] == current:
            ProjectDao().change_state(project.id, states[state+1])
            StateDao().reset_state(message.chat.id)
            break
    return


@log_message
def add_inline_states(message: Message, bot: TeleBot):
    args = extract_arg(message.text)
    code = args[0]
    project = ProjectDao().get_by_code(code)

    if project is None:
        bot.reply_to(message, text='Такого проекта не найдено!')
        return

    project_state = project.current_state.state

    if project_state == ProjectState.READY:
        bot.reply_to(message, text='Проект завершен!')
        return

    markup = InlineKeyboardMarkup(row_width=1)
    keyboard = []
    user_id = UserDao().get_by_username(message.from_user.username).id
    user = ParticipantDao().participants_filtered(user_id, project.id)
    bot.reply_to(message, text=f'Текущий статус проекта: {describe_project_state(project_state)}')

    if user is None:
        bot.reply_to(message, text='Вы не участник проекта!')
        return

    elif user.role == UserRole.ADMIN:
        for state in ProjectState:
            if state != project_state:
                callback_data = {
                    'type': CallbackDataType.CHANGE_USER.value,
                    'data': TmpDao().add_data(ChangeStateDto(state))
                }
                keyboard.append(InlineKeyboardButton(describe_project_state(state),
                                                     callback_data=json.dumps(callback_data)))

    elif user.role == UserRole.DESIGNER:
        if project_state == ProjectState.DEVELOPMENT_DESIGN:
            callback_data = {
                'type': CallbackDataType.CHANGE_STATE.value,
                'data': TmpDao().add_data(ChangeStateDto(ProjectState.DEVELOPMENT_DESIGN))
            }
            keyboard.append(InlineKeyboardButton(describe_project_state(ProjectState.DESIGN_AGREEMENT),
                                                 callback_data=json.dumps(callback_data)))

        else:
            bot.reply_to(message, text='Статус проекта не разработка:дизайн!')
            return

    elif user.role == UserRole.DEVELOPER:
        if project_state == ProjectState.DEVELOPMENT_LAYOUT:
            callback_data = {
                'type': CallbackDataType.CHANGE_STATE.value,
                'data': TmpDao().add_data(ChangeStateDto(ProjectState.DEVELOPMENT_LAYOUT))
            }
            keyboard.append(InlineKeyboardButton(describe_project_state(ProjectState.DEVELOPMENT_LAYOUT),
                                                 callback_data=json.dumps(callback_data)))


        else:
            bot.reply_to(message, text='Статус проекта не разработка:вёрстка!')
            return

    else:
        bot.reply_to(message, text='Ваша роль не соответствует требованиям!')
        return

    markup.add(*keyboard)

    StateDao().set_state(message.chat.id, ChatState.PROJECT_CHANGE_STATE, 1, [TmpData(project), TmpData(project_state)])
    bot.reply_to(message, 'Выберите статус проекта:', reply_markup=markup)


def change_state(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    chat_state = StateDao().get_by_chat_id(call.message.chat.id)
    if chat_state.tmp_data is None or len(chat_state.tmp_data) == 0:
        bot.reply_to(call.message, text='Что-то пошло не так %F0%9F%98%93')
        return

    tmp: TmpData = chat_state.tmp_data[0]
    project = tmp.parsed_data
    temp: TmpData = chat_state.tmp_data[1]
    project_state = temp.parsed_data
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

    state_dto: ChangeStateDto = jp.loads(data.data)
    if state_dto.state == ProjectState.NEXT:
        change_next_state(call.message, bot, project, project_state)
        bot.edit_message_text('Статус изменен!', call.message.chat.id, call.message.id, reply_markup=None)
        return

    ProjectDao().change_state(project.id, state_dto.state)
    StateDao().reset_state(call.message.chat.id)
    bot.edit_message_text('Статус изменен!', call.message.chat.id, call.message.id, reply_markup=None)