from typing import Optional, List
import logging
from sqlalchemy.orm import Session

from tgbot.models import User, UserRole, Project, ProjectParticipant
from tgbot.utils.database import Database


class UserDao:

    db: Database

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(UserDao, cls).__new__(cls)
            cls.instance.db = Database.get_instance()
        return cls.instance

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.session().query(User).filter(User.user_name == username).one_or_none()

    def get_all_by_role(self, user_roles: List[UserRole]) -> List[User]:
        return self.db.session().query(User).filter(User.user_role.in_(user_roles)).all()

    def add_user(self, username: str, role: UserRole) -> None:
        user = User()
        user.user_name = username
        user.user_role = role
        with self.db.session.begin() as session:
            session.add(user)
            session.flush()

    def change_participant(self, old_participant: User, new_participant: User, project: Project) -> None:
        with self.db.session.begin() as session:
                query = session.query(ProjectParticipant).filter(ProjectParticipant.project_id == project.id,
                                                                 ProjectParticipant.user == old_participant).\
                    update({ProjectParticipant.user_id: new_participant.id}, synchronize_session=False)
                session.flush()

