from tgbot.models.link_type import LinkType
from sqlalchemy import Column, Enum, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base

from tgbot.models.base import BaseModel


class ProjectLink(BaseModel):

    __tablename__ = 'project_link'

    id = Column(Integer, primary_key=True)
    type = Column(Enum(LinkType))
    url = Column(String(1000))
    credentials = Column(String(1000))
    description = Column(String(1000))
    project_id = Column(Integer, ForeignKey('project.id'))

    def __init__(self, url: str, type: LinkType):
        self.url = url
        self.type = type
