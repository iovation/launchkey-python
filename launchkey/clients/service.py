from .base import BaseClient, api_call
from launchkey.exceptions import UnexpectedDeviceResponse, UnexpectedKeyID, InvalidParameters
from formencode import Schema, validators, Invalid
from base64 import b64decode
from json import loads, dumps


class AuthorizationResponseValidator(Schema):
    auth = validators.String()
    service_user_hash = validators.String()
    org_user_hash = validators.String()
    user_push_id = validators.String()
    public_key_id = validators.String()
    allow_extra_fields = True


class AuthorizationResponsePackageValidator(Schema):
    service_pins = validators.String()
    auth_request = validators.String()  # UUID
    response = validators.Bool()
    device_id = validators.String()
    allow_extra_fields = True


class AuthorizeValidator(Schema):
    auth_request = validators.String()
    allow_extra_fields = True


class AuthorizeSSEValidator(Schema):
    service_user_hash = validators.String()
    api_time = validators.String()
    allow_extra_fields = True


class AuthPolicy(object):
    """AuthPolicy object for performing dynamic authorizations"""

    def __init__(self, any=0, knowledge=False, inherence=False, possession=False, jailbreak_protection=False):
        """
        Note that if any is used neither knowledge, inherence, nor possession can be used alongside it.

        If all values are left at 0, service defaults will be used.

        :param any: Int. Whether to require any x number of factors
        :param knowledge: Boolean. Whether to require knowledge factors
        :param inherence: Boolean. Whether to require inherence factors
        :param possession: Boolean. Whether to require possesion factors
        :param jailbreak_protection: Boolean. Whether to allow jailbroken / rooted devices to authenticate
        """
        knowledge = int(knowledge)
        inherence = int(inherence)
        possession = int(possession)

        if knowledge > 1 or inherence > 1 or possession > 1:
            raise InvalidParameters("Inherence, knowlege, or possesion input must be a boolean.")
        if any != 0 and (knowledge != 0 or inherence != 0 or possession != 0):
            raise InvalidParameters("Cannot use \"any\" with other specific factor requirements")

        self._policy = {"factors": []}
        if any != 0 or knowledge != 0 or inherence != 0 or possession != 0:
            self._policy['minimum_requirements'] = [
                {
                    "requirement": "authenticated",
                    "any": int(any),
                    "knowledge": int(knowledge),
                    "inherence": int(inherence),
                    "possession": int(possession)
                }
            ]

        if jailbreak_protection is True:
            self._policy['factors'].append({
                "factor": "device integrity",
                "requirement": "forced requirement",
                "quickfail": False,
                "priority": 1,
                "attributes": {"factor enabled": 1}
            })

    def add_geofence(self, latitude, longitude, radius):
        """
        Adds a geofence requirement
        :param latitude: Float. Geographical Latitude
        :param longitude: Float. Geographical Longitude
        :param radius: Float. Radius of the geofence in meters
        """
        try:
            location = {"radius": float(radius), "latitude": float(latitude), "longitude": float(longitude)}
        except TypeError:
            raise InvalidParameters("Latitude, Longitude, and Radius must all be numbers.")
        for i, factor in enumerate(self._policy['factors']):
            if factor.get('factor') == "geofence":
                self._policy['factors'][i]['attributes']['locations'].append(location)
                return
        self._policy['factors'].append(
            {
                "factor": "geofence",
                "requirement": "forced requirement",
                "quickfail": False,
                "priority": 1,
                "attributes": {"locations": [location]}
            }
        )

    def get_policy(self):
        """
        Retrieves json representation of the policy
        :return: Valid policy dict
        """
        try:
            dumps(self._policy)
        except TypeError:
            raise InvalidParameters("Policy input was not JSON serializable. Please verify it is correct.")
        return self._policy


class AuthorizationResponse(object):
    """Authorization Response object containing decrypted auth response and other related information"""

    @staticmethod
    def _decrypt_auth_package(package, issuer_private_key):
        try:
            return AuthorizationResponsePackageValidator.to_python(loads(issuer_private_key.decrypt(
                b64decode(package))))
        except (Invalid, ValueError, TypeError):
            raise UnexpectedDeviceResponse("The device response was invalid. Please verify the same key that initiated"
                                           " the auth request is being used to decrypt the current message.")

    def __init__(self, data, issuer_private_keys):
        if data.get('public_key_id') not in issuer_private_keys:
            raise UnexpectedKeyID("The auth response was for a key id %s which is not recognized" %
                                  data.get('public_key_id'))
        decrypted_package = self._decrypt_auth_package(data['auth'], issuer_private_keys[data.get('public_key_id')])
        self.authorization_request_id = decrypted_package.get('auth_request')
        self.authorized = decrypted_package.get('response')
        self.device_id = decrypted_package.get('device_id')
        self.service_pins = decrypted_package.get('service_pins').split(",")
        self.service_user_hash = data.get('service_user_hash')
        self.organization_user_hash = data.get('org_user_hash')
        self.user_push_id = data.get('user_push_id')


class SessionEndRequest(object):
    """Session end request containing the logout_requested unix timestamp and the service_user_hash"""

    def __init__(self, api_time, service_user_hash):
        self.logout_requested = api_time
        self.service_user_hash = service_user_hash


class ServiceClient(BaseClient):

    def __init__(self, subject_id, transport):
        super(ServiceClient, self).__init__('svc', subject_id, transport)

    @api_call
    def authorize(self, user, context=None, policy=None):
        """
        Authorize a transaction for the provided user. This get_service_service method would be utilized if you are
        using this as a secondary factor for user login or authorizing a single transaction within your application.
        This will NOT begin a user session.
        :param user: LaunchKey Username, User Push ID, or Directory User ID for the End User
        :param context: Arbitrary string of data up to 400 characters to be presented to the End User during
        authorization to provide context regarding the individual request
        :param policy: Authorization policy override for this authorization. The policy can only increase the security
        level any existing policy in the Service Profile. It can never reduce the security level of the Service
        Profile's policy.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.InvalidPolicyInput - Input policy was not valid
        :raise: launchkey.exceptions.PolicyFailure - Auth creation failed due to user not passing policy
        :raise: launchkey.exceptions.EntityNotFound - Username was invalid or the user does not have any valid devices
        :raise: launchkey.exceptions.RateLimited - Too many authorization requests have been created for this user
        :raise: launchkey.exceptions.InvalidPolicy - The input policy is not valid. It should be a
        launchkey.clients.service.AuthPolicy.
        Please wait and try again.
        :return: String - Unique identifier for tracking status of the authorization request
        """
        kwargs = {'username': user}
        if context is not None:
            kwargs['context'] = context
        if policy is not None:
            if not isinstance(policy, AuthPolicy):
                raise InvalidParameters("Please verify the input policy is a "
                                        "launchkey.clients.service.AuthPolicy class")
            kwargs['policy'] = policy.get_policy()

        response = self._transport.post("/service/v3/auths", self._subject, **kwargs)
        return self._validate_response(response, AuthorizeValidator)['auth_request']

    @api_call
    def get_authorization_response(self, authorization_request_id):
        """
        Request the response for a previous authorization call.
        :param authorization_request_id: Unique identifier returned by authorize()
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.RequestTimedOut - The authorization request has not been responded to before the
        timeout period (5 minutes)
        :return: None if the user has not responded otherwise an AuthorizationResponse object with the user's response
        in it
        """
        response = self._transport.get("/service/v3/auths/%s" % authorization_request_id, self._subject)
        if response.status_code == 204:
            return None
        else:
            data = self._validate_response(response, AuthorizationResponseValidator)
            return AuthorizationResponse(data, self._transport.loaded_issuer_private_keys)

    @api_call
    def session_start(self, user, authorization_request_id):
        """
        Request to start a Service Session for the End User which was derived from a authorization request
        :param user: LaunchKey Username, User Push ID, or Directory User ID for the End User
        :param authorization_request_id: Unique identifier returned by authorize()
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.EntityNotFound - The input username was not valid
        """
        self._transport.post("/service/v3/sessions", self._subject, username=user,
                             auth_request=authorization_request_id)

    @api_call
    def session_end(self, user):
        """
        Request to end a Service Session for the End User
        :param user: LaunchKey Username, User Push ID, or Directory User ID for the End User
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were not correct
        :raise: launchkey.exceptions.EntityNotFound - The input username was not valid
        """
        self._transport.delete("/service/v3/sessions", self._subject, username=user)

    def handle_webhook(self, body, headers):
        """
        Handle a webhook callback
        In the event of a Logout webhook, be sure to call session_end() when you complete the process of ending the
        user's session in your implementation.  This will remove the corresponding Application from the authorization
        list on all of the the user's mobile devices.
        :param body: The raw body that was send in the POST content
        :param headers: A generic map of response headers. These will be used to access and validate the JWT
        :return:
        """
        self._transport.verify_jwt_response(headers, None, body, self._subject)
        if "service_user_hash" in body:
            body = self._validate_response(loads(body), AuthorizeSSEValidator)
            return SessionEndRequest(body['service_user_hash'], self._transport.parse_api_time(body['api_time']))
        else:
            body = loads(self._transport.decrypt_response(body))
            return AuthorizationResponse(body, self._transport.loaded_issuer_private_keys)
