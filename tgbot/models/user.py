from typing import List

from sqlalchemy import Column, String, Enum, Integer

from tgbot.models.user_role import UserRole
from sqlalchemy.orm import declarative_base

from tgbot.models.base import BaseModel


class User(BaseModel):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(100), unique=True)
    user_role = Column(Enum(UserRole))
