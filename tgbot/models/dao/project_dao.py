from typing import Optional
import logging
from sqlalchemy.orm import Session, joinedload, selectinload
from tgbot.models import User, UserRole, Project, ProjectState, ProjectHistory, ProjectParticipant,\
    ProjectLink, ProjectAttachment
from tgbot.models.attachment_type import AttachmentType
from tgbot.utils.database import Database

class ProjectDao:

    db: Database

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProjectDao, cls).__new__(cls)
            cls.instance.db = Database.get_instance()
        return cls.instance

    def get_by_code(self, code: str) -> Optional[User]:
        #session = self.db.session()
        #return session.query(Project).filter(Project.code == code).one_or_none()
        return self.db.session().query(Project).filter(Project.code == code).one_or_none()

    def add_project(self, project: Project) -> None:
        with self.db.session.begin() as session:
            session.add(project)
            session.flush()

    def get_project_by_name(self, name: str) -> Optional[User]:
        return self.db.session().query(Project).filter(Project.name == name).one_or_none()

    def activ_projects_of_user(self, user_id: int) -> Optional[User]:
        return self.db.session().query(Project).join(ProjectParticipant).join(ProjectHistory).\
            filter(ProjectParticipant.user_id == user_id, ProjectHistory.state != ProjectState.READY)

    def history_of_project(self, project_id: int) -> Optional[User]:
        return self.db.session().query(ProjectHistory).\
            filter(ProjectHistory.project_id == project_id).one_or_none()

    def links_of_project(self, project_id: int) -> Optional[User]:
        return self.db.session().query(ProjectLink).filter(ProjectLink.project_id == project_id).one_or_none()

    def project_of_state(self, state: ProjectState) -> Optional[User]:
        return self.db.session().query(Project).join(ProjectHistory).filter(ProjectHistory.state == state)

    def projects_of_user_state(self, user_id: int, state: ProjectState) -> Optional[User]:
        return self.db.session().query(Project).join(ProjectParticipant).join(ProjectHistory).\
            filter(ProjectParticipant.user_id == user_id, ProjectHistory.state == state)

    def activ_projects(self) -> Optional[User]:
        return self.db.session().query(Project).join(ProjectHistory).\
            filter(ProjectHistory.state != ProjectState.READY)

    def project_document(self, project_id: int) -> Optional[User]:
        return self.db.session().query(ProjectAttachment).filter(ProjectAttachment.project_id == project_id,
                                                           ProjectAttachment.type == AttachmentType.DOCUMENT).\
            one_or_none()

    def change_state(self, project_id: int, state: ProjectState):
        with self.db.session.begin() as session:
            query = session.query(ProjectHistory).filter(ProjectHistory.project_id == project_id). \
                update({ProjectHistory.state: state}, synchronize_session=False)
            session.flush()

    def add_attachment(self, name: str, file_path: str, type: AttachmentType, project_id: int) -> None:
        new_attachment = ProjectAttachment()
        new_attachment.name = name
        new_attachment.file_path = file_path
        new_attachment.type = type
        new_attachment.project_id = project_id
        with self.db.session.begin() as session:
            session.add(new_attachment)
            session.flush()
