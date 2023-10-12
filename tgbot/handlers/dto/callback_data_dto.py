from enum import Enum


class CallbackDataType(Enum):
    USER_ADD = 'USER_ADD'
    PROJECT_ADD = 'PROJECT_ADD'
    CHANGE_STATE = 'CHANGE_STATE'
    CHANGE_USER = 'CHANGE_USER'
    ADD_FILE = 'ADD_FILE'
    SHOW_PROJECT = 'SHOW_PROJECT'


class CallbackDataDto:
    data_type: str
    data_id: int

    def __init__(self, data_type: CallbackDataType, data_id: int):
        self.data_type = data_type.value
        self.data_id = data_id
