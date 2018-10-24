"""Directory Client module"""

# pylint: disable=too-many-arguments

from ..entities.validation import DirectoryGetDeviceResponseValidator, \
    DirectoryGetSessionsValidator, DirectoryUserDeviceLinkResponseValidator
from ..entities.directory import Session, DirectoryUserDeviceLinkData, Device
from .base import ServiceManagingBaseClient, api_call


class DirectoryClient(ServiceManagingBaseClient):
    """
    Client for interacting with Directory endpoints
    """

    def __init__(self, subject_id, transport):
        super(DirectoryClient, self).__init__('dir', subject_id, transport,
                                              "/directory/v3/services")

    @api_call
    def link_device(self, user_id):
        """
        Begin the process of Linking a Subscriber Authenticator Device with an
        End User based on the Directory User ID. If no Directory User exists
        for the Directory User ID, the Directory User will be created.
        :param user_id: Unique value identifying the End User in the your
        system. It is the permanent link for the End
        User between the your application(s) and the LaunchKey API. This
        will be used for authorization requests as well as managing the End
        User's Devices.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.InvalidDirectoryIdentifier - Input
        identifier is invalid.
        :return: launchkey.entities.directory.DirectoryUserDeviceLinkData -
        Contains data needed to complete the linking process
        """
        response = self._transport.post("/directory/v3/devices",
                                        self._subject,
                                        identifier=user_id)
        data = self._validate_response(
            response,
            DirectoryUserDeviceLinkResponseValidator)
        return DirectoryUserDeviceLinkData(data)

    @api_call
    def get_linked_devices(self, user_id):
        """
        Get a list of Subscriber Authenticator Devices for a Directory User.
        If not Directory User exists for the Directory User ID, an empty
        list will be returned.
        :param user_id: Unique value identifying the End User in the your
        system. This value was used to create the Directory User and Link
        Device.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :return: List - An list of launchkey.entities.directory.Device objects
        for the specified user identifier.
        """
        response = self._transport.post("/directory/v3/devices/list",
                                        self._subject, identifier=user_id)

        devices = [
            Device(
                self._validate_response(d, DirectoryGetDeviceResponseValidator)
            ) for d in response.data
        ]
        return devices

    @api_call
    def unlink_device(self, user_id, device_id):
        """
        Unlink a users device
        :param user_id: Unique value identifying the End User in the your
        system. This value was used to create the Directory User and Link
        Device.
        :param device_id: The unique identifier of the Device you wish to
        Unlink. It would be obtained via Device.id returned by
        get_linked_devices().
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.EntityNotFound - The input device was not
        found. It may already be unlinked.
        """
        self._transport.delete("/directory/v3/devices", self._subject,
                               identifier=user_id, device_id=str(device_id))

    @api_call
    def end_all_service_sessions(self, user_id):
        """
        End Service User Sessions for all Services in which a Session was
        started for the Directory User
        :param user_id: Unique value identifying the End User in your system.
        This value was used to create the Directory User and Link Device.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.EntityNotFound - The user was not found.
        """
        self._transport.delete("/directory/v3/sessions", self._subject,
                               identifier=user_id)

    @api_call
    def get_all_service_sessions(self, user_id):
        """
        Retrieves all Service Sessions that belong to a User
        :param user_id: Unique value identifying the End User in your system.
        This value was used to create the Directory User and Link Device.
        :raise: launchkey.exceptions.EntityNotFound - The input user identifier
        does not exist in your directory, or it does not have any devices
        linked to it
        :return: List - launchkey.entities.directory.Session
        """
        sessions = []
        response = self._transport.post("/directory/v3/sessions/list",
                                        self._subject, identifier=user_id)
        for session in response.data:
            validated_data = self._validate_response(
                session, DirectoryGetSessionsValidator)

            session = Session(validated_data)
            sessions.append(session)

        return sessions
