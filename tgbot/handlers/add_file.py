import datetime
from datetime import datetime
from telebot import TeleBot
import os
import time
from telebot.types import Message, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardButton, CallbackQuery
import zipfile
from tgbot.decorator import log_message
from tgbot.handlers.dto.callback_data_dto import CallbackDataType
from tgbot.models import UserRole, Project, ChatState, TmpData
from tgbot.models.attachment_type import AttachmentType
from tgbot.models.dao.project_dao import ProjectDao
from tgbot.models.dao.state_dao import StateDao
from tgbot.models.dao.tmp_dao import TmpDao
from tgbot.models.dao.user_dao import UserDao
from tgbot.handlers.dto.file_add_dto import FileAddDto
from tgbot.utils.text_utils import extract_arg, describe_file_type
from tgbot.utils.bot import state_step_check_callback_message, state_step_check_callback_query
import jsonpickle as jp
import json

CALLBACK_DATA = {
    'type': CallbackDataType.ADD_FILE.value,
    'step': 1,
    'data': ''
}


def add_file_handler(bot: TeleBot):
    bot.register_message_handler(type_selection,
                                 commands=['addFile', 'file', 'fileAdd'],
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])

    bot.register_callback_query_handler(add_file,
                                        func=state_step_check_callback_query(ChatState.ADD_FILE_STATE, 1),
                                        pass_bot=True,
                                        roles=[UserRole.ADMIN])

    bot.register_message_handler(add_file_callback,
                                 func=state_step_check_callback_message(ChatState.ADD_FILE_STATE, 2),
                                 pass_bot=True,
                                 content_types=['document'],
                                 roles=[UserRole.ADMIN])

    bot.register_message_handler(distr,
                                 func=state_step_check_callback_message(ChatState.ADD_FILE_STATE, 3),
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN])


def distrib_files(src, bot, message):
    files = os.listdir(src)
    files = [os.path.join(src, file) for file in files]
    k = 0
    cur_files = []
    for file in files:
        if not zipfile.is_zipfile(file):
            ctime = os.path.getctime(file)
            date_file = datetime.strptime(time.ctime(ctime), "%a %b %d %H:%M:%S %Y")
            date_now = datetime.today().replace(microsecond=0)
            delta = date_now - date_file
            delta = delta.seconds
            if delta < 30:
                k += 1
                cur_files.append(file.split('\\')[-1])

    if k > 1:
        now = datetime.now()
        name = str(now.strftime("%d-%m-%Y %H.%M")) + ".zip"
        name = src + name
        with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED, True) as myzip:
            for root, dirs, files in os.walk(src):
                for file in files:
                    if file in cur_files:
                        path = os.path.join(root, file)
                        myzip.write(path, file)
                        os.remove(path)
        bot.reply_to(message, text='Архив создан!')

    cur_files.clear()


@log_message
def type_selection(message: Message, bot: TeleBot):
    args = extract_arg(message.text)
    code = args[0]
    project = ProjectDao().get_by_code(code)

    if project is None:
        bot.reply_to(message, text='Такого проекта не найдено!')
        return

    markup = InlineKeyboardMarkup(row_width=1)
    keyboard = []

    for type in AttachmentType:
        callback_data = {
            'type': CallbackDataType.ADD_FILE.value,
            'data': TmpDao().add_data(FileAddDto(type))
        }
        keyboard.append(InlineKeyboardButton(describe_file_type(type),
                                             callback_data=json.dumps(callback_data)))

    markup.add(*keyboard)
    StateDao().set_state(message.chat.id, ChatState.ADD_FILE_STATE, 1, [TmpData(project)])
    bot.reply_to(message, 'Выберите тип файла:', reply_markup=markup)


def add_file(call: CallbackQuery, bot: TeleBot):
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
        logger.error(
            f'Can\'t get tmp data for {call.from_user.username} request! TmpData id: {callback_data.get("data")}')
        bot.edit_message_text('Что-то пошло не так!', call.message.chat.id, call.message.id, reply_markup=None)
        return

    file_dto: FileAddDto = jp.loads(data.data)
    attachment_type = file_dto.type
    StateDao().set_state(call.message.chat.id, ChatState.ADD_FILE_STATE, 2,
                         [TmpData(project), TmpData(attachment_type)])
    bot.reply_to(call.message, 'Отправьте ваши файлы')


def add_file_callback(message: Message, bot: TeleBot):
    state = StateDao().get_by_chat_id(message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(message, text='Что-то пошло не так %F0%9F%98%93')
        return

    tmp: TmpData = state.tmp_data[0]
    project = tmp.parsed_data
    temp: TmpData = state.tmp_data[1]
    attachment_type = temp.parsed_data

    file_info = bot.get_file(message.document.file_id)

    if file_info is None:
        bot.reply_to(message, text='Ошибка! \n'
                                   'Отправьте, пожалуйста, снова')
        return

    #try:
    downloaded_file = bot.download_file(file_info.file_path)
    src = fr'D:\telegram-bot\upload\{str(project.code)}\{str(attachment_type).split(".")[1]}\ '
    src = src.replace(" ", "")
    if not os.path.exists(src):
        os.makedirs(src)

    path = src.replace(" ", "") + message.document.file_name
    with open(path, 'wb') as new_file:
        new_file.write(downloaded_file)

    ProjectDao().add_attachment(message.document.file_name, path, attachment_type, project.id)
    bot.reply_to(message, "Пожалуй, я сохраню это")

    #except Exception as e:
    #    bot.reply_to(message, 'Не получилось...')

    StateDao().set_state(message.chat.id, ChatState.ADD_FILE_STATE, 3, [TmpData(src)])


def distr(message: Message, bot: TeleBot):
    state = StateDao().get_by_chat_id(message.chat.id)
    if state.tmp_data is None or len(state.tmp_data) == 0:
        bot.reply_to(message, text='Что-то пошло не так %F0%9F%98%93')
        return

    tmp: TmpData = state.tmp_data[0]
    src = tmp.parsed_data
    distrib_files(src, bot, message)
    StateDao().reset_state(message.chat.id)
