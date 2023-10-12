from telebot import TeleBot

from telebot.types import Message, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardButton, CallbackQuery

from tgbot.decorator import log_message
from tgbot.handlers.dto.callback_data_dto import CallbackDataType
from tgbot.models import UserRole, Project, ChatState, TmpData, ProjectLink, ProjectState
from tgbot.models.link_type import LinkType
from tgbot.models.dao.project_dao import ProjectDao
from tgbot.models.dao.state_dao import StateDao
from tgbot.models.dao.tmp_dao import TmpDao
from tgbot.models.dao.user_dao import UserDao
from tgbot.models.dao.participant_dao import ParticipantDao
from tgbot.utils.bot import state_step_check_callback_message, state_step_check_callback_query
from tgbot.utils.text_utils import extract_arg, describe_user_role, describe_project_state



CALLBACK_DATA = {
    'type': CallbackDataType.SHOW_PROJECT.value,
    'step': 1,
    'data': ''
}


def show_projects_handler(bot: TeleBot):
    bot.register_message_handler(show_projects,
                                 commands=['showProjects', 'show'],
                                 pass_bot=True,
                                 roles=[UserRole.ADMIN, UserRole.DESIGNER, UserRole.DEVELOPER])


def callback_filter(call: CallbackQuery) -> bool:
    if not call.data:
        return False
    try:
        callback_data = json.loads(call.data)
        return callback_data['type'] == CallbackDataType.SHOW_PROJECT.value
    except Exception as e:
        logger.error(e)
        return False


def return_context(project):
    context = {}
    part = {}
    project_links = ProjectDao().links_of_project(project.id)

    context['name'] = project.name
    context['code'] = project.code
    context['state'] = describe_project_state(ProjectDao().history_of_project(project.id).state)
    context['changed_at'] = ProjectDao().history_of_project(project.id).changed_at

    for participant in project.participants:
        part[participant.user.user_name] = describe_user_role(ParticipantDao().
                                                              participants_filtered(participant.user_id,
                                                                                    participant.project_id).role)

    context['part'] = part
    if project_links:
        if project_links.type.LinkType.TILDA:
            context['tilda'] = LinkType.TILDA
            context['credentials'] = project.links.credentials
        if project_links.type.LinkType.FIGMA:
            context['figma'] = LinkType.FIGMA

    if project.links:
        context['url'] = project_links.url

    if project.price:
        context['price'] = project.price

    context['deadline'] = project.deadline

    document = ProjectDao().project_document(project.id)
    if document:
        context['document'] = document.file_path
    return context


def minimal_reference(bot: TeleBot, message: Message, context, previous=False):
    string = f'Название проекта: {context["name"]} \n'\
             f'Код проекта: {context["code"]} \n'\
             f'Статус проекта: {context["state"]} \n'\
             f'Срок исполнения статуса: {context["changed_at"]}\n'

    if previous:
        return string
    else:
        StateDao().reset_state(message.chat.id)
        bot.send_message(message.chat.id, text=string)



def brief_reference(bot: TeleBot, message: Message, context, previous=False):
    string = minimal_reference(bot, message, context, True)
    partis = ''
    for item in context['part'].items():
        partis += f'{item[0]}: {item[1]}\n'
    partis = 'Участники:\n' + partis +'\n'
    string += partis

    if 'tilda' in context:
        string += f'Тильда: {context.get("tilda")}\n'
    if 'figma' in context:
        string += f'Тильда: {context.get("figma")}\n'

    if previous:
        return string
    else:
        StateDao().reset_state(message.chat.id)
        bot.send_message(message.chat.id, text=string)


def full_reference(bot: TeleBot, message: Message, context, previous=False):
    string = brief_reference(bot, message, context, True)

    if 'credentials' in context:
        string += f'Доступ к тильде: {context["credentials"]}\n'

    if 'url' in context:
        string += f'Архив с файлами: {context["url"]}\n'

    if previous:
        return string
    else:
        bot.send_message(message.chat.id, text=string)
        StateDao().reset_state(message.chat.id)


def wide_reference(bot: TeleBot, message: Message, context):
    string = full_reference(bot, message, context, True)
    if 'price' in context:
        string += f'Стоимость проекта: {context["price"]}\n'

    string += f'Сроки исполнения: {context["deadline"]}\n'

    bot.send_message(message.chat.id, text=string)
    if 'document' in context:
        doc = open(context['document'], 'rb')
        bot.send_document(chat_id, doc)
        bot.send_document(chat_id, "FILEID")
    StateDao().reset_state(message.chat.id)


@log_message
def show_projects(message: Message, bot: TeleBot):
    user_id = UserDao().get_by_username(message.from_user.username).id
    role = UserDao().get_by_username(message.from_user.username).user_role
    args = extract_arg(message.text)

    if role == UserRole.ADMIN:
        if len(args) == 0:
            projects = ProjectDao().activ_projects()
            for project in projects:
                StateDao().set_state(message.chat.id, ChatState.SHOW_PROJECT_STATE, 1, [TmpData(project)])
                context = return_context(project)
                minimal_reference(bot, message, context)

        elif args[0].startswith('project_name='):
            name = args[0].split('=')[1]
            project = ProjectDao().get_project_by_name(name)
            StateDao().set_state(message.chat.id, ChatState.SHOW_PROJECT_STATE, 1, [TmpData(project)])
            if project is not None:

                context = return_context(project)

                if len(args) == 1:
                    brief_reference(bot, message, context)
                    StateDao().reset_state(message.chat.id)

                elif args[1].startswith('info_type='):
                    info_type = args[1].split('=')[1]

                    if info_type == 'minimal':
                        minimal_reference(bot, message, context)

                    elif info_type == 'brief':
                        brief_reference(bot, message, context)

                    elif info_type == 'full':
                        full_reference(bot, message, context)

                    elif info_type == 'wide':
                        wide_reference(bot, message, context)

                    else:
                        bot.send_message(message.chat.id, text='Такой справки нет')
                        return

                else:
                    bot.send_message(message.chat.id, text='Дополнительный аргумент: info_type')
                    return

            else:
                bot.send_message(message.chat.id, text='Такого проекта не существует!')
                return

        elif args[0].startswith('status='):
            name = args[0].split('=')[1]
            projects = ProjectDao().project_of_state(ProjectState(name))
            StateDao().set_state(message.chat.id, ChatState.SHOW_PROJECT_STATE, 1, [TmpData(name)])

            if len(args) == 2:
                if args[1].startswith('username='):
                    user = args[1].split('=')[1]
                    participant_id = UserDao().get_by_username(user).id
                    projects = ProjectDao().projects_of_user_state(participant_id, ProjectState(name))

            if projects is None:
                bot.send_message(message.chat.id, text='Проектов с таким статусом нет!')
                return

            for project in projects:
                context = return_context(project)
                minimal_reference(bot, message, context)

        elif args[0].startswith('username='):
            user = args[0].split('=')[1]
            participant_id = UserDao().get_by_username(user).id
            projects = ProjectDao().activ_projects_of_user(participant_id)
            StateDao().set_state(message.chat.id, ChatState.SHOW_PROJECT_STATE, 1, [TmpData(user)])

            if projects is None:
                bot.send_message(message.chat.id, text='Проектов с этим участником нет!')
                return

            for project in projects:
                context = return_context(project)
                minimal_reference(bot, message, context)

    elif role == UserRole.DESIGNER or role == UserRole.DEVELOPER:
        projects = ProjectDao().activ_projects_of_user(user_id)

        if projects is None:
            bot.send_message(message.chat.id, text='Проектов не найдено!')
            return

        if len(args) == 0:
            for project in projects:
                StateDao().set_state(message.chat.id, ChatState.SHOW_PROJECT_STATE, 1, [TmpData(project)])
                context = return_context(project)
                minimal_reference(bot, message, context)

        elif args[0].startswith('project_name='):
            project_name = args[0].split('=')[1]
            project = ProjectDao().get_project_by_name(project_name)
            StateDao().set_state(message.chat.id, ChatState.SHOW_PROJECT_STATE, 1, [TmpData(project)])

            if project is not None:
                context = return_context(project)

            else:
                bot.send_message(message.chat.id, text='Такого проекта не существует!')
                return

            if len(args) == 1:
                brief_reference(bot, message, context)

            elif args[1].startswith('info_type='):
                info_type = args[1].split('=')[1]

                if info_type == 'minimal':
                    minimal_reference(bot, message, context)

                elif info_type == 'brief':
                    brief_reference(bot, message, context)

                elif info_type == 'full':
                    full_reference(bot, message, context)

                elif info_type == 'wide':
                    wide_reference(bot, message, context)

                else:
                    bot.send_message(message.chat.id, text='Такой справки нет')
                    return

            else:
                bot.send_message(message.chat.id, text='Дополнительный аргумент: info_type')
                return

        else:
            bot.send_message(message.chat.id, text='Такого аргумента нет!')
            return

    else:
        bot.reply_to(message, text='Что-то пошло не так %F0%9F%98%93')
        return
