import jsonpickle
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from tgbot.models.base import Base


class TmpData(Base):

    __tablename__ = 'tmp_data'

    id = Column(Integer, primary_key=True)
    data = Column(JSONB)

    state_id = Column(Integer, ForeignKey('chat_state.id'), nullable=True)

    def __init__(self, data: object):
        self.data = jsonpickle.dumps(data)

    @property
    def parsed_data(self):
        return jsonpickle.loads(self.data)
