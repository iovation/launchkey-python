from time import sleep

from launchkey.exceptions import EntityNotFound

from .base import BaseManager


class AuthRequestNotRetrieved(Exception):
    """Auth request has not been retrieved yet"""


class DirectoryServiceAuthsManager(BaseManager):
    def __init__(self, organization_factory):
        self.current_auth_response = None
        self.previous_auth_response = None
        self.current_auth_request = None
        self.current_auth_request_id = None
        self.previous_auth_request_id = None
        super(DirectoryServiceAuthsManager, self, ).__init__(
            organization_factory)

    @property
    def current_auth_response(self):
        return self._current_auth_response

    @current_auth_response.setter
    def current_auth_response(self, value):
        self.previous_auth_request = getattr(
            self, "_current_auth_response", None)
        self._current_auth_response = value

    @property
    def current_auth_request_id(self):
        return self._current_auth_request_id

    @current_auth_request_id.setter
    def current_auth_request_id(self, value):
        self.previous_auth_request_id = getattr(
            self, "_current_auth_request_id", None)
        self._current_auth_request_id = value

    def create_auth_request(self, service_id, user, context=None, policy=None,
                            title=None, ttl=None, push_title=None,
                            push_body=None, denial_reasons=None):
        client = self._get_service_client(service_id)
        try:
            current_auth_request = client.authorization_request(
                user,
                context=context,
                policy=policy,
                title=title,
                ttl=ttl,
                push_title=push_title,
                push_body=push_body,
                denial_reasons=denial_reasons
            )

            self.current_auth_request = current_auth_request
            self.current_auth_request_id = current_auth_request.auth_request

        except EntityNotFound:
            sleep(2)
            current_auth_request = client.authorization_request(
                user,
                context=context,
                policy=policy,
                title=title,
                ttl=ttl,
                push_title=push_title,
                push_body=push_body,
                denial_reasons=denial_reasons
            )

            self.current_auth_request = current_auth_request
            self.current_auth_request_id = current_auth_request.auth_request

    def get_auth_response(self, service_id, auth_request):
        client = self._get_service_client(service_id)
        self.current_auth_response = client.get_authorization_response(
            auth_request)
        if not self.current_auth_response:
            sleep(2)
            self.current_auth_response = client.get_authorization_response(
                auth_request)
        return self.current_auth_response

    def get_advanced_auth_response(self, service_id, auth_request):
        client = self._get_service_client(service_id)
        self.current_auth_response = client \
            .get_advanced_authorization_response(auth_request)
        if not self.current_auth_response:
            sleep(2)
            self.current_auth_response = client \
                .get_advanced_authorization_response(auth_request)
        return self.current_auth_response
