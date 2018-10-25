"""Service Client"""

# pylint: disable=too-many-arguments

import warnings

from json import loads
from jwkest import JWKESTException
from launchkey.exceptions import InvalidParameters, \
    UnableToDecryptWebhookRequest, UnexpectedAuthorizationResponse, \
    UnexpectedAPIResponse, UnexpectedWebhookRequest, JWTValidationFailure, \
    InvalidJWTResponse, WebhookAuthorizationError
from launchkey.entities.validation import AuthorizationResponseValidator, \
    AuthorizeSSEValidator, AuthorizeValidator
from launchkey.entities.service import AuthPolicy, AuthorizationResponse, \
    SessionEndRequest, AuthorizationRequest
from .base import BaseClient, api_call


class ServiceClient(BaseClient):
    """Service Client for interacting with Serive endpoints"""

    def __init__(self, subject_id, transport):
        super(ServiceClient, self).__init__('svc', subject_id, transport)

    @api_call
    def authorize(self, user, context=None, policy=None, title=None, ttl=None,
                  push_title=None, push_body=None):
        """
        Authorize a transaction for the provided user. This
        get_service_service method would be utilized if you are
        using this as a secondary factor for user login or authorizing a
        single transaction within your application.
        This will NOT begin a user session.
        :param user: LaunchKey Username, User Push ID, or Directory User ID
        for the End User
        :param context: Arbitrary string of data up to 400 characters to be
        presented to the End User during
        authorization to provide context regarding the individual request
        :param policy: Authorization policy override for this authorization.
        The policy can only increase the security level any existing policy
        in the Service Profile. It can never reduce the security level of
        the Service Profile's policy.
        :param title: String of data up to 200 characters to be presented to
        the End User during authorization as the title of the individual
        authorization request
        :param ttl: Time for this authorization request to be valid. If no
        value is provided, the system default will be used.
        :param push_title: Title that will appear in the mobile authenticator's
        push message. This feature is only available for Directory Services
        that have push credentials configured.
        :param push_body: Body that will appear in the mobile authenticator's
        push message. This feature is only available for Directory Services
        that have push credentials configured.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.InvalidPolicyInput - Input policy was not
        valid
        :raise: launchkey.exceptions.PolicyFailure - Auth creation failed due
        to user not passing policy
        :raise: launchkey.exceptions.EntityNotFound - Username was invalid or
        the user does not have any valid devices
        :raise: launchkey.exceptions.RateLimited - Too many authorization
        requests have been created for this user
        :raise: launchkey.exceptions.InvalidPolicy - The input policy is not
        valid. It should be a
        launchkey.clients.service.AuthPolicy.
        Please wait and try again.
        :return: String - Unique identifier for tracking status of the
        authorization request
        """
        warnings.warn('This method has been deprecated and will be removed'
                      ' in a future major release!', DeprecationWarning)
        auth = self.authorization_request(user, context, policy, title, ttl,
                                          push_title, push_body)
        return auth.auth_request

    @api_call
    def authorization_request(self, user, context=None, policy=None,
                              title=None, ttl=None, push_title=None,
                              push_body=None):
        """
        Authorize a transaction for the provided user. This get_service_service
        method would be utilized if you are using this as a secondary factor
        for user login or authorizing a single transaction within your
        application. This will NOT begin a user session.
        :param user: LaunchKey Username, User Push ID, or Directory User ID
        for the End User
        :param context: Arbitrary string of data up to 400 characters to be
        presented to the End User during authorization to provide context
        regarding the individual request
        :param policy: Authorization policy override for this authorization.
        The policy can only increase the security
        level any existing policy in the Service Profile. It can never reduce
        the security level of the Service Profile's policy.
        :param title: String of data up to 200 characters to be presented to
        the End User during authorization as the title of the individual
        authorization request
        :param ttl: Time for this authorization request to be valid. If no
        value is provided, the system default will be used.
        :param push_title: Title that will appear in the mobile authenticator's
        push message. This feature is only available for Directory Services
        that have push credentials configured.
        :param push_body: Body that will appear in the mobile authenticator's
        push message. This feature is only available for Directory Services
        that have push credentials configured.
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.InvalidPolicyInput - Input policy was not
        valid
        :raise: launchkey.exceptions.PolicyFailure - Auth creation failed due
        to user not passing policy
        :raise: launchkey.exceptions.EntityNotFound - Username was invalid or
        the user does not have any valid devices
        :raise: launchkey.exceptions.RateLimited - Too many authorization
        requests have been created for this user
        :raise: launchkey.exceptions.InvalidPolicy - The input policy is not
        valid. It should be a launchkey.clients.service.AuthPolicy.
        Please wait and try again.
        :return AuthorizationResponse: Unique identifier for tracking status
        of the authorization request
        """
        kwargs = {'username': user}
        if context is not None:
            kwargs['context'] = context
        if title is not None:
            kwargs['title'] = title
        if ttl is not None:
            kwargs['ttl'] = ttl
        if push_title is not None:
            kwargs['push_title'] = push_title
        if push_body is not None:
            kwargs['push_body'] = push_body
        if policy is not None:
            if not isinstance(policy, AuthPolicy):
                raise InvalidParameters(
                    "Please verify the input policy is a "
                    "launchkey.clients.service.AuthPolicy class")
            kwargs['policy'] = policy.get_policy()

        response = self._transport.post("/service/v3/auths",
                                        self._subject, **kwargs)
        data = self._validate_response(response, AuthorizeValidator)
        return AuthorizationRequest(data.get('auth_request'),
                                    data.get('push_package'))

    @api_call
    def get_authorization_response(self, authorization_request_id):
        """
        Request the response for a previous authorization call.
        :param authorization_request_id: Unique identifier returned by
        authorize()
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.RequestTimedOut - The authorization
        request has not been responded to before the
        timeout period (5 minutes)
        :return: None if the user has not responded otherwise a
        launchkey.entities.service.AuthorizationResponse object
                 with the user's response
        in it
        """
        response = self._transport.get(
            "/service/v3/auths/%s" % authorization_request_id,
            self._subject)

        if response.status_code == 204:
            authorization_response = None
        else:
            data = self._validate_response(
                response,
                AuthorizationResponseValidator)
            authorization_response = AuthorizationResponse(
                data, self._transport.loaded_issuer_private_keys)

        return authorization_response

    @api_call
    def session_start(self, user, authorization_request_id):
        """
        Request to start a Service Session for the End User which was derived
        from a authorization request
        :param user: LaunchKey Username, User Push ID, or Directory User ID for
        the End User
        :param authorization_request_id: Unique identifier returned by
        authorize()
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.EntityNotFound - The input username was
        not valid
        """
        self._transport.post("/service/v3/sessions",
                             self._subject,
                             username=user,
                             auth_request=authorization_request_id)

    @api_call
    def session_end(self, user):
        """
        Request to end a Service Session for the End User
        :param user: LaunchKey Username, User Push ID, or Directory User ID for
        the End User
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.EntityNotFound - The input username was
        not valid
        """
        self._transport.delete("/service/v3/sessions",
                               self._subject,
                               username=user)

    def handle_webhook(self, body, headers, method=None, path=None):
        """
        Handle a webhook callback
        In the event of a Logout webhook, be sure to call session_end() when
        you complete the process of ending the user's session in your
        implementation.  This will remove the corresponding Application from
        the authorization list on all of the the user's mobile devices.
        :param body: The raw body that was send in the POST content
        :param headers: A generic map of response headers. These will be used
        to access and validate authorization
        :param path:  The path of the request
        :param method: The HTTP method of the request
        :return: launchkey.entities.service.SessionEndRequest or
        launchkey.entities.service.AuthorizationResponse
        :raises launchkey.exceptions.UnexpectedWebhookRequest: when the
        request or its cannot be parsed or fails
        validation.
        :raises launchkey.exceptions.UnableToDecryptWebhookRequest: when the
        request is an authorization response webhook and the request body
        cannot be decrypted
        :raises launchkey.exceptions.UnexpectedAuthorizationResponse: when the
        decrypted auth package is missing required data. This error is
        indicative of a non webhook request being sent to the method.
        :raises launchkey.exceptions.UnexpectedKeyID: when the auth package in
        an authorization response webhook request body is decrypted using a
        public key whose private key is not known by the client. This can be
        a configuration issue.
        :raises launchkey.exceptions.UnexpectedDeviceResponse: when the auth
        package received from the device is invalid. This error is
        indicative of a man in the middle (MITM) attack.
        :raises launchkey.exceptions.WebhookAuthorizationError: when the
        "Authorization" header in the headers.
        """
        if method is None:
            warnings.warn("Not passing a valid request method string is "
                          "deprecated and will be required in the next "
                          "major version", PendingDeprecationWarning)

        if path is None:
            warnings.warn("Not passing a valid request path string is "
                          "deprecated and will be required in the next "
                          "major version", PendingDeprecationWarning)

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
            raise UnexpectedWebhookRequest(reason=reason)
        if "service_user_hash" in body:
            try:
                body = self._validate_response(
                    loads(body),
                    AuthorizeSSEValidator)
            except UnexpectedAPIResponse as reason:
                raise UnexpectedWebhookRequest(reason=reason)
            return SessionEndRequest(
                body['service_user_hash'],
                self._transport.parse_api_time(body['api_time']))
        else:
            try:
                decrypted_body = self._transport.decrypt_response(body)
                auth_response = loads(decrypted_body)
                return AuthorizationResponse(
                    auth_response,
                    self._transport.loaded_issuer_private_keys)
            except JWKESTException as reason:
                raise UnableToDecryptWebhookRequest(reason=reason)
            except KeyError as reason:
                raise UnexpectedAuthorizationResponse(reason=reason)
