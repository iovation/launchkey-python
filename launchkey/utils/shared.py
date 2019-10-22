""" Shared Utilities """

from functools import wraps
from uuid import UUID
import warnings

import six
from jwkest import JWKESTException

from ..exceptions import InvalidIssuerFormat, InvalidIssuerVersion, \
    JWTValidationFailure, InvalidJWTResponse, WebhookAuthorizationError, \
    XiovJWTValidationFailure, XiovJWTDecryptionFailure


class XiovJWTService(object):
    """
    Handles the x-iov-jwt request spec validation and decryption
    """

    def __init__(self, transport, subject):
        self._transport = transport
        self._subject = subject

    def verify_jwt_request(self, body, headers, method, path):
        """
        Retrieves and validates an x-iov-jwt payload
        :param body: The raw body that was send in the POST content
        :param headers: A generic map of response headers. These will be used
        to access and validate authorization
        :param method: The HTTP method of the request
        :param path:  The path of the request
        :return: utf-8 encoded string of the body
        :raises launchkey.exceptions.XiovJWTValidationFailure: when the
        request or its cannot be parsed or fails
        validation.
        :raises launchkey.exceptions.WebhookAuthorizationError: when the
        "Authorization" header in the headers.
        """
        if not isinstance(body, six.string_types):
            body = body.decode("utf-8")

        compact_jwt = None
        for header_key, header_value in headers.items():
            if header_key.lower() == 'x-iov-jwt':
                compact_jwt = header_value

        if compact_jwt is None:
            raise WebhookAuthorizationError(
                "The X-IOV-JWT header was not found in the supplied headers "
                "from the request!")

        try:
            self._transport.verify_jwt_request(
                compact_jwt,
                self._subject,
                method,
                path,
                body)
        except (JWTValidationFailure, InvalidJWTResponse) as reason:
            raise XiovJWTValidationFailure(reason=reason)
        return body

    def decrypt_jwe(self, body, headers, method, path):
        """
        Verifies and decrypts a jwt request
        :param body: The raw body that was send in the POST content
        :param headers: A generic map of response headers. These will be used
        to access and validate authorization
        :param method: The HTTP method of the request
        :param path:  The path of the request
        :raises launchkey.exceptions.UnexpectedKeyID: when the request body is
        decrypted using a public key whose private key is not known by the
        client. This can be a configuration issue.
        :raises launchkey.exceptions.XiovJWTDecryptionFailure: when the request
        body cannot be decrypted.
        :return: Decrypted string
        """
        body = self.verify_jwt_request(body, headers, method, path)
        try:
            return self._transport.decrypt_response(body)
        except JWKESTException as reason:
            raise XiovJWTDecryptionFailure(reason)


class UUIDHelper(object):
    """
    Validate the provided uuid string and return a UUID if string is a valid
    UUID with the correct version or throw InvalidIssuerFormat or
    InvalidIssuerVersion when that criteria is not met.
    """

    def from_string(self, uuid_value, version=None):
        """
        Create a UUID from its string representation
        :param uuid_value: The string representation of a UUID
        :param version: The version of the UUID
        :return: UUID
        :raises launchkey.exceptions.InvalidIssuerFormat: when uuid_value
        is not a valid UUID format
        :raises launchkey.exceptions.InvalidIssuerVersion: when uuid_value
        is not the same version as version.
        """
        if not isinstance(uuid_value, UUID):
            try:
                uuid_value = UUID(uuid_value)
            except (ValueError, TypeError, AttributeError):
                raise InvalidIssuerFormat()

        self.validate_version(uuid_value, version)
        return uuid_value

    @staticmethod
    def validate_version(uuid_value, version):
        """
        Validate the the provided UUID is the provided version
        :param uuid_value: A UUID
        :param version: The expected version of the UUID
        :return: None
        :raises launchkey.exceptions.InvalidIssuerFormat: when uuid_value
        is not a UUID
        :raises launchkey.exceptions.InvalidIssuerVersion: when uuid_value
        is not the same version as version.
        """
        if not isinstance(uuid_value, UUID):
            raise InvalidIssuerFormat()

        if version is not None and int(version) != uuid_value.version:
            raise InvalidIssuerVersion()


def iso_format(datetime):
    """
    Generates an ISO formatted datetime based on what the LaunchKey API
    expects. This is a standard ISO datetime without microseconds.
    :param datetime: datetime.datetime object
    :return: ISO formatted string IE: 2017-10-03T22:50:15Z
    """
    return datetime.strftime("%Y-%m-%dT%H:%M:%SZ") \
        if datetime is not None else None


# pylint: disable=invalid-name
def deprecated(fn):
    """
    Decorator for issuing warnings
    :param fn: Function to be called
    :return Any: The expected return of the passed function
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        """ Decorator function """
        warnings.warn("The %s method has been deprecated and will be removed "
                      "in the next major release." % fn.__name__,
                      DeprecationWarning)

        return fn(*args, **kwargs)

    return wrapper
