import base64
import re
from datetime import datetime

from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardButton, CallbackQuery

from tgbot.decorator import log_message
from tgbot.handlers.dto.callback_data_dto import CallbackDataType
from tgbot.models import UserRole, Project, ChatState, TmpData, ProjectLink, ProjectState
from tgbot.models.dao.project_dao import ProjectDao
from tgbot.models.dao.state_dao import StateDao
from tgbot.models.dao.tmp_dao import TmpDao
from tgbot.models.dao.user_dao import UserDao
from tgbot.models.link_type import LinkType
from tgbot.utils.bot import state_step_check_callback_message, state_step_check_callback_query
from tgbot.utils.text_utils import extract_arg

CALLBACK_DATA = {
    'type': CallbackDataType.PROJECT_ADD.value,
    'step': 1,
    'data': ''
}


def register_project_add_handler(bot: TeleBot):
    bot.register_message_handler(add_project_price_step,
                                 commands=['addProject', 'newProject', 'project'],
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])
    bot.register_message_handler(add_project_deadline_step,
                                 func=state_step_check_callback_message(ChatState.PROJECT_CREATE_STATE, 1),
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])
    bot.register_message_handler(add_project_manager_step,
                                 func=state_step_check_callback_message(ChatState.PROJECT_CREATE_STATE, 2),
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])
    bot.register_callback_query_handler(add_project_designer_step,
                                        func=state_step_check_callback_query(ChatState.PROJECT_CREATE_STATE, 3),
                                        pass_bot=True,
                                        roles=[UserRole.ADMIN])
    bot.register_callback_query_handler(add_project_developer_step,
                                        func=state_step_check_callback_query(ChatState.PROJECT_CREATE_STATE, 4),
                                        pass_bot=True,
                                        roles=[UserRole.ADMIN])
    bot.register_callback_query_handler(add_project_figma_step,
                                        func=state_step_check_callback_query(ChatState.PROJECT_CREATE_STATE, 5),
                                        pass_bot=True,
                                        roles=[UserRole.ADMIN])
    bot.register_message_handler(add_project_tilda_step,
                                 func=state_step_check_callback_message(ChatState.PROJECT_CREATE_STATE, 6),
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])
    bot.register_message_handler(add_project_tilda_creds_step,
                                 func=state_step_check_callback_message(ChatState.PROJECT_CREATE_STATE, 7),
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])
    bot.register_message_handler(add_project_final_step,
                                 func=state_step_check_callback_message(ChatState.PROJECT_CREATE_STATE, 8),
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])


@log_message
def add_project_price_step(message: Message, bot: TeleBot):
    args = extract_arg(message.text)
    project = Project.new()
    project.name = args[0]
    project.code = args[1]
    StateDao().set_state(message.chat.id, ChatState.PROJECT_CREATE_STATE, 1, [TmpData(project)])
    bot.reply_to(message,
                 'Отлично! Введите стоимость проекта. \nЕсли не хотите указывать стоимость, то напишите "Нет".')


def add_project_deadline_step(message: Message, bot: TeleBot):
    state = StateDao().get_by_chat_id(message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(message, text='Что-то пошло не так %F0%9F%98%93')
        return
    tmp: TmpData = state.tmp_data[0]
    project = tmp.parsed_data
    project.price = re.sub('[^0-9,.]', '', message.text)
    StateDao().set_state(message.chat.id, ChatState.PROJECT_CREATE_STATE, 2, [TmpData(project)])
    bot.reply_to(message, text='Омг. Как дорого! :flushed: :flushed: :flushed:\n'
                               'Перейдем к следующему шагу.\n'
                               'Введите дедлайн проекта в формате дд.мм.гггг:')


def add_project_manager_step(message: Message, bot: TeleBot):
    state = StateDao().get_by_chat_id(message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(message, text='Что-то пошло не так %F0%9F%98%93')
        return
    tmp: TmpData = state.tmp_data[0]
    project = tmp.parsed_data
    project.deadline = datetime.strptime(re.sub('[^0-9.]', '', message.text), '%d.%m.%Y')
    markup = InlineKeyboardMarkup()
    keyboard = []
    managers = UserDao().get_all_by_role([UserRole.ADMIN, UserRole.MANAGER])
    for manager in managers:
        keyboard.append(InlineKeyboardButton(manager.user_name,
                                             callback_data=base64.b64encode(manager.user_name.encode('utf-8')).decode('utf-8')))
    markup.add(*keyboard)
    StateDao().set_state(message.chat.id, ChatState.PROJECT_CREATE_STATE, 3, [TmpData(project)])
    bot.reply_to(message,
                 text='Надеюсь успеем!\n'
                 'Перейдем к следующему шагу.\n'
                 'Выберите руководителя проекта:',
                 reply_markup=markup)


def add_project_designer_step(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    state = StateDao().get_by_chat_id(call.message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(call.message, text='Что-то пошло не так %F0%9F%98%93')
        return
    tmp: TmpData = state.tmp_data[0]
    project = tmp.parsed_data
    project.add_participant(UserDao().get_by_username(base64.b64decode(call.data).decode('utf-8')), UserRole.MANAGER)
    markup = InlineKeyboardMarkup()
    keyboard = []
    designers = UserDao().get_all_by_role([UserRole.DESIGNER])
    if len(designers) == 0:
        StateDao().reset_state(call.message.chat.id)
        bot.reply_to(call.message,
                     text='Дизайнеров не найдено.\nДля продолжения добавте разработчика в систему')
        return
    for designer in designers:
        keyboard.append(InlineKeyboardButton(designer.user_name,
                                             callback_data=base64.b64encode(designer.user_name.encode('utf-8')).decode('utf-8')))
    markup.add(*keyboard)
    StateDao().set_state(call.message.chat.id, ChatState.PROJECT_CREATE_STATE, 4, [TmpData(project)])
    bot.reply_to(call.message,
                 text='Я бы назначил этого парня депутатом!\n'
                      'Перейдем к следующему шагу.\n'
                      'Выберите дизайнера проекта:',
                 reply_markup=markup)


def add_project_developer_step(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    state = StateDao().get_by_chat_id(call.message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(call.message, text='Что-то пошло не так %F0%9F%98%93')
        return
    tmp: TmpData = state.tmp_data[0]
    project = tmp.parsed_data
    project.add_participant(UserDao().get_by_username(base64.b64decode(call.data).decode('utf-8')), UserRole.DESIGNER)
    markup = InlineKeyboardMarkup()
    keyboard = []
    developers = UserDao().get_all_by_role([UserRole.DEVELOPER])
    if len(developers) == 0:
        StateDao().reset_state(call.message.chat.id)
        bot.reply_to(call.message,
                     text='Разработчиков не найдено.\nДля продолжения добавте разработчика в систему')
        return
    for developer in developers:
        keyboard.append(InlineKeyboardButton(developer.user_name,
                                             callback_data=base64.b64encode(developer.user_name.encode('utf-8')).decode('utf-8')))
    markup.add(*keyboard)
    StateDao().set_state(call.message.chat.id, ChatState.PROJECT_CREATE_STATE, 5, [TmpData(project)])
    bot.reply_to(call.message,
                 text='Жаль конечно этого добряка!\n'
                      'Перейдем к следующему шагу.\n'
                      'Выберите разработчика проекта:',
                 reply_markup=markup)


def add_project_figma_step(call: CallbackQuery, bot: TeleBot):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    state = StateDao().get_by_chat_id(call.message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(call.message, text='Что-то пошло не так %F0%9F%98%93')
        return
    tmp: TmpData = state.tmp_data[0]
    project = tmp.parsed_data
    project.add_participant(UserDao().get_by_username(base64.b64decode(call.data).decode('utf-8')), UserRole.DEVELOPER)
    StateDao().set_state(call.message.chat.id, ChatState.PROJECT_CREATE_STATE, 6, [TmpData(project)])
    bot.reply_to(call.message,
                 text='Йес, минус три!\n'
                      'Время определиться со ссылками.\n'
                      'Введите ссылку на фигму или "Нет", если её нет (неожиданно, правда?):',
                 reply_markup=None)


def add_project_tilda_step(message: Message, bot: TeleBot):
    state = StateDao().get_by_chat_id(message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(message, text='Что-то пошло не так %F0%9F%98%93')
        return
    tmp: TmpData = state.tmp_data[0]
    project = tmp.parsed_data
    project.links = []
    if not message.text.lower().strip().startswith('нет'):
        project.links.append(ProjectLink(message.text.strip(), LinkType.FIGMA))
    StateDao().set_state(message.chat.id, ChatState.PROJECT_CREATE_STATE, 7, [TmpData(project)])
    bot.reply_to(message,
                 text='А круто нарисовано или нет, я не смотрел!\n'
                      'Перейдем к новой ссылке.\n'
                      'Введите ссылку на тильду или "Нет", если её нет (неожиданно, правда? х2):')


def add_project_tilda_creds_step(message: Message, bot: TeleBot):
    state = StateDao().get_by_chat_id(message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(message, text='Что-то пошло не так %F0%9F%98%93')
        return
    tmp: TmpData = state.tmp_data[0]
    project = tmp.parsed_data
    project.links = []
    if not message.text.lower().strip().startswith('нет'):
        project.links.append(ProjectLink(message.text.strip(), LinkType.TILDA))
    StateDao().set_state(message.chat.id, ChatState.PROJECT_CREATE_STATE, 8, [TmpData(project)])
    bot.reply_to(message,
                 text='Повезло-повезло!\n'
                      'Введите данные для доступа или "Нет", если их нет:')


def add_project_final_step(message: Message, bot: TeleBot):
    state = StateDao().get_by_chat_id(message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(message, text='Что-то пошло не так %F0%9F%98%93')
        return
    tmp: TmpData = state.tmp_data[0]
    project = tmp.parsed_data
    if not message.text.lower().strip().startswith('нет'):
        for link in project.links:
            if link.type == LinkType.TILDA:
                link.credentials = message.text.strip()
    # project.change_state(ProjectState.PRE_DEVELOPMENT)
    ProjectDao().add_project(project)
    StateDao().reset_state(message.chat.id)
    bot.reply_to(message,
                 text='Проект добавлен!\n'
                      'Ты заходи, если что!.\n')