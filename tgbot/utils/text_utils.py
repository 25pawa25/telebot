from ctypes import ArgumentError

from tgbot.models import UserRole, ProjectState
from tgbot.models.attachment_type import AttachmentType


def describe_project_state(state: ProjectState) -> str:
    if state is ProjectState.PRE_DEVELOPMENT:
        return 'Проработка'
    if state is ProjectState.AGREEMENT:
        return 'Согласование'
    if state is ProjectState.DESIGN_AGREEMENT:
        return 'Согласование: дизайн'
    if state is ProjectState.LAYOUT_AGREEMENT:
        return 'Согласование: вёрстка'
    if state is ProjectState.DEVELOPMENT_DESIGN:
        return 'Разработка: дизайн'
    if state is ProjectState.DEVELOPMENT_LAYOUT:
        return 'Разработка: вёрстка'
    if state is ProjectState.READY:
        return 'Завершен'
    if state is ProjectState.NEXT:
        return 'Следующий статус'
    raise ArgumentError('Illegal state')


def describe_user_role(status: UserRole) -> str:
    if status is UserRole.ADMIN:
        return 'Администратор'
    if status is UserRole.MANAGER:
        return 'Руководитель'
    if status is UserRole.DESIGNER:
        return 'Дизайнер'
    if status is UserRole.DEVELOPER:
        return 'Разработчик'
    raise ArgumentError('Illegal status')


def describe_file_type(type: AttachmentType) -> str:
    if type is AttachmentType.DOCUMENT:
        return 'Документ'
    if type is AttachmentType.TECHNICAL:
        return 'Техническое задание'
    if type is AttachmentType.OTHER:
        return 'Материал проекта'
    raise ArgumentError('Illegal type')


def extract_arg(arg):
    from shlex import split
    return split(arg)[1:]