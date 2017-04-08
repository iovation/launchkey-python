class InsufficientRights(Exception):
    """The requesting client does not have sufficient rights for a service"""


class InvalidEntityID(Exception):
    """The given entity ID is not a valid UUID"""


class InvalidPrivateKey(Exception):
    """The given private key is not a valid PEM string"""


class InvalidIssuer(Exception):
    """The issuer is not valid"""


class InvalidAlgorithm(Exception):
    """Input algorithm is not supported"""


class LaunchKeyAPIException(Exception):
    """API Error (400+) was returned"""
    def __init__(self, message=None, status_code=None, *args, **kwargs):
        super(LaunchKeyAPIException, self).__init__(message, *args, **kwargs)
        self.message = message
        self.status_code = status_code


class InvalidParameters(LaunchKeyAPIException):
    """API Error ARG-001 - Parameter validation error"""


class PolicyFailure(LaunchKeyAPIException):
    """API Error A-AUT-P-405 - Auth creation failed due to user not passing policy"""


class InvalidPolicyInput(LaunchKeyAPIException):
    """API Error APP-002 - The input auth policy is not valid"""


class Unauthorized(LaunchKeyAPIException):
    """Generic API 401 Error - Authentication was denied. Likely an invalid key."""


class Forbidden(LaunchKeyAPIException):
    """Generic API 403 Error"""


class EntityNotFound(LaunchKeyAPIException):
    """Generic API 404 Error - Entity was not found"""


class RequestTimedOut(LaunchKeyAPIException):
    """Generic API 408 Error - Request timed out"""


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
