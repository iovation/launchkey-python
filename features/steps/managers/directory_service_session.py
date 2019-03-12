from uuid import uuid4

from .base import BaseManager


class DirectoryServiceSessionManager(BaseManager):
    def __init__(self, organization_factory):
        super(DirectoryServiceSessionManager, self, ).__init__(
            organization_factory)

    def start_session(self, service_id, user_identifier, auth_request=None):
        if auth_request is None:
            auth_request = str(uuid4())
        client = self._get_service_client(service_id)
        client.session_start(
            user_identifier,
            auth_request
        )

    def end_session(self, service_id, user_identifier):
        client = self._get_service_client(service_id)
        client.session_end(user_identifier)
