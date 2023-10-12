from sqlalchemy import Column, Enum, Integer, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from tgbot.models.user_role import UserRole

from tgbot.models.base import BaseModel


class ProjectParticipant(BaseModel):

    __tablename__ = 'project_participant'

    id = Column(Integer, primary_key=True)
    user = relationship('User')
    user_id = Column(Integer, ForeignKey('user.id'))
    role = Column(Enum(UserRole))
    project_id = Column(Integer, ForeignKey('project.id'))
