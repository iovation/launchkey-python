from .base import BaseManager


# @todo This doesn't seem to actually interact with directory services

class DirectoryServiceAuthsManager(BaseManager):
    def __init__(self, organization_factory):
        BaseManager.__init__(self, organization_factory)

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
        return client.get_authorization_response(auth_request)
