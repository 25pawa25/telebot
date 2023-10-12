from tgbot.models import UserRole


class ChangeUserDto:
    user_role: str

    def __init__(self, user_role: UserRole):
        self.user_role = user_role
