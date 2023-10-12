from enum import Enum


class ChatState(Enum):
    DEFAULT_STATE = 0
    USER_CREATE_STATE = 1
    PROJECT_CHANGE_STATE = 2
    PROJECT_CREATE_STATE = 3
    CHANGE_USER_STATE = 4
    ADD_FILE_STATE = 5
    SHOW_PROJECT_STATE = 6
