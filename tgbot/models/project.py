import logging
from datetime import datetime

from sqlalchemy import Date, Column, String, DateTime, func, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from tgbot.models.project_history import ProjectHistory
from tgbot.models.project_states import ProjectState
from tgbot.models.project_participant import ProjectParticipant
from tgbot.models.user import User
from tgbot.models.attachment_type import AttachmentType
from tgbot.models.user_role import UserRole
from tgbot.models.project_attachment import ProjectAttachment
from tgbot.models.base import BaseModel


class Project(BaseModel):

    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    code = Column(String(100), unique=True)
    history = relationship('ProjectHistory', lazy='dynamic')
    participants = relationship('ProjectParticipant', lazy='dynamic')
    links = relationship('ProjectLink')
    attachments = relationship('ProjectAttachment', lazy='dynamic')
    price = Column(String(100))
    deadline = Column(Date())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    @classmethod
    def new(cls):
        instance = Project()
        instance.change_state(ProjectState.PRE_DEVELOPMENT)
        return instance


    @property
    def current_state(self) -> ProjectState:
        return sorted(self.history, key=lambda x: x.changed_at, reverse=True)[0]

    def change_state(self, new_state) -> None:
        self.history.append(ProjectHistory(new_state))

    def add_participant(self, user: User, role: UserRole) -> None:
        if len(self.participants) == 3:
            logging.error(f'You can\'t add new participant to project "{self.name}"')
            raise RuntimeError(f'You can\'t add new participant to project "{self.name}"')
        new_participant = ProjectParticipant()
        new_participant.role = role
        new_participant.user = user
        self.participants.append(new_participant)

    def change_participant(self, old_participant: User, new_participant: User) -> None:
        for participant in self.participants:
            if participant.user.user_name == new_participant.user_name:
                logging.error(f'You can\'t change participant which exists in project "{self.name}"')
                raise RuntimeError(f'You can\'t change participant which exists in project "{self.name}"')
            if participant.user.user_name == old_participant.user_name:
                participant.user = new_participant
                return
        logging.error(f'Changable participant not found in "{self.name}"')
