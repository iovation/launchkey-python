"""Service Client"""

# pylint: disable=too-many-arguments

import warnings
from json import loads

from launchkey.exceptions import InvalidParameters, \
    UnableToDecryptWebhookRequest, UnexpectedAuthorizationResponse, \
    UnexpectedAPIResponse, UnexpectedWebhookRequest, XiovJWTValidationFailure,\
    XiovJWTDecryptionFailure
from launchkey.utils.shared import XiovJWTService, deprecated
from launchkey.entities.validation import AuthorizationResponseValidator, \
    AuthorizeSSEValidator, AuthorizeValidator, ServiceTOTPVerificationValidator
from launchkey.entities.service import AuthPolicy, AuthorizationResponse, \
    SessionEndRequest, AuthorizationRequest, AdvancedAuthorizationResponse, \
    DenialReason
from .base import BaseClient, api_call


class ServiceClient(BaseClient):
    """Service Client for interacting with Serive endpoints"""

    def __init__(self, subject_id, transport):
        super(ServiceClient, self).__init__('svc', subject_id, transport)
        self.x_iov_jwt_service = XiovJWTService(self._transport, self._subject)

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
                              push_body=None, denial_reasons=None):
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
        :param denial_reasons: List of denial reasons to present to the user if
        they deny the request. This list must include at least two items. At
        least one of the items must have a fraud value of false and at least
        one of the items must have a fraud value of true. If no denial_reasons
        are given the defaults will be used. If a list is provided and denial
        context inquiry is not enabled for the Directory, this request will
        error. This feature is only available for Directory Services.
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
        :raise: launchkey.exceptions.AuthorizationInProgress - Authorization
        request already exists for the requesting user. That request either
        needs to be responded to, expire out, or be canceled with
        cancel_authorization_request().
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
                    "launchkey.entities.service.AuthPolicy class")
            kwargs['policy'] = policy.get_policy()
        if denial_reasons is not None:
            if not isinstance(denial_reasons, (list, set)):
                raise InvalidParameters(
                    "Please ensure that input denial_reasons are a list of "
                    "launchkey.entities.service.DenialReason classes.")
            parsed_reasons = []
            for reason in denial_reasons:
                if not isinstance(reason, DenialReason):
                    raise InvalidParameters(
                        "Please verify that denial_reasons are "
                        "launchkey.entities.service.DenialReason classes.")
                parsed_reasons.append(
                    {"id": reason.denial_id, "reason": reason.reason,
                     "fraud": reason.fraud}
                )
            kwargs['denial_reasons'] = parsed_reasons

        response = self._transport.post("/service/v3/auths",
                                        self._subject, **kwargs)
        data = self._validate_response(response, AuthorizeValidator)
        return AuthorizationRequest(data.get('auth_request'),
                                    data.get('push_package'),
                                    data.get('device_ids'))

    @api_call
    def get_advanced_authorization_response(self, authorization_request_id):
        """
        Request the response for a previous authorization call.
        :param authorization_request_id: Unique identifier returned by
        authorization_request()
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.RequestTimedOut - The authorization
        request has not been responded to before the
        timeout period (5 minutes)
        :raise: launchkey.exceptions.AuthorizationRequestCanceled - The
        authorization request has been canceled so a response cannot be
        retrieved.
        :return: None if the user has not responded otherwise a
        launchkey.entities.service.AdvancedAuthorizationResponse object
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
            authorization_response = AdvancedAuthorizationResponse(
                data,
                self._transport
            )

        return authorization_response

    @deprecated
    def get_authorization_response(self, authorization_request_id):
        """
        NOTE: This method is being deprecated. Use
        `get_advanced_authorization_response` instead!

        Request the response for a previous authorization call.
        :param authorization_request_id: Unique identifier returned by
        authorization_request()
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.RequestTimedOut - The authorization
        request has not been responded to before the
        timeout period (5 minutes)
        :raise: launchkey.exceptions.AuthorizationRequestCanceled - The
        authorization request has been canceled so a response cannot be
        retrieved.
        :return: None if the user has not responded otherwise a
        launchkey.entities.service.AuthorizationResponse object
                 with the user's response
        in it
        """
        advanced_authorization_response = \
            self.get_advanced_authorization_response(authorization_request_id)

        if not advanced_authorization_response:
            return None

        return AuthorizationResponse(
            advanced_authorization_response.data,
            advanced_authorization_response.transport)

    @api_call
    def cancel_authorization_request(self, authorization_request_id):
        """
        Request to cancel an authorization request for the End User
        :param authorization_request_id: Unique identifier returned by
        authorization_request()
        :raise: launchkey.exceptions.InvalidParameters - Input parameters were
        not correct
        :raise: launchkey.exceptions.EntityNotFound - The authorization
        request does not exist.
        :raise: launchkey.exceptions.AuthorizationRequestCanceled - The
        authorization request has already been canceled.
        :raise: launchkey.exceptions.AuthorizationResponseExists - The
        authorization request has already been responded to so it cannot be
        canceled.
        """
        self._transport.delete(
            "/service/v3/auths/%s" % authorization_request_id,
            self._subject)

    @api_call
    def session_start(self, user, authorization_request_id):
        """
        Request to start a Service Session for the End User which was derived
        from a authorization request
        :param user: LaunchKey Username, User Push ID, or Directory User ID for
        the End User
        :param authorization_request_id: Unique identifier returned by
        authorization_request()
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

    @api_call
    def verify_totp(self, user, otp):
        """
        Verifies a given TOTP is valid for a given user.
        :param user: Unique value identifying the End User in your
        system. This value was used to create the Directory User and Link
        Device.
        :param otp: 6-8 digit OTP code for to verify.
        :return: Boolean stating whether the given OTP code is valid.
        :raise: launchkey.exceptions.EntityNotFound - Unable to find TOTP
        configuration for given user.
        """
        response = self._transport.post("/service/v3/totp",
                                        self._subject, identifier=user,
                                        otp=otp)
        data = self._validate_response(
            response,
            ServiceTOTPVerificationValidator)

        return data["valid"]

    def handle_advanced_webhook(self, body, headers, method=None, path=None):
        """
        Handle an advanced webhook callback
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
        launchkey.entities.service.AdvancedAuthorizationResponse
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
        try:
            if "service_user_hash" in "%s" % body:
                body = self.x_iov_jwt_service.verify_jwt_request(body, headers,
                                                                 method, path)
                try:
                    body = self._validate_response(
                        loads(body),
                        AuthorizeSSEValidator)
                except UnexpectedAPIResponse as reason:
                    raise UnexpectedWebhookRequest(reason=reason)
                result = SessionEndRequest(
                    body['service_user_hash'],
                    self._transport.parse_api_time(body['api_time']))
            else:
                try:
                    decrypted_body = self.x_iov_jwt_service.decrypt_jwe(
                        body, headers, method, path
                    )
                    auth_response = loads(decrypted_body)
                    result = AdvancedAuthorizationResponse(
                        auth_response,
                        self._transport
                    )
                except XiovJWTDecryptionFailure as reason:
                    raise UnableToDecryptWebhookRequest(reason=reason)
                except KeyError as reason:
                    raise UnexpectedAuthorizationResponse(reason=reason)
        except XiovJWTValidationFailure as reason:
            raise UnexpectedWebhookRequest(reason)

        return result

    @deprecated
    def handle_webhook(self, body, headers, method=None, path=None):
        """
        NOTE: This method is being deprecated. Use `handle_advanced_webhook`
        instead!

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
        advanced_authorization_response = self.handle_advanced_webhook(
            body, headers, method, path)

        if isinstance(advanced_authorization_response, SessionEndRequest):
            return advanced_authorization_response

        return AuthorizationResponse(
            advanced_authorization_response.data,
            advanced_authorization_response.transport)
