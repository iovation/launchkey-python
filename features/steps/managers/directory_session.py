from .base import BaseManager


class SessionListNotRetrieved(Exception):
    """Session list has not been retrieved yet"""


class DirectorySessionManager(BaseManager):
    def __init__(self, organization_factory):
        self.current_session_list = None
        self.previous_session_list = None
        super(DirectorySessionManager, self, ).__init__(
            organization_factory)

    @property
    def current_session_list(self):
        if self._current_session_list is None:
            raise SessionListNotRetrieved
        return self._current_session_list

    @current_session_list.setter
    def current_session_list(self, value):
        self.previous_session_list = getattr(
            self, "_current_session_list", None)
        self._current_session_list = value

    def retrieve_session_list_for_user(self, user_identifier, directory_id):
        directory_client = self._get_directory_client(directory_id)
        self.current_session_list = directory_client.get_all_service_sessions(
            user_identifier
        )
        return self.current_session_list

    def end_all_sessions_for_user(self, user_identifier, directory_id):
        directory_client = self._get_directory_client(directory_id)
        directory_client.end_all_service_sessions(
            user_identifier
        )
