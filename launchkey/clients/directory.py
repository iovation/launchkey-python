from .base import BaseClient, api_call
from formencode import Schema, validators
from launchkey.exceptions import InvalidDeviceStatus


class DirectoryUserDeviceLinkResponseValidator(Schema):
    qrcode = validators.String()  # URL
    code = validators.String(min=7)
    allow_extra_fields = True


class DirectoryGetDeviceResponseValidator(Schema):
    id = validators.String()
    name = validators.String()
    status = validators.Int()
    type = validators.String()
    allow_extra_fields = True


class DirectoryUserDeviceLinkData(object):
    """Directory user device data used to finish the linking process"""

    def __init__(self, data):
        self.qrcode = data['qrcode']
        self.code = data['code']


class DeviceStatus(object):
    """Activation status of a directory user's device"""

    _status_map = {
        0: ("LINK_PENDING", False),
        1: ("LINKED", True),
        2: ("UNLINK_PENDING", True)
    }

    def __init__(self, status_code):
        if status_code not in self._status_map:
            raise InvalidDeviceStatus("Status code %s was not recognized" % status_code)
        self._status_code = status_code

    @property
    def is_active(self):
        return self._status_map[self._status_code][1]

    @property
    def status_code(self):
        return self._status_map[self._status_code][0]


class Device(object):
    """Device object belonging to a directory user"""

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.status = DeviceStatus(data['status'])
        self.type = data['type']


class DirectoryClient(BaseClient):

    def __init__(self, subject_id, transport):
        super(DirectoryClient, self).__init__('dir', subject_id, transport)

    @api_call
    def link_device(self, user_id):
        """
        Begin the process of Linking a Subscriber Authenticator Device with an End User based on the Directory User ID.
        If no Directory User exists for the Directory User ID, the Directory User will be created.
        :param user_id: Unique value identifying the End User in the your system. It is the permanent link for the End
        User between the your application(s) and the LaunchKey API. This will be used for authorization requests as
        well as managing the End User's Devices.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.InvalidDirectoryIdentifier - Input identifier is invalid.
        :return: DirectoryUserDeviceLinkData - Contains data needed to complete the linking process
        """
        response = self._transport.post("/directory/v3/devices", self._subject, identifier=user_id)
        data = self._validate_response(response, DirectoryUserDeviceLinkResponseValidator)
        return DirectoryUserDeviceLinkData(data)

    @api_call
    def get_linked_devices(self, user_id):
        """
        Get a list of Subscriber Authenticator Devices for a Directory User. If not Directory User exists for the
        Directory User ID, an empty list will be returned.
        :param user_id: Unique value identifying the End User in the your system. This value was used to create the
        Directory User and Link Device.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :return: List - An list of Device objects for the specified user identifier.
        """
        return [Device(self._validate_response(d, DirectoryGetDeviceResponseValidator)) for d in
                self._transport.post("/directory/v3/devices/list", self._subject, identifier=user_id).data]

    @api_call
    def unlink_device(self, user_id, device_id):
        """
        Unlink a users device
        :param user_id: Unique value identifying the End User in the your system. This value was used to create the
        Directory User and Link Device.
        :param device_id: The unique identifier of the Device you wish to Unlink. It would be obtained via Device.id
        returned by get_linked_devices().
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.EntityNotFound - The input device was not found. It may already be unlinked.
        """
        self._transport.delete("/directory/v3/devices", self._subject, identifier=user_id, device_id=device_id)

    @api_call
    def end_all_service_sessions(self, user_id):
        """
        End Service User Sessions for all Services in which a Session was started for the Directory User
        :param user_id:Unique value identifying the End User in the your system. This value was used to create the
        Directory User and Link Device.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.EntityNotFound - The user was not found.
        """
        self._transport.delete("/directory/v3/sessions", self._subject, identifier=user_id)
