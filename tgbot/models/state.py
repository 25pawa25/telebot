from sqlalchemy import Integer, Column, Enum
from sqlalchemy.orm import relationship

from tgbot.models import Base
from tgbot.models.chat_state import ChatState


class State(Base):

    __tablename__ = 'chat_state'

    id = Column(Integer, primary_key=True)
    state = Column(Enum(ChatState))
    step = Column(Integer, default=0, nullable=False)
    chat_id = Column(Integer, unique=True)
    tmp_data = relationship('TmpData')
