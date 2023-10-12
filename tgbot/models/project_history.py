from datetime import datetime

from sqlalchemy import Column, Date, Enum, DateTime, func, Integer, ForeignKey

from tgbot.models.project_states import ProjectState
from sqlalchemy.orm import declarative_base

from tgbot.models.base import BaseModel


class ProjectHistory(BaseModel):
    __tablename__ = 'project_history'

    id = Column(Integer, primary_key=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    state = Column(Enum(ProjectState))
    project_id = Column(Integer, ForeignKey('project.id'))

    def __init__(self, state: ProjectState):
        self.state = state

    def change_state(self, new_state) -> None:
        self.state.append(new_state)
