from logging import getLogger
from uuid import uuid4

from launchkey.exceptions import Forbidden

logger = getLogger(__name__)


class DirectoryManager:

    def __init__(self, organization_factory):
        self.organization_factory = organization_factory
        self.directories = []
        self.current_directory_entity_list = []  # Look into removing
        self.current_sdk_keys = []
        self.current_directory = None
        self.previous_directory = None
        self.client = self.organization_factory.make_organization_client()
        self.current_public_keys = []

    def cleanup_state(self):
        self.current_directory = None
        self.previous_directory = None
        self.current_directory_entity_list = []
        self.current_sdk_keys = []
        self.current_public_keys = []

    def cleanup_directories(self):
        for directory in self.directories:
            logger.info("Cleaning up directory: %s" % directory.id)
            self.update_directory(directory.id, active=True)
            directory = self.client.get_directory(directory.id)
            try:
                directory_client = self.organization_factory.make_directory_client(
                    directory.id
                )
                for service_id in directory.service_ids:
                    try:
                        directory_client.update_service(service_id, active=False)
                    except Forbidden as e:
                        logger.error(
                            "Unable Directory Service to inactive for "
                            "Directory %s due to error %s." % (directory.id, e)
                        )
                self.update_directory(directory.id, active=False)
            except Exception as e:
                logger.error(
                    "Unable to deactivate Directory %s or it's Services due "
                    "to error %s" % (directory.id, e)
                )
        self.directories = []

    def get_directory_client(self, directory_id=None):
        if directory_id is None:
            directory_id = self.current_directory.id
        return self.organization_factory.make_directory_client(directory_id)

    def create_directory(self, name=None):
        if name is None:
            name = str(uuid4())
        directory_id = self.client.create_directory(name)
        self.previous_directory = self.current_directory
        directory = self.client.get_directory(directory_id)
        self.current_directory = directory
        self.directories.append(directory)
        return self.current_directory

    def get_any_directory(self):
        return self.current_directory if self.current_directory is not None \
            else self.create_directory()

    def update_directory(self, directory_id=None, ios_p12=False,
                         android_key=False, active=None,
                         denial_context_inquiry_enabled=None):
        if directory_id is None:
            directory_id = self.current_directory.id
        self.client.update_directory(
            directory_id,
            ios_p12=ios_p12,
            android_key=android_key,
            active=active,
            denial_context_inquiry_enabled=denial_context_inquiry_enabled
        )

    def generate_and_add_directory_sdk_key_to_directory(self,
                                                        directory_id=None):
        if directory_id is None:
            directory_id = self.current_directory.id
        return self.client.generate_and_add_directory_sdk_key(
            directory_id
        )

    def retrieve_directory(self, directory_id):
        return self.client.get_directory(directory_id)

    def retrieve_all_directories(self):
        return self.client.get_all_directories()

    def retrieve_directory_sdk_keys(self, directory_id):
        # if directory_id is None:
        #     directory_id = self.current_directory.id
        raise NotImplemented()

    def remove_sdk_key_from_directory(self, sdk_key, directory_id=None):
        if directory_id is None:
            directory_id = self.current_directory.id
        self.client.remove_directory_sdk_key(directory_id, sdk_key)

    def add_public_key_to_directory(self, public_key, directory_id=None):
        self.client.add_directory_public_key(
            directory_id,
            public_key.public_key,
            expires=public_key.expires,
            active=public_key.active
        )

    def retrieve_directory_public_keys(self, directory_id=None):
        if directory_id is None:
            directory_id = self.current_directory.id
        public_keys = self.client.get_directory_public_keys(directory_id)
        if directory_id == self.current_directory.id:
            self.current_public_keys = public_keys
        return public_keys

    def update_directory_public_key(self, key_id, directory_id=None,
                                    expires=False, active=None):
        if directory_id is None:
            directory_id = self.current_directory
        self.client.update_directory_public_key(directory_id, key_id,
                                                expires=expires, active=active)
        if directory_id == self.current_directory.id:
            # If we update the current directory, trigger a refresh on its keys
            self.retrieve_directory_public_keys()

    def remove_directory_public_key(self, key_id, directory_id=None):
        if directory_id is None:
            directory_id = self.current_directory
        self.client.remove_directory_public_key(directory_id, key_id)
