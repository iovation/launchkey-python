"""Base Client containing shared functionality for all clients"""

# pylint: disable=too-few-public-methods, too-many-arguments

from functools import wraps
from uuid import UUID
import warnings

from formencode import Invalid

from launchkey.entities.service import Service, ServiceSecurityPolicy
from launchkey.entities.service.policy import ConditionalGeoFencePolicy, \
    GeoCircleFence, TerritoryFence, LegacyPolicy, \
    MethodAmountPolicy, FactorsPolicy
from launchkey.entities.shared import PublicKey
from launchkey.entities.validation import ServiceValidator, \
    PublicKeyValidator, ServiceSecurityPolicyValidator
from launchkey.exceptions import InvalidEntityID, LaunchKeyAPIException, \
    InvalidParameters, EntityNotFound, PolicyFailure, InvalidPolicyInput, \
    RequestTimedOut, RateLimited, InvalidDirectoryIdentifier, \
    UnexpectedAPIResponse, Forbidden, Unauthorized, InvalidRoute, \
    ServiceNameTaken, ServiceNotFound, PublicKeyAlreadyInUse, \
    InvalidPublicKey, PublicKeyDoesNotExist, LastRemainingKey, \
    LastRemainingSDKKey, InvalidSDKKey, DirectoryNameInUse, \
    AuthorizationInProgress, Conflict, AuthorizationResponseExists, \
    AuthorizationRequestCanceled, UnknownPolicyException, InvalidFenceType
from launchkey.transports.base import APIResponse
from launchkey.utils.shared import iso_format, deprecated

ERROR_CODE_MAP = {
    "ARG-001": InvalidParameters,
    "ARG-002": InvalidRoute,
    "SVC-001": ServiceNameTaken,
    "SVC-002": InvalidPolicyInput,
    "SVC-003": PolicyFailure,
    "SVC-004": ServiceNotFound,
    "SVC-005": AuthorizationInProgress,
    "SVC-006": AuthorizationResponseExists,
    "SVC-007": AuthorizationRequestCanceled,
    "DIR-001": InvalidDirectoryIdentifier,
    "KEY-001": InvalidPublicKey,
    "KEY-002": PublicKeyAlreadyInUse,
    "KEY-003": PublicKeyDoesNotExist,
    "KEY-004": LastRemainingKey,
    "ORG-003": DirectoryNameInUse,
    "ORG-005": LastRemainingSDKKey,
    "ORG-006": InvalidSDKKey
}

STATUS_CODE_MAP = {
    401: Unauthorized,
    403: Forbidden,
    404: EntityNotFound,
    408: RequestTimedOut,
    409: Conflict,
    429: RateLimited
}


def api_call(function_):
    """
    Decorator for handling LaunchKey API Exceptions
    :param function_:
    :return:
    """

    @wraps(function_)
    def wrapper(*args, **kwargs):
        """Decorator function"""

        try:
            return function_(*args, **kwargs)
        except LaunchKeyAPIException as cause:
            if not isinstance(cause.message, dict) \
                    or 'error_code' not in cause.message \
                    or 'error_detail' not in cause.message:
                error_code = "HTTP-%s" % cause.status_code
                error_detail = "%s" % cause.reason
                error_data = None
            else:
                error_code = cause.message.get('error_code')
                error_detail = cause.message.get('error_detail')
                error_data = cause.message.get('error_data')
            status_code = cause.status_code
            if error_code in ERROR_CODE_MAP:
                raise ERROR_CODE_MAP[error_code](error_detail, status_code,
                                                 error_data=error_data)
            if status_code in STATUS_CODE_MAP:
                raise STATUS_CODE_MAP[status_code](error_detail, status_code,
                                                   error_data=error_data)
            raise

    return wrapper


class BaseClient(object):
    """
    Base Client for performing API queries against the LaunchKey API. Clients
    are the interfaces that will be used by implementers to query against
    specific entity based endpoints (service, directory, organization, etc).
    """

    def __init__(self, subject_type, subject_id, transport):
        """
        :param subject_type: Entity type that the service will represent
        :param subject_id: Entity id of which the service will represent
        :param transport: Transport class that will perform API queries
        """
        try:
            UUID(str(subject_id))
        except ValueError:
            raise InvalidEntityID("The given id was invalid. Please ensure "
                                  "it is a UUID.")
        self._subject = "%s:%s" % (subject_type, subject_id)
        self._transport = transport

    @staticmethod
    def _validate_response(api_response, validator):
        if isinstance(api_response, APIResponse):
            try:
                return validator.to_python(api_response.data)
            except Invalid:
                raise UnexpectedAPIResponse(
                    api_response.data,
                    api_response.status_code)
        else:
            try:
                return validator.to_python(api_response)
            except Invalid:
                raise UnexpectedAPIResponse(api_response)


class ServiceManagingBaseClient(BaseClient):
    """Base client containing shared code for managing Services"""

    def __init__(self, subject_type, subject_id, transport, service_base_path):

        super(ServiceManagingBaseClient, self).__init__(
            subject_type, subject_id, transport)
        self.__service_base_path = service_base_path

    @api_call
    def create_service(self, name, description=None, icon=None,
                       callback_url=None, active=True):
        """
        Creates a Service
        :param name: Unique name that will be displayed in an Auth Request
        :param description: Optional description that can be viewed in the
        Admin Center or when retrieving the Service.
        :param icon: Optional URL to an icon that will be displayed in an
        Auth Request
        :param callback_url: URL that Webhooks will be sent to
        :param active: Whether the Service should be able to send Auth Requests
        :raise: launchkey.exceptions.InvalidParameters - Input parameters
        were not correct
        :raise: launchkey.exceptions.ServiceNameTaken - Service name
        already taken
        :return: String - ID of the Service that is created
        """
        return self._transport.post(self.__service_base_path,
                                    self._subject, name=name,
                                    description=description,
                                    icon=icon, callback_url=callback_url,
                                    active=active).data['id']

    @api_call
    def get_all_services(self):
        """
        Retrieves all Services belonging to the subject entity
        :return: List - launchkey.entities.service.Service object containing
        Service details
        """
        response = self._transport.get(
            self.__service_base_path,
            self._subject)

        services = []

        for service_data in response.data:
            validated_data = self._validate_response(
                service_data, ServiceValidator)
            service = Service(validated_data)
            services.append(service)

        return services

    @api_call
    def get_services(self, service_ids):
        """
        Retrieves Services based on an input list of Service IDs
        :param service_ids: List of unique Service IDs
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :return: List - launchkey.entities.service.Service object containing
        Service details
        """
        string_service_ids = [str(service_id) for service_id in service_ids]

        response = self._transport.post(
            "{}/list".format(self.__service_base_path),
            self._subject, service_ids=string_service_ids)

        services = []

        for service_data in response.data:
            validated_data = self._validate_response(
                service_data, ServiceValidator)
            service = Service(validated_data)
            services.append(service)

        return services

    @api_call
    def get_service(self, service_id):
        """
        Retrieves a Service based on an input Service ID
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :return: launchkey.entities.service.Service object containing
        Service details
        """
        response = self._transport.post(
            "{}/list".format(self.__service_base_path),
            self._subject, service_ids=[str(service_id)])

        service_data = self._validate_response(response.data[0],
                                               ServiceValidator)
        service = Service(service_data)

        return service

    @api_call
    def update_service(self, service_id, name=False, description=False,
                       icon=False, callback_url=False, active=None):
        """
        Updates a Service's general settings. If an optional parameter is not
        included it will not be updated.
        :param service_id: Unique Service ID
        :param name: Unique name that will be displayed in an Auth Request
        :param description: Description that can be viewed in the Admin Center
        or when retrieving the Service.
        :param icon: URL to an icon that will be displayed in an Auth Request
        :param callback_url: URL that Webhooks will be sent to
        :param active: Whether the Service should be able to send Auth Requests
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.ServiceNameTaken - Service name
        already taken
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be
        found matching the input ID
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
        self._transport.patch(self.__service_base_path, self._subject,
                              **kwargs)

    @api_call
    def add_service_public_key(self, service_id, public_key, expires=None,
                               active=None, key_type=None):
        """
        Adds a public key to a Service
        :param service_id: Unique Service ID
        :param public_key: String RSA public key
        :param expires: Optional datetime.datetime stating a time in which the
        key will no longer be valid
        :param active: Optional bool stating whether the key should be
        considered active and usable.
        :param key_type: Optional KeyType enum to identify whether the key is
        an encryption key, signature key, or a dual use key
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.InvalidPublicKey - The public key you
        supplied is not valid.
        :raise: launchkey.exceptions.PublicKeyAlreadyInUse - The public key
        you supplied already exists for the requested entity. It cannot be
        added again.
        :return: MD5 fingerprint (key_id) of the public key,
        IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        """
        kwargs = {"service_id": str(service_id), "public_key": public_key}
        if expires is not None:
            kwargs['date_expires'] = iso_format(expires)
        if active is not None:
            kwargs['active'] = active
        if key_type is not None:
            kwargs['key_type'] = key_type.value

        key_id = self._transport.post(
            "{}/keys".format(self.__service_base_path[0:-1]),
            self._subject, **kwargs).data['key_id']
        return key_id

    @api_call
    def get_service_public_keys(self, service_id):
        """
        Retrieves a list of Public Keys belonging to a Service
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be
        found matching the input ID
        :raise: launchkey.exceptions.Forbidden - The Service you requested
        either does not exist or you do not have sufficient permissions.
        :return: List - launchkey.entities.shared.PublicKey
        """
        response = self._transport.post(
            "{}/keys/list".format(self.__service_base_path[0:-1]),
            self._subject, service_id=str(service_id))

        public_keys = []

        for key in response.data:
            key_data = self._validate_response(key, PublicKeyValidator)
            public_key = PublicKey(key_data)
            public_keys.append(public_key)

        return public_keys

    @api_call
    def remove_service_public_key(self, service_id, key_id):
        """
        Removes a public key from a Service. You may only remove
        a public key if other public keys exist. If you wish for a last
        remaining key to no longer be usable, use  update_service_public_key to
        instead and set it as inactive.
        :param service_id: Unique Service ID
        :param key_id: MD5 fingerprint of the public key,
        IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        :raise: launchkey.exceptions.InvalidParameters - Input parameters
        were not correct
        :raise: launchkey.exceptions.PublicKeyDoesNotExist - The key_id you
        ]supplied could not be found
        :raise: launchkey.exceptions.LastRemainingKey - The last remaining
        public key cannot be removed
        :raise: launchkey.exceptions.Forbidden - The Service you requested
        either does not exist or you do not have sufficient permissions.
        :return:
        """
        self._transport.delete(
            "{}/keys".format(self.__service_base_path[0:-1]),
            self._subject, service_id=str(service_id), key_id=key_id)

    @api_call
    def update_service_public_key(self, service_id, key_id, expires=False,
                                  active=None):
        """
        Updates a public key from a Service
        :param service_id: Unique Service ID
        :param key_id: MD5 fingerprint of the public key,
        IE: e0:2f:a9:5a:76:92:6b:b5:4d:24:67:19:d1:8a:0a:75
        :param expires: datetime.datetime stating a time in which the key will
        no longer be valid
        :param active: Bool stating whether the key should be considered active
        and usable
        :raise: launchkey.exceptions.PublicKeyDoesNotExist - The key_id you
        supplied could not be found
        :raise: launchkey.exceptions.Forbidden - The Service you requested
        either does not exist or you do not have sufficient permissions.
        :return:
        """
        kwargs = {"service_id": str(service_id), "key_id": key_id}
        if active is not None:
            kwargs['active'] = active
        if expires is not False:
            kwargs['date_expires'] = iso_format(expires)

        self._transport.patch(
            "{}/keys".format(self.__service_base_path[0:-1]),
            self._subject, **kwargs)

    @deprecated
    def get_service_policy(self, service_id):
        """
        NOTE: This method is being deprecated. Use
        `get_advanced_service_policy` instead!

        Retrieves a Service's Security Policy
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be
        found matching the input ID
        :return: launchkey.entities.service.ServiceSecurityPolicy object
        containing policy details
        :return: None if policy returned from `get_advanced_service_policy` is
        not a legacy policy
        """
        current_policy = self.get_advanced_service_policy(service_id)
        if not isinstance(current_policy, LegacyPolicy):
            warnings.warn("Policy received was not a legacy policy and cannot "
                          "be converted into a ServiceSecurityPolicy.",
                          category=DeprecationWarning)

            return None

        policy = ServiceSecurityPolicy(
            any=current_policy.amount,
            knowledge=current_policy.knowledge_required,
            inherence=current_policy.inherence_required,
            possession=current_policy.possession_required,
            jailbreak_protection=current_policy.deny_rooted_jailbroken
        )

        for fence in current_policy.fences:
            policy.add_geofence(
                fence.latitude,
                fence.longitude,
                fence.radius,
                name=fence.name
            )

        for fence in current_policy.time_restrictions:
            policy.add_timefence(
                fence.name,
                fence.start_time,
                fence.end_time,
                monday=fence.monday,
                tuesday=fence.tuesday,
                wednesday=fence.wednesday,
                thursday=fence.thursday,
                friday=fence.friday,
                saturday=fence.saturday,
                sunday=fence.sunday
            )

        return policy

    @api_call
    def get_advanced_service_policy(self, service_id):
        """
        Retrieves a Service's Security Policy
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be
        found matching the input ID
        :return: ConditionalGeoFencePolicy, FactorsPolicy, MethodAmountPolicy
        or LegacyPolicy
        :raises UnknownPolicyError: in the event an unrecognized policy type
        is received
        :raises InvalidFenceType: in the event an unrecognized fence type is
        received
        """
        response = self._transport.post(
            "{}/policy/item".format(self.__service_base_path[0:-1]),
            self._subject, service_id=str(service_id))

        policy_data = self._validate_response(response.data,
                                              ServiceSecurityPolicyValidator)

        if policy_data["type"] == "COND_GEO":
            inside = self.__process_nested_service_policy(
                policy_data["inside"]
            )
            outside = self.__process_nested_service_policy(
                policy_data["outside"]
            )

            policy = ConditionalGeoFencePolicy(
                inside,
                outside,
                deny_rooted_jailbroken=policy_data["deny_rooted_jailbroken"],
                deny_emulator_simulator=policy_data["deny_emulator_simulator"],
                fences=self.__generate_fence_objects_from_policy(policy_data)
            )
        elif policy_data["type"] == "LEGACY":
            ss_policy = ServiceSecurityPolicy()
            ss_policy.set_policy(policy_data)
            policy = self.__service_security_policy_to_legacy_policy(ss_policy)
        elif policy_data["type"] == "METHOD_AMOUNT":
            policy = MethodAmountPolicy(
                deny_rooted_jailbroken=policy_data[
                    "deny_rooted_jailbroken"],
                deny_emulator_simulator=policy_data[
                    "deny_emulator_simulator"],
                fences=self.__generate_fence_objects_from_policy(policy_data),
                amount=policy_data["amount"]
            )
        elif policy_data["type"] == "FACTORS":
            policy = FactorsPolicy(
                deny_rooted_jailbroken=policy_data[
                    "deny_rooted_jailbroken"],
                deny_emulator_simulator=policy_data[
                    "deny_emulator_simulator"],
                inherence_required="INHERENCE" in policy_data["factors"],
                knowledge_required="KNOWLEDGE" in policy_data["factors"],
                possession_required="POSSESSION" in policy_data["factors"],
                fences=self.__generate_fence_objects_from_policy(policy_data)
            )
        else:
            raise UnknownPolicyException(
                "The Policy {0} was not a known Policy type".format(
                    policy_data["type"])
            )

        return policy

    def __service_security_policy_to_legacy_policy(self, policy):
        return LegacyPolicy(
            amount=policy.minimum_amount,
            inherence_required="inherence" in policy.minimum_requirements,
            knowledge_required="knowledge" in policy.minimum_requirements,
            possession_required="possession" in policy.minimum_requirements,
            deny_rooted_jailbroken=policy.jailbreak_protection,
            fences=list(map(self.__geofence_to_geo_circle, policy.geofences)),
            time_restrictions=policy.timefences
        )

    @staticmethod
    def __geofence_to_geo_circle(geofence):
        return GeoCircleFence(
            geofence.latitude,
            geofence.longitude,
            geofence.radius,
            name=geofence.name
        )

    @staticmethod
    def __generate_fence_objects_from_policy(policy):
        fences = list()
        for fence in policy["fences"]:
            if fence["type"] == "GEO_CIRCLE":
                fences.append(
                    GeoCircleFence(
                        latitude=fence["latitude"],
                        longitude=fence["longitude"],
                        radius=fence["radius"],
                        name=fence["name"]
                    )
                )
            elif fence["type"] == "TERRITORY":
                fences.append(
                    TerritoryFence(
                        country=fence["country"],
                        administrative_area=fence["administrative_area"],
                        postal_code=fence["postal_code"],
                        name=fence["name"]
                    )
                )
            else:
                raise InvalidFenceType(
                    "Fence type \"{0}\" was not a valid Fence type".format(
                        fence["type"]
                    )
                )

        return fences

    @staticmethod
    def __process_nested_service_policy(policy):
        if policy["type"] == "METHOD_AMOUNT":
            new_policy = MethodAmountPolicy(
                amount=policy["amount"],
                deny_rooted_jailbroken=None,
                deny_emulator_simulator=None,
                fences=policy["fences"]
            )
        elif policy["type"] == "FACTORS":
            new_policy = FactorsPolicy(
                deny_rooted_jailbroken=None,
                deny_emulator_simulator=None,
                inherence_required="INHERENCE" in policy["factors"],
                knowledge_required="KNOWLEDGE" in policy["factors"],
                possession_required="POSSESSION" in policy["factors"],
                fences=policy["fences"]
            )
        else:
            raise UnknownPolicyException(
                "Valid nested Policy types for ConditionalGeofence Policies "
                "are: [\"METHOD_AMOUNT\", \"FACTORS\"]"
            )
        return new_policy

    @deprecated
    def set_service_policy(self, service_id, policy):
        """
        NOTE: This method is being deprecated. Use
        `set_advanced_service_policy` instead!

        Sets a Service's Security Policy
        :param service_id: Unique Service ID
        :param policy: launchkey.clients.shared.ServiceSecurityPolicy
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be
        found matching the input ID
        :return:
        """
        self.set_advanced_service_policy(service_id, policy)

    @api_call
    def set_advanced_service_policy(self, service_id, policy):
        """
        Sets a Service's Security Policy
        :param service_id: Unique Service ID
        :param policy: LegacyPolicy, ConditionalGeoFencePolicy,
        MethodAmountPolicy, FactorsPolicy, or ServiceSecurityPolicy
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be
        found matching the input ID
        :return:
        """
        self._transport.put(
            "{}/policy".format(self.__service_base_path[0:-1]),
            self._subject, service_id=str(service_id),
            policy=policy.to_dict())

    @api_call
    def remove_service_policy(self, service_id):
        """
        Resets a Service's Security Policy back to default
        :param service_id: Unique Service ID
        :raise: launchkey.exceptions.ServiceNotFound - No Service could be
        found matching the input ID
        :return:
        """
        self._transport.delete(
            "{}/policy".format(self.__service_base_path[0:-1]),
            self._subject, service_id=str(service_id))
