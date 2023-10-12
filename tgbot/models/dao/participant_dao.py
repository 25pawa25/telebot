from typing import Optional

from sqlalchemy.orm import Session
from tgbot.models import User, UserRole, Project, ProjectParticipant
from tgbot.utils.database import Database


class ParticipantDao:

    db: Database

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ParticipantDao, cls).__new__(cls)
            cls.instance.db = Database.get_instance()
        return cls.instance

    def participants_filtered(self, user_id: int, project_id: int) -> Optional[User]:
        return self.db.session().query(ProjectParticipant). \
            filter(ProjectParticipant.project_id == project_id, ProjectParticipant.user_id == user_id). \
            one_or_none()

    def participants_filtered_by_role(self, role: UserRole, project_id: int):
        return self.db.session().query(ProjectParticipant). \
            filter(ProjectParticipant.project_id == project_id, ProjectParticipant.role == role). \
            one_or_none()