from launchkey.entities.service import AuthPolicy


class AuthPolicyManager:

    def __init__(self):
        self.previous_policy = None
        self.current_policy = AuthPolicy()

    @property
    def current_policy(self):
        return self._current_policy

    @current_policy.setter
    def current_policy(self, value):
        self.previous_policy = getattr(self, "_current_policy", None)
        self._current_policy = value
