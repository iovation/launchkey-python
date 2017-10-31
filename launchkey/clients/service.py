from .base import BaseClient, api_call
from launchkey.exceptions import InvalidParameters
from launchkey.entities.validation import AuthorizationResponseValidator, AuthorizeSSEValidator, AuthorizeValidator
from launchkey.entities.service import AuthPolicy, AuthorizationResponse, SessionEndRequest
from json import loads


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
        :return: None if the user has not responded otherwise a launchkey.entities.service.AuthorizationResponse object
                 with the user's response
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
        :return: launchkey.entities.service.SessionEndRequest or launchkey.entities.service.AuthorizationResponse
        """
        self._transport.verify_jwt_response(headers, None, body, self._subject)
        if "service_user_hash" in body:
            body = self._validate_response(loads(body), AuthorizeSSEValidator)
            return SessionEndRequest(body['service_user_hash'], self._transport.parse_api_time(body['api_time']))
        else:
            body = loads(self._transport.decrypt_response(body))
            return AuthorizationResponse(body, self._transport.loaded_issuer_private_keys)
