from uuid import uuid4

from .base import BaseManager


class DirectoryNotCreated(Exception):
    """A Directory was requested but none existed"""


class DirectoryManager(BaseManager):

    def __init__(self, organization_factory):
        self._directories = []
        # self._current_directory_entity_list = []  # Look into removing
        # self._current_sdk_keys = []  # Look into removing
        # self.previous_directory = None  # Look into removing
        self._current_public_keys = []
        self.current_directory = None

        BaseManager.__init__(self, organization_factory)

    @property
    def current_directory(self):
        if self._current_directory is None:
            raise DirectoryNotCreated("A Directory has not been created yet.")
        return self._current_directory

    @current_directory.setter
    def current_directory(self, value):
        self.previous_directory = getattr(self, "_current_directory", None)
        self._current_directory = value

    def create_directory(self, name=None):
        if name is None:
            name = str(uuid4())
        directory_id = self._organization_client.create_directory(name)
        directory = self._organization_client.get_directory(directory_id)
        self.current_directory = directory
        self._directories.append(directory)
        return self.current_directory

    def get_any_directory(self):
        return self.current_directory if self._current_directory is not None \
            else self.create_directory()

    def update_directory(self, directory_id, ios_p12=False,
                         android_key=False, active=None,
                         denial_context_inquiry_enabled=None):
        self._organization_client.update_directory(
            directory_id,
            ios_p12=ios_p12,
            android_key=android_key,
            active=active,
            denial_context_inquiry_enabled=denial_context_inquiry_enabled
        )

    def generate_and_add_directory_sdk_key_to_directory(self, directory_id):
        return self._organization_client.generate_and_add_directory_sdk_key(
            directory_id
        )

    def retrieve_directory(self, directory_id):
        return self._organization_client.get_directory(directory_id)

    def retrieve_all_directories(self):
        return self._organization_client.get_all_directories()

    def retrieve_directory_sdk_keys(self, directory_id):
        raise NotImplemented()

    def remove_sdk_key_from_directory(self, sdk_key, directory_id):
        self._organization_client.remove_directory_sdk_key(
            directory_id, sdk_key)

    def add_public_key_to_directory(self, public_key, directory_id):
        self._organization_client.add_directory_public_key(
            directory_id,
            public_key.public_key,
            expires=public_key.expires,
            active=public_key.active
        )

    def retrieve_directory_public_keys(self, directory_id):
        public_keys = self._organization_client.get_directory_public_keys(
            directory_id)
        if directory_id == self.current_directory.id:
            self._current_public_keys = public_keys
        return public_keys

    def update_directory_public_key(self, key_id, directory_id,
                                    expires=False, active=None):
        self._organization_client.update_directory_public_key(
            directory_id, key_id, expires=expires, active=active)
        if directory_id == self.current_directory.id:
            # If we update the current directory, trigger a refresh on its keys
            self.retrieve_directory_public_keys()

    def remove_directory_public_key(self, key_id, directory_id):
        self._organization_client.remove_directory_public_key(
            directory_id, key_id)
