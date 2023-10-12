from typing import Optional

import jsonpickle

from tgbot.models import TmpData
from tgbot.utils.database import Database


class TmpDao:
    db: Database

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TmpDao, cls).__new__(cls)
            cls.instance.db = Database.get_instance()
        return cls.instance

    def get(self, id: int) -> Optional[TmpData]:
        return self.db.session().query(TmpData).filter(TmpData.id == id).one_or_none()

    def add_data(self, data: object) -> int:
        tmp = TmpData(data)
        with self.db.session.begin() as session:
            session.add(tmp)
            session.flush()
            return tmp.id

    def delete_by_state(self, state_id: int):
        with self.db.session.begin() as session:
            session.query(TmpData). \
                filter(TmpData.state_id == state_id). \
                delete()
            session.commit()
            session.flush()

