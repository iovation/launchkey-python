from .base import BaseClient, api_call
from launchkey.utils import iso_format
from launchkey.entities.validation import DirectoryGetDeviceResponseValidator, DirectoryGetSessionsValidator, \
    DirectoryUserDeviceLinkResponseValidator, ServiceValidator, ServiceSecurityPolicyValidator, PublicKeyValidator
from launchkey.entities.service import Service, ServiceSecurityPolicy
from launchkey.entities.directory import Session, DirectoryUserDeviceLinkData, Device
from launchkey.entities.shared import PublicKey


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
        :return: launchkey.entities.directory.DirectoryUserDeviceLinkData - Contains data needed to complete the
                                                                            linking process
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
        :return: List - An list of launchkey.entities.directory.Device objects for the specified user identifier.
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
        self._transport.delete("/directory/v3/devices", self._subject, identifier=user_id, device_id=str(device_id))

    @api_call
    def end_all_service_sessions(self, user_id):
        """
        End Service User Sessions for all Services in which a Session was started for the Directory User
        :param user_id: Unique value identifying the End User in your system. This value was used to create the
        Directory User and Link Device.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.EntityNotFound - The user was not found.
        """
        self._transport.delete("/directory/v3/sessions", self._subject, identifier=user_id)

    @api_call
    def get_all_service_sessions(self, user_id):
        """
        Retrieves all Service Sessions that belong to a User
        :param user_id: Unique value identifying the End User in your system. This value was used to create the
        Directory User and Link Device.
        :raise: launchkey.exceptions.EntityNotFound - The input user identifier does not exist in your directory, or
                                                      it does not have any devices linked to it
        :return: List - launchkey.entities.directory.Session
        """
        return [Session(self._validate_response(session, DirectoryGetSessionsValidator)) for session in
                self._transport.post("/directory/v3/sessions/list", self._subject, identifier=user_id).data]

    @api_call
    def create_service(self, name, description=None, icon=None, callback_url=None, active=True):
        """
        Creates a Directory Service
        :param name: Unique name that will be displayed in an Auth Request
        :param description: Optional description that can be viewed in the Admin Center or when retrieving the Service.
        :param icon: Optional URL to an icon that will be displayed in an Auth Request
        :param callback_url: URL that Webhooks will be sent to
        :param active: Whether the Service should be able to send Auth Requests
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.ServiceNameTaken - Service name already taken
        :return: String - ID of the Service that is created
        """
        return self._transport.post("/directory/v3/services", self._subject, name=name, description=description,
                                    icon=icon, callback_url=callback_url, active=active).data['id']

    @api_call
    def get_all_services(self):
        """
        Retrieves all Services belonging to a Directory
        :return: List - launchkey.entities.service.Service object containing Service details
        """
        return [Service(self._validate_response(service, ServiceValidator)) for service in
                self._transport.get("/directory/v3/services", self._subject).data]

    @api_call
    def get_services(self, service_ids):
        """
        Retrieves Services based on an input list of Service IDs
        :param service_ids: List of unique Service IDs
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :return: List - launchkey.entities.service.Service object containing Service details
        """
        return [Service(self._validate_response(service, ServiceValidator)) for service in
                self._transport.post("/directory/v3/services/list", self._subject,
                                     service_ids=[str(service_id) for service_id in service_ids]).data]

    @api_call
    def get_service(self, service_id):
        """
        Retrieves a Service based on an input Service ID
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :return: launchkey.entities.service.Service object containing Service details
        """
        return Service(self._validate_response(
            self._transport.post("/directory/v3/services/list", self._subject, service_ids=[str(service_id)]).data[0],
            ServiceValidator))

    @api_call
    def update_service(self, service_id, name=False, description=False, icon=False, callback_url=False, active=None):
        """
        Updates a Service's general settings. If an optional parameter is not included it will not be updated.
        :param service_id: Unique Service ID
        :param name: Unique name that will be displayed in an Auth Request
        :param description: Description that can be viewed in the Admin Center or when retrieving the Service.
        :param icon: URL to an icon that will be displayed in an Auth Request
        :param callback_url: URL that Webhooks will be sent to
        :param active: Whether the Service should be able to send Auth Requests
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.ServiceNameTaken - Service name already taken
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be found matching the input ID
        :raise: launchkey.exceptions.Forbidden - The Service you requested either does not exist or you do not have
                                                 sufficient permissions.
        :return:
        """
        kwargs = {"service_id": str(service_id)}
        if name is not False:
            kwargs['name'] = name
        if description is not False:
            kwargs['description'] = description
        if icon is not False:
            kwargs['icon'] = icon
        if callback_url is not False:
            kwargs['callback_url'] = callback_url
        if active is not None:
            kwargs['active'] = active
        self._transport.patch("/directory/v3/services", self._subject, **kwargs)

    @api_call
    def add_service_public_key(self, service_id, public_key, expires=None, active=None):
        """
        Adds a public key to a Directory Service
        :param service_id: Unique Service ID
        :param public_key: String RSA public key
        :param expires: Optional datetime.datetime stating a time in which the key will no longer be valid
        :param active: Optional bool stating whether the key should be considered active and usable.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.InvalidPublicKey - The public key you supplied is not valid.
        :raise: launchkey.exceptions.PublicKeyAlreadyInUse - The public key you supplied already exists for the
                                                                requested entity. It cannot be added again.
        :raise: launchkey.exceptions.Forbidden - The Service you requested either does not exist or you do not have
                                                 sufficient permissions.
        :return: MD5 fingerprint (key_id) of the public key, IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        """
        kwargs = {"service_id": str(service_id), "public_key": public_key}
        if expires is not None:
            kwargs['date_expires'] = iso_format(expires)
        if active is not None:
            kwargs['active'] = active
        return self._transport.post("/organization/v3/service/keys", self._subject, **kwargs).data['key_id']

    @api_call
    def remove_service_public_key(self, service_id, key_id):
        """
        Removes a public key from a Directory Service. You may only remove a public key if other public keys exist.
        If you wish for a last remaining key to no longer be usable, use update_service_public_key to instead and set it
        as inactive.
        :param service_id: Unique Service ID
        :param key_id: MD5 fingerprint of the public key, IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.PublicKeyDoesNotExist - The key_id you supplied could not be found
        :raise: launchkey.exceptions.LastRemainingKey - The last remaining public key cannot be removed
        :raise: launchkey.exceptions.Forbidden - The Service you requested either does not exist or you do not have
                                                 sufficient permissions.
        :return:
        """
        self._transport.delete("/directory/v3/service/keys", self._subject, service_id=str(service_id),
                               key_id=key_id)

    @api_call
    def get_service_public_keys(self, service_id):
        """
        Retrieves a list of Public Keys belonging to a Service
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be found matching the input ID
        :raise: launchkey.exceptions.Forbidden - The Service you requested either does not exist or you do not have
                                                 sufficient permissions.
        :return: List - launchkey.entities.shared.PublicKey
        """
        return [PublicKey(self._validate_response(key, PublicKeyValidator)) for key in
                self._transport.post("/directory/v3/service/keys/list", self._subject,
                                     service_id=str(service_id)).data]

    @api_call
    def update_service_public_key(self, service_id, key_id, expires=False, active=None):
        """
        Removes a public key from an Directory Service
        :param service_id: Unique Service ID
        :param key_id: MD5 fingerprint of the public key, IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        :param expires: datetime.datetime stating a time in which the key will no longer be valid
        :param active: Bool stating whether the key should be considered active and usable
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.PublicKeyDoesNotExist - The key_id you supplied could not be found
        :raise: launchkey.exceptions.Forbidden - The Service you requested either does not exist or you do not have
                                                 sufficient permissions.
        :return:
        """
        kwargs = {"service_id": str(service_id), "key_id": key_id}
        if active is not None:
            kwargs['active'] = active
        if expires is not False:
            kwargs['date_expires'] = iso_format(expires)
        self._transport.patch("/directory/v3/service/keys", self._subject, **kwargs)

    @api_call
    def get_service_policy(self, service_id):
        """
        Retrieves a Service's Security Policy
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be found matching the input ID
        :return: launchkey.entities.service.ServiceSecurityPolicy object containing policy details
        """
        policy = ServiceSecurityPolicy()
        policy.set_policy(self._validate_response(
            self._transport.post("/directory/v3/service/policy/item", self._subject, service_id=str(service_id)).data,
            ServiceSecurityPolicyValidator))
        return policy

    @api_call
    def set_service_policy(self, service_id, policy):
        """
        Sets a Service's Security Policy
        :param service_id: Unique Service ID
        :param policy: launchkey.clients.shared.ServiceSecurityPolicy
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be found matching the input ID
        :return:
        """
        self._transport.put("/directory/v3/service/policy", self._subject, service_id=str(service_id),
                            policy=policy.get_policy())

    @api_call
    def remove_service_policy(self, service_id):
        """
        Resets a Service's Security Policy back to default
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be found matching the input ID
        :return:
        """
        self._transport.delete("/directory/v3/service/policy", self._subject, service_id=str(service_id))
