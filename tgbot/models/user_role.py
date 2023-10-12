from enum import Enum


class UserRole(Enum):
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    DESIGNER = 'DESIGNER'
    DEVELOPER = 'DEVELOPER'

    @classmethod
    def is_value_of(cls, value) -> bool:
        for role in cls:
            if role.value == value:
                return True
        return False

    @classmethod
    def value_of(cls, value):
        for role in cls:
            if role.value == value:
                return role
        raise ValueError(f'Can\'t parse UserRole from: {value} ')
