from typing import Optional, List

from telebot import logger

from tgbot.models import State, ChatState, TmpData
from tgbot.models.dao.tmp_dao import TmpDao
from tgbot.utils.database import Database


class StateDao:
    db: Database

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StateDao, cls).__new__(cls)
            cls.instance.db = Database.get_instance()
        return cls.instance

    def get_by_chat_id(self, chat_id: int) -> Optional[State]:
        return self.db.session().query(State).filter(State.chat_id == chat_id).one_or_none()

    def check_current_state(self, chat_id: int, current_state: ChatState, step: int = 0) -> bool:
        logger.info(f'Check chat {chat_id} is on {current_state.name} and step {step}')
        return self.db.session().query(self.db.session().query(State)\
               .filter(State.chat_id == chat_id, State.state == current_state, State.step == step)\
               .exists()).scalar()

    def set_state(self, chat_id: int, chat_state: ChatState, step: int = 0, tmp: List[TmpData] = None) -> State:
        with self.db.session.begin() as session:
            state = session.query(State).filter(State.chat_id == chat_id).one_or_none()
            if state is None:
                state = State()
                state.chat_id = chat_id
            state.state = chat_state
            state.step = step
            state.tmp_data = tmp
            session.add(state)
            session.flush()
            return state

    def reset_state(self, chat_id):
        with self.db.session.begin() as session:
            session.query(State). \
                filter(State.chat_id == chat_id). \
                update({'state': ChatState.DEFAULT_STATE, 'step': 0})
            session.commit()
            session.flush()

        TmpDao().delete_by_state(self.db.session().query(State).filter(State.chat_id == chat_id).one().id)

    def _state_exists(self, chat_id) -> bool:
        return self.db.session().query(self.db.session().query(State)
                                       .filter(State.chat_id == chat_id)
                                       .exists()).scalar()
