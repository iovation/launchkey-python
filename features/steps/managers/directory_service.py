from uuid import uuid4

from .base import BaseManager


class ServiceNotCreated(Exception):
    """A Service was requested but none existed"""


class ServiceListNotQueried(Exception):
    """Service list not queried yet"""


class ServicePublicKeysNotQueried(Exception):
    """Service public keys not queried yet"""


class DirectoryServiceManager(BaseManager):
    def __init__(self, organization_factory):
        self.current_service = None
        self.previous_service = None
        self.current_service_list = None
        self.previous_service_list = None
        self.current_service_public_keys = {}
        self.previous_service_public_keys = None
        super(DirectoryServiceManager, self, ).__init__(organization_factory)

    @property
    def current_service(self):
        if self._current_service is None:
            raise ServiceNotCreated("A Service has not been created yet.")
        return self._current_service

    @current_service.setter
    def current_service(self, value):
        self.previous_service = getattr(
            self, "_current_service_list", None)
        self._current_service = value

    @property
    def current_service_list(self):
        if self._current_service_list is None:
            raise ServiceListNotQueried("Service list not queried yet")
        return self._current_service_list

    @current_service_list.setter
    def current_service_list(self, value):
        self.previous_service_list = getattr(
            self, "_current_service_list", None)
        self._current_service_list = value

    @property
    def current_service_public_keys(self):
        if self._current_service_public_keys is None:
            raise ServicePublicKeysNotQueried("Service public keys "
                                              "not queried yet")
        return self._current_service_public_keys

    @current_service_public_keys.setter
    def current_service_public_keys(self, value):
        self.previous_service_public_keys = getattr(
            self, "_current_service_public_keys", None)
        self._current_service_public_keys = value

    def create_service(self, directory_id, name=None, description=None, icon=None,
                       callback_url=None, active=True):
        if name is None:
            name = str(uuid4())
        directory_client = self._get_directory_client(directory_id)
        service_id = directory_client.create_service(
            name,
            description=description,
            icon=icon,
            callback_url=callback_url,
            active=active
        )
        return self.retrieve_service(directory_id, service_id)

    def retrieve_service(self, directory_id, service_id):
        directory_client = self._get_directory_client(directory_id)
        self.current_service = directory_client.get_service(service_id)
        return self.current_service

    def add_public_key_to_service(self, directory_id, public_key, service_id):
        directory_client = self._get_directory_client(directory_id)
        directory_client.add_service_public_key(
            service_id,
            public_key.public_key,
            expires=public_key.expires,
            active=public_key.active
        )

    def update_public_key(self, directory_id, key_id, service_id,
                          expires=False, active=None):
        directory_client = self._get_directory_client(directory_id)
        directory_client.update_service_public_key(
            service_id,
            key_id,
            expires=expires,
            active=active
        )

    def retrieve_public_keys_list(self, directory_id, service_id):
        directory_client = self._get_directory_client(directory_id)
        self.current_service_public_keys = \
            directory_client.get_service_public_keys(
                service_id
            )
        return self.current_service_public_keys

    def remove_public_key(self, directory_id, key_id, service_id):
        directory_client = self._get_directory_client(directory_id)
        directory_client.remove_service_public_key(
            service_id,
            key_id
        )

    def update_service(self, directory_id, service_id, name=False,
                       description=False, icon=False, callback_url=False,
                       active=None):
        directory_client = self._get_directory_client(directory_id)
        directory_client.update_service(
            service_id,
            name=name,
            description=description,
            icon=icon,
            callback_url=callback_url,
            active=active
        )

    def retrieve_services(self, directory_id, service_ids):
        directory_client = self._get_directory_client(directory_id)
        self.current_service_list = directory_client.get_services(service_ids)
        return self.current_service_list

    def retrieve_all_services(self, directory_id):
        directory_client = self._get_directory_client(directory_id)
        self.current_service_list = directory_client.get_all_services()
        return self.current_service_list
