from tgbot.models import UserRole


class UserAddDto:
    username: str
    role: str

    def __init__(self, username: str, role: UserRole):
        self.username = username
        self.role = role.value
