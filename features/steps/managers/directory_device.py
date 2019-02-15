from .base import BaseManager


class UserNotCreated(Exception):
    """A User was requested but none existed"""


class NoCurrentLinkingResponse(Exception):
    """A linking request has not been made"""


class DeviceNotCreated(Exception):
    """A Device was requested but none existed"""


class DirectoryDeviceManager(BaseManager):
    def __init__(self, organization_factory):
        self.current_device_list = []
        self.previous_user_identifier = None
        self.current_user_identifier = None
        self.previous_device = None
        self.current_device = None
        self.directory_user_identifiers = dict()
        self.previous_linking_response = None
        self.current_linking_response = None
        BaseManager.__init__(self, organization_factory)

    def cleanup(self):
        for directory_id, user_identifier_list in \
                self.directory_user_identifiers.items():
            self.log_info("Cleaning up directory: %s users" % directory_id)

            self._organization_client.update_directory(
                directory_id=directory_id, active=True)
            for user_identifier in user_identifier_list:
                self.log_info("Cleaning up user: %s devices" %
                              user_identifier)
                for device in self.retrieve_user_devices(
                        user_identifier, directory_id=directory_id):
                    self.log_info("Unlinking Device: %s" % device.id)
                    self.unlink_device(device.id,
                                       user_identifier=user_identifier,
                                       directory_id=directory_id)
        self.current_device_list = []
        self.current_user_identifier = None
        self.directory_user_identifiers = dict()
        self.current_linking_response = None

    @property
    def current_user_identifier(self):
        # @todo determine whether we want to enforce a pre-existing user identifier
        # if self._current_user_identifier is None:
        #     raise UserNotCreated("A user has not been created yet.")
        return self._current_user_identifier

    @current_user_identifier.setter
    def current_user_identifier(self, value):
        self.previous_user_identifier = getattr(
            self, "_current_user_identifier", None)
        self._current_user_identifier = value

    @property
    def current_device(self):
        if self._current_device is None:
            raise DeviceNotCreated("A device has not been created yet.")
        return self._current_device

    @current_device.setter
    def current_device(self, value):
        self.previous_device = getattr(
            self, "_current_device", None)
        self._current_device = value

    @property
    def current_linking_response(self):
        if self._current_linking_response is None:
            raise NoCurrentLinkingResponse("A linking request has not been "
                                           "made yet.")
        return self._current_linking_response

    @current_linking_response.setter
    def current_linking_response(self, value):
        self.previous_linking_response = getattr(
            self, "_current_linking_response", None)
        self._current_linking_response = value

    def create_linking_request(self, user_identifier, directory_id, ttl=None):
        self.current_user_identifier = user_identifier
        directory_client = self._get_directory_client(
            directory_id=directory_id)
        self.current_linking_response = directory_client.link_device(
            user_identifier, ttl=ttl)
        if self.directory_user_identifiers.get(directory_id):
            self.directory_user_identifiers[directory_id].add(user_identifier)
        else:
            self.directory_user_identifiers[directory_id] = {user_identifier}

    def retrieve_user_devices(self, user_identifier, directory_id):
        directory_client = self._get_directory_client(
            directory_id=directory_id)
        devices = directory_client.get_linked_devices(user_identifier)
        self.current_device_list = devices

        if self.current_device_list:
            self.current_device = self.current_device_list[0]
        else:
            self.current_device = None

        return self.current_device_list

    def unlink_device(self, device_id, user_identifier, directory_id):
        directory_client = self._get_directory_client(
            directory_id=directory_id)
        directory_client.unlink_device(user_identifier, device_id)
        self.current_device = None
