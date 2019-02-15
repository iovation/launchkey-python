from .base import BaseManager


class DirectorySessionManager(BaseManager):
    def __init__(self, organization_factory):
        self._current_session_list = []
        BaseManager.__init__(self, organization_factory)

    def retrieve_session_list_for_user(self, user_identifier, directory_id):
        directory_client = self._get_directory_client(directory_id)
        self._current_session_list = directory_client.get_all_service_sessions(
            user_identifier
        )
        return self._current_session_list

    def end_all_sessions_for_user(self, user_identifier, directory_id):
        directory_client = self._get_directory_client(directory_id)
        directory_client.end_all_service_sessions(
            user_identifier
        )
        self._current_session_list = []
