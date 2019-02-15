from uuid import uuid4

from .base import BaseManager


class ServiceNotCreated(Exception):
    """A Service was requested but none existed"""


class OrganizationServiceManager(BaseManager):
    def __init__(self, organization_factory):
        self.current_service = None
        self.previous_service = None
        self._current_service_list = []
        self._current_service_public_keys = {}
        BaseManager.__init__(self, organization_factory)

    @property
    def current_service(self):
        if self._current_service is None:
            raise ServiceNotCreated("A Service has not been created yet.")
        return self._current_service

    @current_service.setter
    def current_service(self, value):
        self.previous_service = getattr(
            self, "_current_service", None)
        self._current_service = value

    def create_service(self, name=None, description=None, icon=None,
                       callback_url=None, active=True):
        if name is None:
            name = str(uuid4())
        self.current_service = self._organization_client.create_service(
            name,
            description=description,
            icon=icon,
            callback_url=callback_url,
            active=active
        )
        return self.current_service

    def retrieve_service(self, service_id):
        self.current_service = self._organization_client.get_service(
            service_id
        )
        return self.current_service

    def add_public_key_to_service(self, public_key, service_id):
        self._organization_client.add_service_public_key(
            service_id,
            public_key.public_key,
            expires=public_key.expires,
            active=public_key.active
        )

    def update_public_key(self, key_id, service_id, expires=False,
                          active=None):
        self._organization_client.update_service_public_key(
            service_id,
            key_id,
            expires=expires,
            active=active
        )

    def retrieve_public_keys_list(self, service_id):
        self._organization_client.get_service_public_keys(
            service_id
        )

    def remove_public_key(self, key_id, service_id):
        self._organization_client.remove_service_public_key(
            service_id,
            key_id
        )

    def update_service(self, service_id, name=False,
                       description=False, icon=False, callback_url=False,
                       active=None):
        self._organization_client.update_service(
            service_id,
            name=name,
            description=description,
            icon=icon,
            callback_url=callback_url,
            active=active
        )

    def retrieve_services(self, service_ids):
        self._current_service_list = self._organization_client.get_services(
            service_ids
        )
        return self._current_service_list

    def retrieve_all_services(self):
        self._current_service_list = self._organization_client.\
            get_all_services()
        return self._current_service_list
