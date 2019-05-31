from uuid import uuid4

from .base import BaseManager


class DirectoryNotCreated(Exception):
    """A Directory was requested but none existed"""


class DirectoriesNotRetrieved(Exception):
    """Directories haven't been retrieved yet"""


class PublicKeysNotRetrieved(Exception):
    """Public keys have not been retrieved yet"""


class DirectoryManager(BaseManager):

    def __init__(self, organization_factory):
        self.current_directories = None
        self.previous_directory = None
        self.current_sdk_keys = self._current_sdk_keys = []
        self.previous_sdk_keys = None
        self.current_public_keys = None
        self.current_directory = None
        super(DirectoryManager, self, ).__init__(organization_factory)

    @property
    def current_directory(self):
        if self._current_directory is None:
            raise DirectoryNotCreated("A Directory has not been created yet.")
        return self._current_directory

    @current_directory.setter
    def current_directory(self, value):
        self.previous_directory = getattr(self, "_current_directory", None)
        self._current_directory = value

    @property
    def current_directories(self):
        if self._current_directories is None:
            raise DirectoriesNotRetrieved
        return self._current_directories

    @current_directories.setter
    def current_directories(self, value):
        self.previous_directories = getattr(self, "_current_directories", None)
        self._current_directories = value

    @property
    def current_public_keys(self):
        if self._current_public_keys is None:
            raise PublicKeysNotRetrieved
        return self._current_public_keys

    @current_public_keys.setter
    def current_public_keys(self, value):
        self.previous_public_keys = getattr(self, "_current_public_keys", None)
        self._current_public_keys = value

    @property
    def current_sdk_keys(self):
        return self._current_sdk_keys

    @current_sdk_keys.setter
    def current_sdk_keys(self, value):
        self.previous_sdk_keys = getattr(self, "_current_sdk_keys", None)
        self._current_sdk_keys = value

    def create_directory(self, name=None):
        if name is None:
            name = str(uuid4())
        directory_id = self._organization_client.create_directory(name)
        directory = self._organization_client.get_directory(directory_id)
        self.current_directory = directory
        return self.current_directory

    def get_any_directory(self):
        return self.current_directory if self._current_directory is not None \
            else self.create_directory()

    def update_directory(self, directory_id, ios_p12=False,
                         android_key=False, active=None,
                         denial_context_inquiry_enabled=None,
                         webhook_url=False):
        self._organization_client.update_directory(
            directory_id,
            ios_p12=ios_p12,
            android_key=android_key,
            active=active,
            denial_context_inquiry_enabled=denial_context_inquiry_enabled,
            webhook_url=webhook_url
        )

    def generate_and_add_directory_sdk_key_to_directory(self, directory_id):
        sdk_key = self._organization_client.generate_and_add_directory_sdk_key(
            directory_id
        )
        self._current_sdk_keys.append(sdk_key)
        return sdk_key

    def retrieve_directory(self, directory_id):
        self.current_directory = self._organization_client.get_directory(directory_id)
        return self.current_directory

    def retrieve_all_directories(self):
        self.current_directories = \
            self._organization_client.get_all_directories()
        return self.current_directories

    def retrieve_directories(self, directory_ids):
        self.current_directories = \
            self._organization_client.get_directories(directory_ids)
        return self.current_directories

    def retrieve_directory_sdk_keys(self, directory_id):
        sdk_keys = self._organization_client.get_all_directory_sdk_keys(
            directory_id)
        self.current_sdk_keys = sdk_keys
        return self.current_sdk_keys

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
        self.current_public_keys = public_keys
        return public_keys

    def update_directory_public_key(self, key_id, directory_id,
                                    expires=False, active=None):
        self._organization_client.update_directory_public_key(
            directory_id, key_id, expires=expires, active=active)

    def remove_directory_public_key(self, key_id, directory_id):
        self._organization_client.remove_directory_public_key(
            directory_id, key_id)
