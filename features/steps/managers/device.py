from logging import getLogger

logger = getLogger(__name__)


class DeviceManager:
    def __init__(self, organization_factory, directory_manager):
        self.organization_factory = organization_factory
        self.directory_manager = directory_manager
        self.current_device_list = []
        self.current_user_identifier = None
        self.directory_user_identifiers = dict()
        self.current_linking_response = None

    def cleanup_devices(self):
        for directory_id, user_identifier_list in \
                self.directory_user_identifiers.items():
            logger.info("Cleaning up directory: %s users" % directory_id)

            self.directory_manager.update_directory(directory_id=directory_id,
                                                    active=True)
            for user_identifier in user_identifier_list:
                logger.info("Cleaning up user: %s devices" % user_identifier)
                for device in self.retrieve_user_devices(
                        user_identifier, directory_id=directory_id):
                    logger.info("Unlinking Device: %s" % device.id)
                    self.unlink_device(device.id,
                                       user_identifier=user_identifier,
                                       directory_id=directory_id)
            self.directory_manager.update_directory(active=False)
        self.directory_user_identifiers = {}

    def create_linking_request(self, user_identifier=None, ttl=None,
                               directory_id=None):
        if user_identifier is None:
            user_identifier = self.current_user_identifier
        self.current_user_identifier = user_identifier

        directory = self.directory_manager.current_directory
        directory_client = self.directory_manager.get_directory_client(
            directory_id=directory_id)
        self.current_linking_response = directory_client.link_device(
            user_identifier, ttl=ttl)
        if self.directory_user_identifiers.get(directory.id):
            self.directory_user_identifiers[directory.id].add(user_identifier)
        else:
            self.directory_user_identifiers[directory.id] = {user_identifier}

    def retrieve_user_devices(self, user_identifier=None, directory_id=None):
        if user_identifier is None:
            user_identifier = self.current_user_identifier
        directory_client = self.directory_manager.get_directory_client(
            directory_id=directory_id)
        devices = directory_client.get_linked_devices(user_identifier)
        self.current_device_list = devices
        return self.current_device_list

    def unlink_device(self, device_id, user_identifier=None,
                      directory_id=None):
        if user_identifier is None:
            user_identifier = self.current_user_identifier
        directory_client = self.directory_manager.get_directory_client(
            directory_id=directory_id)
        directory_client.unlink_device(user_identifier, device_id)






