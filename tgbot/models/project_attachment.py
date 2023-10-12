from tgbot.models.attachment_type import AttachmentType
from sqlalchemy import Column, String, Enum, Integer, ForeignKey
from sqlalchemy.orm import declarative_base

from tgbot.models.base import BaseModel


class ProjectAttachment(BaseModel):
    __tablename__ = 'project_attachment'

    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    file_path = Column(String(200), unique=True)
    type = Column(Enum(AttachmentType))
    project_id = Column(Integer, ForeignKey('project.id'))
