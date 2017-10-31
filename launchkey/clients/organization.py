from .base import BaseClient, api_call
from launchkey.utils import iso_format
from launchkey.entities.shared import PublicKey
from launchkey.entities.service import Service, ServiceSecurityPolicy
from launchkey.entities.directory import Directory
from launchkey.entities.validation import DirectoryValidator, ServiceValidator, ServiceSecurityPolicyValidator, \
    PublicKeyValidator
try:
    from base64 import encodebytes as encodestring
except ImportError:
    from base64 import encodestring


class OrganizationClient(BaseClient):

    def __init__(self, subject_id, transport):
        super(OrganizationClient, self).__init__('org', subject_id, transport)

    @api_call
    def create_service(self, name, description=None, icon=None, callback_url=None, active=True):
        """
        Creates an Organization Service
        :param name: Unique name that will be displayed in an Auth Request
        :param description: Optional description that can be viewed in the Admin Center or when retrieving the Service.
        :param icon: Optional URL to an icon that will be displayed in an Auth Request
        :param callback_url: URL that Webhooks will be sent to
        :param active: Whether the Service should be able to send Auth Requests
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.ServiceNameTaken - Service name already taken
        :return: String - ID of the Service that is created
        """
        return self._transport.post("/organization/v3/services", self._subject, name=name, description=description,
                                    icon=icon, callback_url=callback_url, active=active).data['id']

    @api_call
    def get_all_services(self):
        """
        Retrieves all Services belonging to an Organization
        :return: List - launchkey.entities.service.Service object containing Service details
        """
        return [Service(self._validate_response(service, ServiceValidator)) for service in
                self._transport.get("/organization/v3/services", self._subject).data]

    @api_call
    def get_services(self, service_ids):
        """
        Retrieves Services based on an input list of Service IDs
        :param service_ids: List of unique Service IDs
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :return: List - launchkey.entities.service.Service object containing Service details
        """
        return [Service(self._validate_response(service, ServiceValidator)) for service in
                self._transport.post("/organization/v3/services/list", self._subject,
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
            self._transport.post("/organization/v3/services/list", self._subject,
                                 service_ids=[str(service_id)]).data[0], ServiceValidator))

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
        self._transport.patch("/organization/v3/services", self._subject, **kwargs)

    @api_call
    def add_service_public_key(self, service_id, public_key, expires=None, active=None):
        """
        Adds a public key to an Organization Service
        :param service_id: Unique Service ID
        :param public_key: String RSA public key
        :param expires: Optional datetime.datetime stating a time in which the key will no longer be valid
        :param active: Optional bool stating whether the key should be considered active and usable.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.InvalidPublicKey - The public key you supplied is not valid.
        :raise: launchkey.exceptions.PublicKeyAlreadyInUse - The public key you supplied already exists for the
                                                                requested entity. It cannot be yadded again.
        :return: MD5 fingerprint (key_id) of the public key, IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        """
        kwargs = {"service_id": str(service_id), "public_key": public_key}
        if expires is not None:
            kwargs['date_expires'] = iso_format(expires)
        if active is not None:
            kwargs['active'] = active
        return self._transport.post("/organization/v3/service/keys", self._subject, **kwargs).data['key_id']

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
                self._transport.post("/organization/v3/service/keys/list", self._subject,
                                     service_id=str(service_id)).data]

    @api_call
    def remove_service_public_key(self, service_id, key_id):
        """
        Removes a public key from an Organization Service. You may only remove a public key if other public keys exist.
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
        self._transport.delete("/organization/v3/service/keys", self._subject, service_id=str(service_id),
                               key_id=key_id)

    @api_call
    def update_service_public_key(self, service_id, key_id, expires=False, active=None):
        """
        Removes a public key from an Organization Service
        :param service_id: Unique Service ID
        :param key_id: MD5 fingerprint of the public key, IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        :param expires: datetime.datetime stating a time in which the key will no longer be valid
        :param active: Bool stating whether the key should be considered active and usable
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
        self._transport.patch("/organization/v3/service/keys", self._subject, **kwargs)

    @api_call
    def get_service_policy(self, service_id):
        """
        Retrieves a Service's Security Policy
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be found matching the input ID
        :return: launchkey.entities.service.ServiceSecurityPolicy object containing policy details
        """
        policy = ServiceSecurityPolicy()
        policy.set_policy(self._validate_response(
            self._transport.post("/organization/v3/service/policy/item", self._subject,
                                 service_id=str(service_id)).data,
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
        self._transport.put("/organization/v3/service/policy", self._subject, service_id=str(service_id),
                            policy=policy.get_policy())

    @api_call
    def remove_service_policy(self, service_id):
        """
        Resets a Service's Security Policy back to default
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be found matching the input ID
        :return:
        """
        self._transport.delete("/organization/v3/service/policy", self._subject, service_id=str(service_id))

    @api_call
    def create_directory(self, name):
        """
        Creates a new Directory
        :param name: Name describing the Directory that can be viewed in the Admin Center
        :return: String - ID of the Directory that is created
        """
        return self._transport.post("/organization/v3/directories", self._subject, name=name).data['id']

    @api_call
    def get_all_directories(self):
        """
        Retrieves all Directories belonging to an Organization
        :return: List - launchkey.entities.directory.Directory object containing Directory details
        """
        return [Directory(self._validate_response(directory, DirectoryValidator)) for directory in
                self._transport.get("/organization/v3/directories", self._subject).data]

    @api_call
    def get_directories(self, directory_ids):
        """
        Retrieves a list of Directories belonging to an Organization
        :param directory_ids: List of unique Directory IDs
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :return: List - launchkey.entities.directory.Directory object containing Directory details
        """
        return [Directory(self._validate_response(directory, DirectoryValidator)) for directory in
                self._transport.post("/organization/v3/directories/list", self._subject,
                                     directory_ids=[str(directory_id) for directory_id in directory_ids]).data]

    @api_call
    def get_directory(self, directory_id):
        """
        Retrieves a Directory based on an input Directory ID
        :param directory_id: Unique Directory ID
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :return: launchkey.entities.directory.Directory object containing Directory details
        """
        return Directory(self._validate_response(
            self._transport.post("/organization/v3/directories/list", self._subject,
                                 directory_ids=[str(directory_id)]).data[0], DirectoryValidator))

    @api_call
    def update_directory(self, directory_id, ios_p12=False, android_key=False, active=None):
        """
        Updates a Directories's settings. If an optional parameter is not included it will not be updated.
        :param directory_id: Unique Directory ID
        :param ios_p12: MPNS P12 formatted push key containing both private key and cert (must be password free)
        :param android_key: GCM Push Key
        :param active: Boolean. Status preventing Directory Service Auths as well as other Directory related calls.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :return:
        """
        kwargs = {"directory_id": str(directory_id)}
        if ios_p12 is not False:
            kwargs['ios_p12'] = encodestring(ios_p12).decode('utf-8') if ios_p12 else ios_p12
        if android_key is not False:
            kwargs['android_key'] = android_key
        if active is not None:
            kwargs['active'] = active
        self._transport.patch("/organization/v3/directories", self._subject, **kwargs)

    @api_call
    def get_directory_public_keys(self, directory_id):
        """
        Retrieves a list of Public Keys belonging to a Directory
        :param directory_id: Unique Directory ID
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.Forbidden - The Directory you requested either does not exist or you do not have
                                                 sufficient permissions.
        :return: List - launchkey.entities.shared.PublicKey
        """
        return [PublicKey(self._validate_response(key, PublicKeyValidator)) for key in
                self._transport.post("/organization/v3/directory/keys/list", self._subject,
                                     directory_id=str(directory_id)).data]

    @api_call
    def add_directory_public_key(self, directory_id, public_key, expires=None, active=None):
        """
        Adds a public key to an Directory
        :param directory_id: Unique Directory ID
        :param public_key: String RSA public key
        :param expires: Optional datetime.datetime stating a time in which the key will no longer be valid
        :param active: Optional bool stating whether the key should be considered active and usable.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.InvalidPublicKey - The public key you supplied is not valid.
        :raise: launchkey.exceptions.PublicKeyAlreadyInUse - The public key you supplied already exists for the
                                                                requested entity. It cannot be added again.
        :raise: launchkey.exceptions.Forbidden - The Directory you requested either does not exist or you do not have
                                                 sufficient permissions.
        :return: MD5 fingerprint (key_id) of the public key, IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        """
        kwargs = {"directory_id": str(directory_id), "public_key": public_key}
        if expires is not None:
            kwargs['date_expires'] = iso_format(expires)
        if active is not None:
            kwargs['active'] = active
        return self._transport.post("/organization/v3/directory/keys", self._subject, **kwargs).data['key_id']

    @api_call
    def remove_directory_public_key(self, directory_id, key_id):
        """
        Removes a public key from a Directory. You may only remove a public key if other public keys exist.
        If you wish for a last remaining key to no longer be usable, use update_service_public_key to instead and set it
        as inactive.
        :param directory_id: Unique Directory ID
        :param key_id: MD5 fingerprint of the public key, IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.PublicKeyDoesNotExist - The key_id you supplied could not be found.
        :raise: launchkey.exceptions.LastRemainingKey - The last remaining public key cannot be removed.
        :raise: launchkey.exceptions.Forbidden - The Directory you requested either does not exist or you do not have
                                                 sufficient permissions.
        :return:
        """
        self._transport.delete("/organization/v3/directory/keys", self._subject, directory_id=str(directory_id),
                               key_id=key_id)

    @api_call
    def update_directory_public_key(self, directory_id, key_id, expires=False, active=None):
        """
        Removes a public key from a Directory
        :param directory_id: Unique Directory ID
        :param key_id: MD5 fingerprint of the public key, IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        :param expires: datetime.datetime stating a time in which the key will no longer be valid
        :param active: Bool stating whether the key should be considered active and usable
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.PublicKeyDoesNotExist - The key_id you supplied could not be found.
        :raise: launchkey.exceptions.Forbidden - The Directory you requested either does not exist or you do not have
                                                 sufficient permissions.
        :return:
        """
        kwargs = {"directory_id": str(directory_id), "key_id": key_id}
        if active is not None:
            kwargs['active'] = active
        if expires is not False:
            kwargs['date_expires'] = iso_format(expires)
        self._transport.patch("/organization/v3/directory/keys", self._subject, **kwargs)

    @api_call
    def generate_and_add_directory_sdk_key(self, directory_id):
        """
        Creates and retrieves a new Authenticator SDK Key for a Directory
        :param directory_id: Unique Directory ID
        :return: String - Newly generated Authenticator SDK Key
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        """
        return self._transport.post("/organization/v3/directory/sdk-keys",
                                    self._subject, directory_id=str(directory_id)).data['sdk_key']

    @api_call
    def remove_directory_sdk_key(self, directory_id, sdk_key):
        """
        Removes an Authenticator SDK Key from a Directory
        :param directory_id: Unique Directory ID
        :param sdk_key: Authenticator SDK Key
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.LastRemainingSDKKey - The last remaining SDK key cannot be removed
        :raise: launchkey.exceptions.InvalidSDKKey - The input SDK key does not belong to the given Directory
        :return:
        """
        self._transport.delete("/organization/v3/directory/sdk-keys", self._subject, directory_id=str(directory_id),
                               sdk_key=sdk_key)
