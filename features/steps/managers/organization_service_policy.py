from .base import BaseManager

from launchkey.entities.service import ServiceSecurityPolicy


class ServicePolicyNotCreated(Exception):
    """A Service Policy was requested but none existed"""


class OrganizationServicePolicyManager(BaseManager):
    def __init__(self, organization_factory):
        self.previous_service_policy = None
        self.current_service_policy = ServiceSecurityPolicy()
        BaseManager.__init__(self, organization_factory)

    @property
    def current_service_policy(self):
        if self._current_service_policy is None:
            raise ServicePolicyNotCreated("A policy has not been created yet.")
        return self._current_service_policy

    @current_service_policy.setter
    def current_service_policy(self, value):
        self.previous_service_policy = getattr(
            self, "_current_service_policy", None)
        self._current_service_policy = value

    def retrieve_service_policy(self, service_id):
        self._current_service_policy = \
            self._organization_client.get_service_policy(service_id)
        return self._current_service_policy

    def remove_service_policy(self, service_id):
        self._organization_client.remove_service_policy(service_id)

    def set_service_policy(self, service_id, policy):
        self._organization_client.set_service_policy(service_id, policy)
