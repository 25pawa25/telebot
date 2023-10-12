from tgbot.models import UserRole


class ChangeStateDto:
    state: str

    def __init__(self, state: str):
        self.state = state

