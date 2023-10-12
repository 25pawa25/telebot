from tgbot.models import ChatState
from tgbot.models.dao.state_dao import StateDao


def state_step_check_callback_query(state: ChatState, step: int = 0):
    def wrapper(call):
        return StateDao().check_current_state(call.message.chat.id, state, step)
    return wrapper


def state_step_check_callback_message(state: ChatState, step: int = 0):
    def wrapper(call):
        return StateDao().check_current_state(call.chat.id, state, step)
    return wrapper
