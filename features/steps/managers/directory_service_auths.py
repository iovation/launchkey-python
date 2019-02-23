from .base import BaseManager


class AuthRequestNotRetrieved(Exception):
    """Auth request has not been retrieved yet"""


class DirectoryServiceAuthsManager(BaseManager):
    def __init__(self, organization_factory):
        BaseManager.__init__(self, organization_factory)
        self.current_auth_request = None
        self.previous_auth_request = None

    @property
    def current_auth_request(self):
        return self._current_auth_request

    @current_auth_request.setter
    def current_auth_request(self, value):
        self.previous_auth_request = getattr(
            self, "_current_auth_request", None)
        self._current_auth_request = value

    def create_auth_request(self, service_id, user, context=None, policy=None,
                            title=None, ttl=None, push_title=None,
                            push_body=None, denial_reasons=None):
        client = self._get_service_client(service_id)
        client.authorization_request(
            user,
            context=context,
            policy=policy,
            title=title,
            ttl=ttl,
            push_title=push_title,
            push_body=push_body,
            denial_reasons=denial_reasons
        )

    def get_auth_response(self, service_id, auth_request):
        client = self._get_service_client(service_id)
        self.current_auth_request = client.get_authorization_response(auth_request)
        return self.current_auth_request
