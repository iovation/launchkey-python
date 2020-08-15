"""Directory Client module"""

# pylint: disable=too-many-arguments

import warnings
from json import loads
from formencode import Invalid
from ..entities.validation import DirectoryGetDeviceResponseValidator, \
    DirectoryGetSessionsValidator, DirectoryUserDeviceLinkResponseValidator, \
    DirectoryDeviceLinkCompletionValidator, DirectoryUserTOTPValidator
from ..entities.directory import Session, DirectoryUserDeviceLinkData, Device,\
    DeviceLinkCompletionResponse, DirectoryUserTOTP
from .base import ServiceManagingBaseClient, api_call
from ..exceptions import UnableToDecryptWebhookRequest, \
    UnexpectedWebhookRequest, XiovJWTValidationFailure, \
    XiovJWTDecryptionFailure
from ..utils.shared import XiovJWTService


class DirectoryClient(ServiceManagingBaseClient):
    """
    Client for interacting with Directory endpoints
    """

    def __init__(self, subject_id, transport):
        super(DirectoryClient, self).__init__('dir', subject_id, transport,
                                              "/directory/v3/services")
        self.x_iov_jwt_service = XiovJWTService(self._transport, self._subject)

    @api_call
    def link_device(self, user_id, ttl=None):
        """
        Begin the process of Linking a Subscriber Authenticator Device with an
        End User based on the Directory User ID. If no Directory User exists
        for the Directory User ID, the Directory User will be created.
        :param user_id: Unique value identifying the End User in your
        system. It is the permanent link for the End
        User between the your application(s) and the LaunchKey API. This
        will be used for authorization requests as well as managing the End
        User's Devices.
        :param ttl: Number of seconds the linking code returned in the response
        should be valid. If no value is provided, the system default will be
        used.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.InvalidDirectoryIdentifier - Input
        identifier is invalid.
        :return: launchkey.entities.directory.DirectoryUserDeviceLinkData -
        Contains data needed to complete the linking process
        """
        kwargs = {"identifier": user_id}
        if ttl is not None:
            kwargs['ttl'] = ttl

        response = self._transport.post("/directory/v3/devices",
                                        self._subject,
                                        **kwargs)
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
        :param user_id: Unique value identifying the End User in your
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
        :param user_id: Unique value identifying the End User in your
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

    @api_call
    def generate_user_totp(self, user_id):
        """
        Generates, adds, and returns a TOTP secret for a given user identifier.

        Note that a user can only have a single TOTP configured. Submitting
        this request when there is an existing configuration will overwrite any
        previous settings.

        :param user_id: Unique value identifying the End User in your
        system. This value was used to create the Directory User and Link
        Device.
        :return: launchkey.entities.directory.DirectoryUserTOTP
        """
        response = self._transport.post("/directory/v3/totp",
                                        self._subject, identifier=user_id)
        validated_data = self._validate_response(
            response, DirectoryUserTOTPValidator)
        return DirectoryUserTOTP(validated_data)

    @api_call
    def remove_user_totp(self, user_id):
        """
        Removes a TOTP configuration from a given user.
        :param user_id: Unique value identifying the End User in your
        system. This value was used to create the Directory User and Link
        Device.
        :return:
        """
        self._transport.delete("/directory/v3/totp", self._subject,
                               identifier=user_id)

    def handle_webhook(self, body, headers, method, path):
        """
        Handle a webhook callback
        :param body: The raw body that was send in the POST content
        :param headers: A generic map of response headers. These will be used
        to access and validate authorization
        :param path:  The path of the request
        :param method: The HTTP method of the request
        :return: launchkey.entities.directory.
        DirectoryUserDeviceLinkCompletionWebhookPackage
        :raises launchkey.exceptions.UnexpectedWebhookRequest: when the
        request or its cannot be parsed or fails
        validation.
        :raises launchkey.exceptions.UnableToDecryptWebhookRequest: when the
        request is an authorization response webhook and the request body
        cannot be decrypted
        :raises launchkey.exceptions.UnexpectedKeyID: when the auth package in
        an authorization response webhook request body is decrypted using a
        public key whose private key is not known by the client. This can be
        a configuration issue.
        :raises launchkey.exceptions.WebhookAuthorizationError: when the
        "Authorization" header in the headers.
        """
        result = None
        try:
            decrypted_body = self.x_iov_jwt_service.decrypt_jwe(body, headers,
                                                                method, path)
            payload = loads(decrypted_body)
            device_link_data = DirectoryDeviceLinkCompletionValidator(
            ).to_python(payload)
            result = DeviceLinkCompletionResponse(
                device_link_data
            )
        except Invalid:
            warnings.warn("Invalid Directory Webhook received. There may be"
                          " an update available to add support.")
        except XiovJWTDecryptionFailure as reason:
            raise UnableToDecryptWebhookRequest(reason=reason)
        except XiovJWTValidationFailure as reason:
            raise UnexpectedWebhookRequest(reason)

        return result
