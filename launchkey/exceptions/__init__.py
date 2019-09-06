"""Exception Classes"""

# pylint: disable=keyword-arg-before-vararg


import warnings

from formencode import Invalid

from .validation import AuthorizationInProgressValidator


class InsufficientRights(Exception):
    """The requesting client does not have sufficient rights for a service"""


class InvalidEntityID(Exception):
    """The given entity ID is not a valid UUID"""


class InvalidPrivateKey(Exception):
    """The given private key is not a valid PEM string"""


class InvalidIssuer(Exception):
    """The issuer is not valid"""


class InvalidIssuerFormat(Exception):
    """The issuer format is not a valid UUID"""


class InvalidIssuerVersion(Exception):
    """The issuer UUID is the wrong version type"""


class InvalidAlgorithm(Exception):
    """Input algorithm is not supported"""


class InvalidPolicyFormat(Exception):
    """
    Invalid policy format. A JSON object is expected which is in the proper
    format containing minimum_requirements and factors.
    """


class DuplicateGeoFenceName(Exception):
    """The input Geo-Fence name is already taken"""


class InvalidGeoFenceName(Exception):
    """The input Geo-Fence name was not found"""


class InvalidFenceType(Exception):
    """The GeoFence provided was not allowed"""


class DuplicateTimeFenceName(Exception):
    """The input Time-Fence name is already taken"""


class InvalidTimeFenceName(Exception):
    """The input Time-Fence name was not found"""


class InvalidTimeFenceStartTime(Exception):
    """The input start time should be a datetime.time object"""


class InvalidTimeFenceEndTime(Exception):
    """The input end time should be a datetime.time object"""


class MismatchedTimeFenceTimezones(Exception):
    """Start time and end time timezones must match"""


class UnknownPolicyException(Exception):
    """Policy Type was unknown to this version of the SDK"""


class InvalidPolicyAttributes(Exception):
    """Invalid Policy Attributes on Inside or Outside Policies"""


class LaunchKeyAPIException(Exception):
    """API Error (400+) was returned"""

    def __init__(self, message=None, status_code=None, reason=None,
                 error_data=None, *args, **kwargs):
        super(LaunchKeyAPIException, self).__init__(message, *args, **kwargs)
        self.message = message
        self.status_code = status_code
        self.reason = reason
        self.data = error_data if error_data else {}


class InvalidParameters(LaunchKeyAPIException):
    """API Error ARG-001 - Parameter validation error"""


class PolicyFailure(LaunchKeyAPIException):
    """
    API Error A-AUT-P-405 - Auth creation failed due to user not passing policy
    """


class InvalidPolicyInput(LaunchKeyAPIException):
    """API Error APP-002 - The input auth policy is not valid"""


class Unauthorized(LaunchKeyAPIException):
    """
    Generic API 401 Error - Authentication was denied. Likely an invalid key.
    """


class Forbidden(LaunchKeyAPIException):
    """Generic API 403 Error"""


class EntityNotFound(LaunchKeyAPIException):
    """Generic API 404 Error - Entity was not found"""


class RequestTimedOut(LaunchKeyAPIException):
    """Generic API 408 Error - Request timed out"""


class Conflict(LaunchKeyAPIException):
    """Generic API 409 Error - Conflict"""


class RateLimited(LaunchKeyAPIException):
    """Generic API 429 Error - Rate Limited"""


class InvalidDirectoryIdentifier(LaunchKeyAPIException):
    """API Error DIR-001 - The input directory identifier was invalid"""


class UnexpectedAPIResponse(LaunchKeyAPIException):
    """The API returned a response that cannot be handled"""


class UnexpectedDeviceResponse(LaunchKeyAPIException):
    """The device returned a response that cannot be handled"""


class InvalidDeviceStatus(LaunchKeyAPIException):
    """The device status code is not recognized"""


class JWTValidationFailure(LaunchKeyAPIException):
    """JWT Response from the API was determined to be invalid"""


class UnexpectedKeyID(LaunchKeyAPIException):
    """The given key id was not unrecognized"""


class NoIssuerKey(LaunchKeyAPIException):
    """Issuer key was not loaded"""


class InvalidJWTResponse(LaunchKeyAPIException):
    """JWT Response is not in a valid format"""


class InvalidRoute(LaunchKeyAPIException):
    """The requested route does not exist in the requested path + method"""


class ServiceNameTaken(LaunchKeyAPIException):
    """
    The requested Service name is already in use. Service names are unique.
    """


class ServiceNotFound(LaunchKeyAPIException):
    """
    The requested Service does not exist. Likely invalid UUID or the service
    has been removed.
    """


class AuthorizationInProgress(LaunchKeyAPIException):
    """
    An auth already exists for the given user. Another one cannot be created
    until the current one is either responded to or expires.

    Contains attributes to describe the blocking auth request:
        :attr my_auth: Boolean stating whether the auth belongs to the
        requesting Service or another one. This is necessary when the Service
        may want to resume the current auth request.
        :attr expires: datetime object stating when the auth request will
        expire, and thus another auth can be created without user intervention.
        :attr auth_request: Auth request ID associated with the blocking auth.
        This ID can be used to resume polling for an auth request.
    """

    from_same_service = None
    expires = None
    authorization_request_id = None

    def __init__(self, message=None, *args, **kwargs):
        super(AuthorizationInProgress, self).__init__(message, *args, **kwargs)

        try:
            self.data = AuthorizationInProgressValidator().to_python(self.data)
            self.from_same_service = self.data['from_same_service']
            self.expires = self.data['expires']
            self.authorization_request_id = self.data['auth_request']
        except Invalid as exception:
            warnings.warn("Failed to parse AuthorizationInProgress data: "
                          "exception: {0} data: {1}".format(exception,
                                                            self.data))


class AuthorizationRequestCanceled(LaunchKeyAPIException):
    """
    The authorization request has been canceled.
    """


class AuthorizationResponseExists(LaunchKeyAPIException):
    """
    The authentication request has already been responded to so it cannot be
    modified.
    """


class PublicKeyAlreadyInUse(LaunchKeyAPIException):
    """
    The public key you supplied already exists for the requested entity. It
    cannot be added again.
    """


class InvalidPublicKey(LaunchKeyAPIException):
    """The public key you supplied is not valid."""


class PublicKeyDoesNotExist(LaunchKeyAPIException):
    """The key_id you supplied could not be found."""


class LastRemainingKey(LaunchKeyAPIException):
    """The last remaining public key cannot be removed."""


class LastRemainingSDKKey(LaunchKeyAPIException):
    """The last remaining Authenticator SDK Key cannot be removed."""


class InvalidSDKKey(LaunchKeyAPIException):
    """
    The Authenticator SDK Key you supplied does not belong to the referenced
    Directory
    """


class DirectoryNameInUse(LaunchKeyAPIException):
    """The input Directory name is already in use."""


class UnexpectedWebhookRequest(LaunchKeyAPIException):
    """There was an error processing the webhook request."""


class UnableToDecryptWebhookRequest(LaunchKeyAPIException):
    """There was an error decrypting the body of the webhook request."""


class UnableToDecryptAuthorizationResponse(LaunchKeyAPIException):
    """
    There was an error decrypting the response package of the authorization
    response webhook request.
    """


class UnexpectedAuthorizationResponse(LaunchKeyAPIException):
    """
    There was an issue with the response package of the authorization response
    webhook request.
    """


class WebhookAuthorizationError(LaunchKeyAPIException):
    """
    There was an issue with validating the authorization provided by the
    webhook request.
    """


class XiovJWTValidationFailure(LaunchKeyAPIException):
    """x-iov-jwt validation failure"""


class XiovJWTDecryptionFailure(LaunchKeyAPIException):
    """x-iov-jwt decryption failure"""
