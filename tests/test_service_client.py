import json
import unittest
from datetime import datetime
from json import dumps
from uuid import uuid4

from ddt import ddt, data, unpack
from formencode import Invalid
from jwkest import JWKESTException
from mock import MagicMock, ANY, patch
from six import assertRaisesRegex, assertCountEqual

from launchkey.clients import ServiceClient
from launchkey.clients.service import AuthorizationResponse, SessionEndRequest, AuthPolicy
from launchkey.entities.service import AuthorizationRequest, DenialReason, \
    GeoFence, TimeFence
from launchkey.entities.service.policy import FactorsPolicy, \
    ConditionalGeoFencePolicy, GeoCircleFence, TerritoryFence, \
    MethodAmountPolicy, LegacyPolicy, AuthorizationResponsePolicy, \
    Requirement
from launchkey.exceptions import LaunchKeyAPIException, InvalidParameters, \
    InvalidPolicyInput, PolicyFailure, \
    EntityNotFound, RateLimited, RequestTimedOut, UnexpectedAPIResponse, \
    UnexpectedDeviceResponse, UnexpectedKeyID, \
    InvalidGeoFenceName, InvalidPolicyFormat, InvalidJWTResponse, \
    UnexpectedWebhookRequest, \
    UnableToDecryptWebhookRequest, UnexpectedAuthorizationResponse, \
    WebhookAuthorizationError, AuthorizationRequestCanceled, \
    AuthorizationResponseExists, XiovJWTValidationFailure, \
    XiovJWTDecryptionFailure, InvalidFenceType, InvalidPolicyAttributes
from launchkey.transports import JOSETransport
from launchkey.transports.base import APIResponse


@ddt
class TestServiceClient(unittest.TestCase):

    def setUp(self):
        self._transport = MagicMock()
        self._response = APIResponse({}, {}, 200)
        self._transport.post.return_value = self._response
        self._transport.get.return_value = self._response
        self._transport.put.return_value = self._response
        self._transport.delete.return_value = self._response
        self._device_response = {"auth_request": str(uuid4()), "response": True, "device_id": str(uuid4()),
                                 "service_pins": ["1234", "3456", "5678"]}
        self._transport.loaded_issuer_private_key.decrypt.return_value = dumps(self._device_response)
        self._service_id = uuid4()
        self._issuer = "svc:{}".format(self._service_id)
        self._service_client = ServiceClient(self._service_id, self._transport)
        self._service_client._transport._verify_jwt_response = MagicMock()

    def test_authorize_calls_authorization_request(self):
        policy = AuthPolicy()
        auth_response = AuthorizationRequest(str(uuid4()), None)
        self._service_client.authorization_request = MagicMock(return_value=auth_response)
        self._service_client.authorize('user', 'context', policy, 'title', 30,
                                       'push_title', 'push_body')
        self._service_client.authorization_request.assert_called_once_with(
            'user', 'context', policy, 'title', 30, 'push_title', 'push_body')

    def test_authorize_returns_auth_request_id_from_authorization_request_response(self):
        expected = str(uuid4())
        self._response.data = {"auth_request": expected}
        actual = self._service_client.authorize('user', 'context', AuthPolicy())
        self.assertEqual(actual, expected)

    def test_authorization_request_success(self):
        self._response.data = {"auth_request": "value"}
        policy = MagicMock(spec=AuthPolicy)
        policy.get_policy.return_value = "policy"
        self._service_client.authorization_request("user", "context", policy)
        self._transport.post.assert_called_once_with(
            '/service/v3/auths', self._issuer, username="user",
            context="context", policy="policy"
        )

    def test_authorization_request_response_has_auth_request(self):
        self._response.data = {"auth_request": "expected value"}
        self.assertEqual('expected value', self._service_client.authorization_request(ANY).auth_request)

    def test_authorization_request_response_has_push_package(self):
        self._response.data = {"auth_request": "auth", "push_package": "expected package"}
        self.assertEqual('expected package', self._service_client.authorization_request(ANY).push_package)

    def test_authorization_request_invalid_policy_input(self):
        self._response.data = {"auth_request": ANY}
        with self.assertRaises(InvalidParameters):
            self._service_client.authorization_request(ANY, ANY, ANY)

    def test_authorization_request_unexpected_result(self):
        self._response.data = {MagicMock(spec=str): ANY}
        with self.assertRaises(UnexpectedAPIResponse):
            self._service_client.authorization_request(ANY)

    def test_authorization_request_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._service_client.authorization_request(ANY)

    def test_authorization_request_invalid_policy(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "SVC-002", "error_detail": ""}, 400)
        with self.assertRaises(InvalidPolicyInput):
            self._service_client.authorization_request(ANY)

    def test_authorization_request_policy_failure(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "SVC-003", "error_detail": ""}, 400)
        with self.assertRaises(PolicyFailure):
            self._service_client.authorization_request(ANY)

    def test_authorization_request_entity_not_found(self):
        self._transport.post.side_effect = LaunchKeyAPIException({}, 404)
        with self.assertRaises(EntityNotFound):
            self._service_client.authorization_request(ANY)

    def test_authorization_request_rate_limited(self):
        self._transport.post.side_effect = LaunchKeyAPIException({}, 429)
        with self.assertRaises(RateLimited):
            self._service_client.authorization_request(ANY)

    def test_authorization_request_default(self):
        self._response.data = {"auth_request": "expected value"}
        self._service_client.authorization_request("my_user")
        self._transport.post.assert_called_with(ANY, ANY, username="my_user")

    def test_authorization_request_context(self):
        self._response.data = {"auth_request": "expected value"}
        self._service_client.authorization_request("my_user", context="Here's some context!")
        self._transport.post.assert_called_with(ANY, ANY, username="my_user", context="Here's some context!")

    def test_authorization_request_title(self):
        self._response.data = {"auth_request": "expected value"}
        self._service_client.authorization_request("my_user", title="Here's a title!")
        self._transport.post.assert_called_with(ANY, ANY, username="my_user", title="Here's a title!")

    def test_authorization_request_push_title(self):
        self._response.data = {"auth_request": "expected value"}
        self._service_client.authorization_request("my_user",
                                                   push_title="A Push Title")
        self._transport.post.assert_called_with(ANY, ANY, username="my_user",
                                                push_title="A Push Title")

    def test_authorization_request_push_body(self):
        self._response.data = {"auth_request": "expected value"}
        self._service_client.authorization_request("my_user",
                                                   push_body="Push Body")
        self._transport.post.assert_called_with(ANY, ANY, username="my_user",
                                                push_body="Push Body")

    def test_authorization_request_ttl(self):
        self._response.data = {"auth_request": "expected value"}
        self._service_client.authorization_request("my_user", ttl=336)
        self._transport.post.assert_called_with(ANY, ANY, username="my_user", ttl=336)

    def test_authorization_request_denial_reasons_as_list(self):
        self._response.data = {"auth_request": "expected value"}
        self._service_client.authorization_request("my_user", denial_reasons=[
            DenialReason('fraud', 'Fraud Reason', True),
            DenialReason('not', 'Not Fraud Reason', False)
        ])
        self._transport.post.assert_called_with(
            ANY, ANY, username="my_user",
            denial_reasons=[
                {"id": 'fraud', "reason": 'Fraud Reason', "fraud": True},
                {"id": 'not', "reason": 'Not Fraud Reason', "fraud": False}
            ]
        )

    def test_authorization_request_denial_reasons_as_set(self):
        self._response.data = {"auth_request": "expected value"}
        self._service_client.authorization_request("my_user", denial_reasons={
            DenialReason('fraud', 'Fraud Reason', True),
            DenialReason('not', 'Not Fraud Reason', False)
        })
        denial_reasons = self._transport.post.call_args[1]['denial_reasons']
        self.assertEqual(len(denial_reasons), 2)
        self.assertIn(
            {"id": 'fraud', "reason": 'Fraud Reason', "fraud": True},
            denial_reasons
        )
        self.assertIn(
            {"id": 'not', "reason": 'Not Fraud Reason', "fraud": False},
            denial_reasons
        )

    @data(
        "e6e809ab-9e83-47a2-924a-64ae3d424a45",
        True,
        False,
        {"Test": "Data"},
        DenialReason(1, 2, 3)
    )
    def test_authorization_request_denial_reasons_invalid_input(self, reasons):
        with self.assertRaises(InvalidParameters):
            self._service_client.authorization_request(
                "my_user",
                denial_reasons=reasons
            )

    @data(
        "e6e809ab-9e83-47a2-924a-64ae3d424a45",
        True,
        False,
        {"Test": "Data"}
    )
    def test_authorization_request_denial_reasons_invalid_reason(self,
                                                                 reason):
        with self.assertRaises(InvalidParameters):
            self._service_client.authorization_request(
                "my_user",
                denial_reasons=[reason]
            )

    @patch("launchkey.entities.service.loads")
    @patch("launchkey.entities.service.AuthorizationResponsePackageValidator")
    def test_get_authorization_response_success(
            self, json_loads_patch,
            auth_response_package_validator_patch):
        json_loads_patch.return_value = MagicMock(spec=dict)
        auth_response_package_validator_patch.return_value = MagicMock(spec=dict)
        public_key_id = str(uuid4())
        self._service_client._transport.loaded_issuer_private_keys = {public_key_id: MagicMock()}
        self._response.data = {
            "auth": ANY,
            "service_user_hash": ANY,
            "user_push_id": ANY,
            "org_user_hash": ANY,
            "public_key_id": public_key_id
        }
        actual = self._service_client.get_authorization_response(
            "auth-request-id")
        self._transport.get.assert_called_once_with(
            "/service/v3/auths/auth-request-id", self._issuer)
        self.assertIsInstance(actual, AuthorizationResponse)

    def test_get_authorization_response_unexpected_response(self):
        self._response.data = {MagicMock(spec=str): ANY}
        with self.assertRaises(UnexpectedAPIResponse):
            self._service_client.get_authorization_response(ANY)

    def test_get_authorization_response_no_response(self):
        self._response.status_code = 204
        self.assertIsNone(self._service_client.get_authorization_response(ANY))

    def test_get_authorization_response_invalid_params(self):
        self._transport.get.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._service_client.get_authorization_response(ANY)

    def test_get_authorization_response_response_exists(self):
        self._transport.get.side_effect = LaunchKeyAPIException(
            {"error_code": "SVC-006", "error_detail": ""}, 400)
        with self.assertRaises(AuthorizationResponseExists):
            self._service_client.get_authorization_response(ANY)

    def test_get_authorization_response_timeout(self):
        self._transport.get.side_effect = LaunchKeyAPIException({}, 408)
        with self.assertRaises(RequestTimedOut):
            self._service_client.get_authorization_response(ANY)

    def test_cancel_authorization_request_success(self):
        self._service_client.cancel_authorization_request("auth-request-id")
        self._transport.delete.assert_called_once_with(
            "/service/v3/auths/auth-request-id", self._issuer
        )

    def test_cancel_authorization_request_authorization_response_exists(self):
        self._transport.delete.side_effect = LaunchKeyAPIException(
            {"error_code": "SVC-006", "error_detail": ""}, 400)
        with self.assertRaises(AuthorizationResponseExists):
            self._service_client.cancel_authorization_request(
                "auth-request-id"
            )

    def test_cancel_authorization_request_authorization_request_canceled(self):
        self._transport.delete.side_effect = LaunchKeyAPIException(
            {"error_code": "SVC-007", "error_detail": ""}, 400)
        with self.assertRaises(AuthorizationRequestCanceled):
            self._service_client.cancel_authorization_request(
                "auth-request-id"
            )

    def test_cancel_authorization_request_invalid_params(self):
        self._transport.delete.side_effect = LaunchKeyAPIException(
            {"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._service_client.cancel_authorization_request(
                "auth-request-id"
            )

    def test_session_start_success(self):
        self._service_client.session_start("user-id", "auth-request-id")
        self._transport.post.assert_called_once_with(
            "/service/v3/sessions", self._issuer, username="user-id",
            auth_request="auth-request-id")

    def test_session_start_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._service_client.session_start(ANY, ANY)

    def test_session_start_entity_not_found(self):
        self._transport.post.side_effect = LaunchKeyAPIException({}, 404)
        with self.assertRaises(EntityNotFound):
            self._service_client.session_start(ANY, ANY)

    def test_session_end_success(self):
        self._service_client.session_end("user-id")
        self._transport.delete.assert_called_once_with(
            "/service/v3/sessions", self._issuer, username="user-id")

    def test_session_end_invalid_params(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._service_client.session_end(ANY)

    def test_session_end_entity_not_found(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({}, 404)
        with self.assertRaises(EntityNotFound):
            self._service_client.session_end(ANY)


class TestHandleWebhookRegression(unittest.TestCase):

    _subject_id = uuid4()

    PUBLIC_KEY_ID = "Public Key ID"

    def setUp(self):
        self._transport = MagicMock(spec=JOSETransport)
        self._transport.decrypt_response.return_value = '{"public_key_id":"' + self.PUBLIC_KEY_ID + '", "auth": null}'
        self._service_client = ServiceClient(self._subject_id, self._transport)
        self._headers = {"X-IOV-JWT": "jwt", "Other Header": "jwt"}

        self._issuer_private_key = MagicMock()
        self._transport.loaded_issuer_private_keys = {self.PUBLIC_KEY_ID: self._issuer_private_key}

        patcher = patch("launchkey.entities.validation.AuthorizationResponsePackageValidator.to_python")
        self._authorization_response_validator_patch = patcher.start()
        self.addCleanup(patcher.stop)
        self._authorization_response_validator_patch.return_value = MagicMock(spec=dict)

        patcher = patch("launchkey.clients.service.loads")
        self._service_client_loads_patch = patcher.start()
        self.addCleanup(patcher.stop)
        self._service_client_loads_patch.side_effect = json.loads

        patcher = patch("launchkey.entities.service.loads")
        self._service_entity_loads_patch = patcher.start()
        self.addCleanup(patcher.stop)
        self._service_entity_loads_patch.return_value = MagicMock(spec=dict)

        patcher = patch("launchkey.entities.validation.AuthorizeSSEValidator")
        self._authorize_sse_validator_patch = patcher.start()
        self.addCleanup(patcher.stop)
        self._authorize_sse_validator_patch.return_value = MagicMock(spec=dict)

    def test_webhook_session_end(self):
        request = dumps({"service_user_hash": str(uuid4()),
                         "api_time": str(datetime.utcnow())[:19].replace(" ", "T") + "Z"})
        self.assertIsInstance(self._service_client.handle_webhook(request, self._headers), SessionEndRequest)

    def test_webhook_session_end_invalid_input(self):
        request = dumps({"service_user_hash": str(uuid4())})
        with self.assertRaises(UnexpectedWebhookRequest):
            self.assertIsInstance(self._service_client.handle_webhook(request, self._headers), SessionEndRequest)

    def test_webhook_authorization_response_returns_authorization_response(self):
        self.assertIsInstance(self._service_client.handle_webhook(MagicMock(), self._headers), AuthorizationResponse)

    def test_calls_verify_jwt_request_with_expected_parameters(self):
        self._headers['X-IOV-JWT'] = 'compact.jwt.string'
        self._service_client.handle_webhook('body', self._headers, 'method', 'path')
        self._transport.verify_jwt_request.assert_called_with("compact.jwt.string", 'svc:' + str(self._subject_id), 'method', 'path', 'body')

    def test_handle_webhook_handles_jwt_validation_errors(self):
        self._transport.verify_jwt_request.side_effect = InvalidJWTResponse
        with self.assertRaises(UnexpectedWebhookRequest):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_session_end_requests_handles_data_validation_errors(self):
        self._authorize_sse_validator_patch.to_python.side_effect = Invalid
        with self.assertRaises(UnexpectedWebhookRequest):
            self._service_client.handle_webhook(dumps({"service_user_hash": str(uuid4())}), self._headers)

    def test_handle_webhook_auth_response_handles_json_loads_errors(self):
        self._transport.decrypt_response.return_value = '{"public_key_id":"' + self.PUBLIC_KEY_ID + '","auth":null}'
        self._service_entity_loads_patch.side_effect = ValueError
        with self.assertRaises(UnexpectedDeviceResponse):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_auth_response_requests_handles_unexpected_key(self, ):
        self._transport.decrypt_response.side_effect = UnexpectedKeyID
        with self.assertRaises(UnexpectedKeyID):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_for_authorization_response_handles_jwe_decryption_errors(self):
        self._transport.decrypt_response.side_effect = JWKESTException
        with self.assertRaises(UnableToDecryptWebhookRequest):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_for_invalid_response_when_validating_auth_response(self):
        self._authorization_response_validator_patch.side_effect = Invalid
        with self.assertRaises(UnexpectedDeviceResponse):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_for_response_without_auth_package_parsing_auth_response(self):
        self._transport.decrypt_response.return_value = '{"public_key_id":"' + self.PUBLIC_KEY_ID + '"}'
        with self.assertRaises(UnexpectedAuthorizationResponse):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_no_jwt_header_raises_webhook_authorization_error(self):
        del self._headers['X-IOV-JWT']
        with self.assertRaises(WebhookAuthorizationError):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_session_end_with_request_as_bytes(self):
        request = bytearray(dumps({"service_user_hash": str(uuid4()),
                            "api_time": str(datetime.utcnow())[:19].replace(" ", "T") + "Z"}), "utf-8")
        self.assertIsInstance(self._service_client.handle_webhook(request, self._headers), SessionEndRequest)


class TestHandleWebhook(unittest.TestCase):

    _subject_id = uuid4()

    PUBLIC_KEY_ID = "Public Key ID"

    def setUp(self):
        patcher = patch("launchkey.clients.service.XiovJWTService")
        self._x_iov_jwt_service_patch = patcher.start().return_value
        self.addCleanup(patcher.stop)
        self._x_iov_jwt_service_patch.decrypt_jwe.return_value = '{"public_key_id":"' + self.PUBLIC_KEY_ID + '", "auth": null}'

        self._transport = MagicMock(spec=JOSETransport)
        self._service_client = ServiceClient(self._subject_id, self._transport)
        self._headers = {"X-IOV-JWT": "jwt", "Other Header": "jwt"}

        self._issuer_private_key = MagicMock()
        self._transport.loaded_issuer_private_keys = {self.PUBLIC_KEY_ID: self._issuer_private_key}

        patcher = patch("launchkey.entities.validation.AuthorizationResponsePackageValidator.to_python")
        self._authorization_response_validator_patch = patcher.start()
        self.addCleanup(patcher.stop)
        self._authorization_response_validator_patch.return_value = MagicMock(spec=dict)

        patcher = patch("launchkey.clients.service.loads")
        self._service_client_loads_patch = patcher.start()
        self.addCleanup(patcher.stop)
        self._service_client_loads_patch.side_effect = json.loads

        patcher = patch("launchkey.entities.service.loads")
        self._service_entity_loads_patch = patcher.start()
        self.addCleanup(patcher.stop)
        self._service_entity_loads_patch.return_value = MagicMock(spec=dict)

        patcher = patch("launchkey.entities.validation.AuthorizeSSEValidator")
        self._authorize_sse_validator_patch = patcher.start()
        self.addCleanup(patcher.stop)
        self._authorize_sse_validator_patch.return_value = MagicMock(spec=dict)

    def test_webhook_session_end(self):
        body = dumps({"service_user_hash": str(uuid4()),
                         "api_time": str(datetime.utcnow())[:19].replace(" ", "T") + "Z"})
        self._x_iov_jwt_service_patch.verify_jwt_request.return_value = body
        self.assertIsInstance(self._service_client.handle_webhook(body, self._headers), SessionEndRequest)

    def test_webhook_session_end_invalid_input(self):
        body = dumps({"service_user_hash": str(uuid4())})
        self._x_iov_jwt_service_patch.verify_jwt_request.return_value = body
        with self.assertRaises(UnexpectedWebhookRequest):
            self.assertIsInstance(self._service_client.handle_webhook(body, self._headers), SessionEndRequest)

    def test_webhook_authorization_response_returns_authorization_response(self):
        self.assertIsInstance(self._service_client.handle_webhook(MagicMock(), self._headers), AuthorizationResponse)

    def test_calls_decrypt_jwe_request_with_expected_parameters(self):
        self._service_client.handle_webhook('body', self._headers, 'method', 'path')
        self._x_iov_jwt_service_patch.decrypt_jwe.assert_called_with(
            "body", self._headers, "method", "path"
        )

    def test_handle_webhook_handles_jwt_validation_errors(self):
        self._x_iov_jwt_service_patch.decrypt_jwe.side_effect = XiovJWTValidationFailure
        with self.assertRaises(UnexpectedWebhookRequest):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_session_end_requests_handles_data_validation_errors(self):
        self._authorize_sse_validator_patch.to_python.side_effect = Invalid
        body = dumps({"service_user_hash": str(uuid4())})
        self._x_iov_jwt_service_patch.verify_jwt_request.return_value = body
        with self.assertRaises(UnexpectedWebhookRequest):
            self._service_client.handle_webhook(body, self._headers)

    def test_handle_webhook_auth_response_handles_json_loads_errors(self):
        self._transport.decrypt_response.return_value = '{"public_key_id":"' + self.PUBLIC_KEY_ID + '","auth":null}'
        self._service_entity_loads_patch.side_effect = ValueError
        with self.assertRaises(UnexpectedDeviceResponse):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_auth_response_requests_handles_unexpected_key(self,):
        self._x_iov_jwt_service_patch.decrypt_jwe.side_effect = UnexpectedKeyID
        with self.assertRaises(UnexpectedKeyID):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_for_authorization_response_handles_jwe_decryption_errors(self):
        self._x_iov_jwt_service_patch.decrypt_jwe.side_effect = XiovJWTDecryptionFailure
        with self.assertRaises(UnableToDecryptWebhookRequest):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_for_invalid_response_when_validating_auth_response(self):
        self._authorization_response_validator_patch.side_effect = Invalid
        with self.assertRaises(UnexpectedDeviceResponse):
            self._service_client.handle_webhook(MagicMock(), self._headers)

    def test_handle_webhook_for_response_without_auth_package_parsing_auth_response(self):
        self._x_iov_jwt_service_patch.decrypt_jwe.return_value = '{"public_key_id":"' + self.PUBLIC_KEY_ID + '"}'
        with self.assertRaises(UnexpectedAuthorizationResponse):
            self._service_client.handle_webhook(MagicMock(), self._headers)


@ddt
class TestLegacyPolicyObject(unittest.TestCase):

    @data(1, True, 0, False)
    def test_knowledge_factor_success(self, value):
        AuthPolicy(knowledge=value)

    @data(1, True, 0, False)
    def test_inherence_factor_success(self, value):
        AuthPolicy(inherence=value)

    @data(1, True, 0, False)
    def test_possession_factor_success(self, value):
        AuthPolicy(possession=value)

    @data(2, 3, 4, 5, None)
    def test_knowledge_factor_failure(self, value):
        with self.assertRaises(InvalidParameters):
            AuthPolicy(knowledge=value)

    @data(2, 3, 4, 5, None)
    def test_inherence_factor_failure(self, value):
        with self.assertRaises(InvalidParameters):
            AuthPolicy(inherence=value)

    @data(2, 3, 4, 5, None)
    def test_possession_factor_failure(self, value):
        with self.assertRaises(InvalidParameters):
            AuthPolicy(possession=value)

    def test_mixing_factor_requirements_exception(self):
        with self.assertRaises(InvalidParameters):
            AuthPolicy(any=1, knowledge=1, inherence=1, possession=1)

    def test_empty_policy_creation(self):
        policy = AuthPolicy()
        retrieved = policy.get_policy()
        self.assertIn('minimum_requirements', retrieved)
        self.assertEqual(retrieved['minimum_requirements'], [])

    @data(1, 2, 3, 4, 5)
    def test_setting_any_requirement(self, value):
        policy = AuthPolicy(any=value)
        self.assertEqual(policy.get_policy()['minimum_requirements'][0]['any'], value)

    def test_setting_specific_requirement(self):
        knowledge = 0
        inherence = 1
        possession = True
        policy = AuthPolicy(knowledge=knowledge, inherence=inherence, possession=possession)
        self.assertEqual(policy.get_policy()['minimum_requirements'][0]['knowledge'], int(knowledge))
        self.assertEqual(policy.get_policy()['minimum_requirements'][0]['inherence'], int(inherence))
        self.assertEqual(policy.get_policy()['minimum_requirements'][0]['possession'], int(possession))

    def test_jailbreak_protection_default(self):
        policy = AuthPolicy()
        self.assertEqual(len(policy.get_policy()['factors']), 1)
        self.assertEqual(policy.get_policy()['factors'][0]['factor'], 'device integrity')
        self.assertEqual(policy.get_policy()['factors'][0]['attributes']['factor enabled'], 0)

    def test_jailbreak_protection_true(self):
        policy = AuthPolicy(jailbreak_protection=True)
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 1)
        factor = retrieved['factors'][0]
        self.assertEqual(factor['factor'], 'device integrity')
        self.assertEqual(factor['attributes']['factor enabled'], 1)

    def test_add_geofence_success(self):
        policy = AuthPolicy()
        latitude = MagicMock(spec=int)
        longitude = MagicMock(spec=int)
        radius = MagicMock(spec=int)
        policy.add_geofence(latitude, longitude, radius)
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 2)
        factor = retrieved['factors'][1] if retrieved['factors'][1]['factor'] == 'geofence' else retrieved['factors'][0]
        self.assertEqual(factor['factor'], 'geofence')
        self.assertEqual(len(factor['attributes']['locations']), 1)
        location = factor['attributes']['locations'][0]
        self.assertEqual(location['latitude'], float(latitude))
        self.assertEqual(location['longitude'], float(longitude))
        self.assertEqual(location['radius'], float(radius))
        # Add a second geofence
        latitude2 = MagicMock(spec=int)
        longitude2 = MagicMock(spec=int)
        radius2 = MagicMock(spec=int)
        policy.add_geofence(latitude2, longitude2, radius2)
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 2)
        factor = retrieved['factors'][1] if retrieved['factors'][1]['factor'] == 'geofence' else retrieved['factors'][0]
        self.assertEqual(factor['factor'], 'geofence')
        self.assertEqual(len(factor['attributes']['locations']), 2)
        location = factor['attributes']['locations'][1]
        self.assertEqual(location['latitude'], float(latitude2))
        self.assertEqual(location['longitude'], float(longitude2))
        self.assertEqual(location['radius'], float(radius2))

    @data('invalid', None, "")
    def test_add_geofence_invalid_lat_input(self, value):
        policy = AuthPolicy()
        with self.assertRaises(InvalidParameters):
            policy.add_geofence(value, 0, 0)

    @data('invalid', None, "")
    def test_add_geofence_invalid_long_input(self, value):
        policy = AuthPolicy()
        with self.assertRaises(InvalidParameters):
            policy.add_geofence(0, value, 0)

    @data('invalid', None, "")
    def test_add_geofence_invalid_radius_input(self, value):
        policy = AuthPolicy()
        with self.assertRaises(InvalidParameters):
            policy.add_geofence(0, 0, value)

    @data('myfence', 'my fence', '** fence 1234')
    def test_remove_geofence(self, name):
        policy = AuthPolicy()
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 1)
        self.assertEqual(policy.geofences, [])

        policy.add_geofence(MagicMock(spec=int), MagicMock(spec=int), MagicMock(spec=int), name)
        self.assertEqual(len(policy.geofences), 1)
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 2)
        self.assertEqual(len(retrieved['factors'][1]['attributes']['locations']), 1)

        policy.remove_geofence(name)
        self.assertEqual(policy.geofences, [])
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors'][1]['attributes']['locations']), 0)

    def test_remove_invalid_geofence(self):
        policy = AuthPolicy()
        policy.add_geofence(1, 1, 2)
        with self.assertRaises(InvalidGeoFenceName):
            policy.remove_geofence(MagicMock(spec=str))

    def test_remove_partially_invalid_geofence(self):
        policy = AuthPolicy()
        policy.add_geofence(1, 1, 2, 'name')
        policy.geofences.pop()
        with self.assertRaises(InvalidGeoFenceName):
            policy.remove_geofence('name')

    def test_invalid_policy(self):
        policy = AuthPolicy()
        policy._policy['factors'].append(uuid4())
        with self.assertRaises(InvalidParameters):
            policy.get_policy()

    def test_eq_match(self):
        policy = AuthPolicy()
        policy.add_geofence(1, 2, 3, '123')
        policy2 = AuthPolicy()
        policy2.set_policy(policy.get_policy())
        self.assertTrue(policy == policy2)

    def test_eq_mismatch(self):
        policy = AuthPolicy()
        policy.add_geofence(1, 2, 3, '123')
        policy2 = AuthPolicy()
        self.assertNotEqual(policy, policy2)
        policy2.add_geofence(1, 2, 2, '122')
        self.assertTrue(policy != policy2)

    @data("test", {}, True, False, None)
    def test_eq_mismatch_non_object(self, value):
        policy = AuthPolicy()
        self.assertFalse(policy == value)

    def test_eq_mismatch_non_object_matching_policy(self):
        policy = AuthPolicy(any=1)
        self.assertFalse(policy == AuthPolicy().get_policy())

    @data(True, False)
    def test_require_jailbreak_protection_new(self, status):
        policy = AuthPolicy()
        policy._policy['factors'] = []
        policy.require_jailbreak_protection(status)
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 1)
        self.assertEqual(retrieved['factors'][0]['attributes']['factor enabled'], 1 if status else 0)

    @data(True, False)
    def test_require_jailbreak_protection_existing(self, status):
        policy = AuthPolicy()
        policy.require_jailbreak_protection(status)
        retrieved = policy.get_policy()
        self.assertEqual(len(retrieved['factors']), 1)
        self.assertEqual(retrieved['factors'][0]['attributes']['factor enabled'], 1 if status else 0)

    def test_set_policy_dict(self):
        policy = AuthPolicy()
        self.assertEqual(len(policy.geofences), 0)
        policy.set_policy({'minimum_requirements': [], 'factors': []})

    def test_set_policy_json(self):
        policy = AuthPolicy()
        self.assertEqual(len(policy.geofences), 0)
        policy.set_policy(dumps({'minimum_requirements': [], 'factors': []}))

    def test_set_policy_invalid_json(self):
        with self.assertRaises(InvalidPolicyFormat):
            AuthPolicy().set_policy("{{{{Invalid JSON")

    @data({}, {'minimum_requirements': []}, {'factors': []})
    def test_set_policy_invalid(self, policy):
        with self.assertRaises(InvalidPolicyFormat):
            AuthPolicy().set_policy(policy)

    def test_set_policy_geofence(self):
        policy = AuthPolicy()
        self.assertEqual(len(policy.geofences), 0)
        policy.set_policy(
            {
                'minimum_requirements': [],
                'factors': [
                    {
                        'quickfail': False,
                        'priority': 1,
                        'requirement': 'forced requirement',
                        'attributes': {
                            'locations': [
                                {'latitude': 1.0, 'radius': 3.0, 'name': '123', 'longitude': 2.0}]},
                        'factor': 'geofence'
                    }
                ]
            }
        )
        self.assertEqual(len(policy.geofences), 1)
        self.assertEqual(policy.geofences[0].latitude, 1.0)
        self.assertEqual(policy.geofences[0].longitude, 2.0)
        self.assertEqual(policy.geofences[0].radius, 3.0)
        self.assertEqual(policy.geofences[0].name, '123')\


    @data(1, 0)
    def test_set_policy_jailbreak(self, enabled):
        policy = AuthPolicy()
        self.assertEqual(len(policy.geofences), 0)
        policy.set_policy(
            {
                'minimum_requirements': [],
                'factors': [
                    {
                        'quickfail': False,
                        'priority': 1,
                        'requirement': 'forced requirement',
                        'attributes': {'factor enabled': enabled},
                        'factor': 'device integrity'
                    }
                ]
            }
        )
        self.assertEqual(policy.jailbreak_protection, True if enabled else False)

    def test_set_minimum_requirments_all(self):
        policy = AuthPolicy()
        policy.set_policy(
            {
                'minimum_requirements': [
                    {
                        'possession': 1,
                        'requirement': 'authenticated',
                        'all': 1,
                        'inherence': 1,
                        'knowledge': 1
                    }
                ],
                'factors': []
            }
        )
        self.assertEqual(policy.minimum_amount, 1)
        self.assertIn('possession', policy.minimum_requirements)
        self.assertIn('inherence', policy.minimum_requirements)
        self.assertIn('knowledge', policy.minimum_requirements)

    @data((1, 1, 1, 1), (1, 1, 1, 0), (1, 1, 0, 1), (1, 0, 1, 1), (1, 0, 0, 1), (0, 0, 0, 0), (0, 0, 0, 1))
    @unpack
    def test_set_minimum_requirements(self, possession, inherence, knowledge, minimum_requirements):
        policy = AuthPolicy()
        policy.set_policy(
            {
                'minimum_requirements': [
                    {
                        'possession': possession,
                        'requirement': 'authenticated',
                        'any': minimum_requirements,
                        'inherence': inherence,
                        'knowledge': knowledge
                    }
                ],
                'factors': []
            }
        )
        self.assertEqual(policy.minimum_amount, minimum_requirements)
        if possession:
            self.assertIn('possession', policy.minimum_requirements)
        else:
            self.assertNotIn('possession', policy.minimum_requirements)
        if inherence:
            self.assertIn('inherence', policy.minimum_requirements)
        else:
            self.assertNotIn('inherence', policy.minimum_requirements)
        if knowledge:
            self.assertIn('knowledge', policy.minimum_requirements)
        else:
            self.assertNotIn('knowledge', policy.minimum_requirements)


class TestConditionalGeoFencePolicy(unittest.TestCase):
    DEFAULT_INSIDE_POLICY = FactorsPolicy(deny_rooted_jailbroken=False, deny_emulator_simulator=False,
                                          knowledge_required=True)
    DEFAULT_OUTSIDE_POLICY = FactorsPolicy(deny_rooted_jailbroken=False, deny_emulator_simulator=False,
                                           possession_required=True)

    def test_default_instantiation(self):
        geofence_policy = ConditionalGeoFencePolicy(self.DEFAULT_INSIDE_POLICY, self.DEFAULT_OUTSIDE_POLICY)

        self.assertIsInstance(geofence_policy, ConditionalGeoFencePolicy)
        self.assertEqual(0, len(geofence_policy.fences))
        self.assertEqual(None, geofence_policy.inside.deny_emulator_simulator)
        self.assertEqual(None, geofence_policy.inside.deny_rooted_jailbroken)
        self.assertEqual(list(), geofence_policy.inside.fences)
        self.assertTrue(geofence_policy.inside.knowledge_required)
        self.assertEqual(None, geofence_policy.outside.deny_emulator_simulator)
        self.assertEqual(None, geofence_policy.outside.deny_rooted_jailbroken)
        self.assertEqual(list(), geofence_policy.outside.fences)
        self.assertTrue(geofence_policy.outside.possession_required)
        self.assertEqual(False, geofence_policy.deny_rooted_jailbroken)
        self.assertEqual(False, geofence_policy.deny_emulator_simulator)

    def test_set_inside_policy_as_method_policy(self):
        inside = MethodAmountPolicy(amount=1)
        geofence_policy = ConditionalGeoFencePolicy(inside=inside, outside=self.DEFAULT_OUTSIDE_POLICY)
        self.assertEqual(1, geofence_policy.inside.amount)

    def test_setting_deny_rooted_jailbroken(self):
        geofence_policy = ConditionalGeoFencePolicy(self.DEFAULT_INSIDE_POLICY, self.DEFAULT_OUTSIDE_POLICY,
                                                    deny_rooted_jailbroken=True, deny_emulator_simulator=False)
        self.assertEqual(True, geofence_policy.deny_rooted_jailbroken)

    def test_setting_deny_emulator_simulator(self):
        geofence_policy = ConditionalGeoFencePolicy(self.DEFAULT_INSIDE_POLICY, self.DEFAULT_OUTSIDE_POLICY,
                                                    deny_rooted_jailbroken=False, deny_emulator_simulator=True)
        self.assertEqual(True, geofence_policy.deny_emulator_simulator)

    def test_setting_fences(self):
        fences = [GeoCircleFence(200, 320, 350)]
        geofence_policy = ConditionalGeoFencePolicy(self.DEFAULT_INSIDE_POLICY, self.DEFAULT_OUTSIDE_POLICY,
                                                    deny_rooted_jailbroken=False, deny_emulator_simulator=True,
                                                    fences=fences)

        self.assertEqual(fences, geofence_policy.fences)

        fences = [GeoCircleFence(200, 250, 1000), TerritoryFence("US", "US-CA", "89172")]
        geofence_policy = ConditionalGeoFencePolicy(self.DEFAULT_INSIDE_POLICY, self.DEFAULT_OUTSIDE_POLICY,
                                                    deny_rooted_jailbroken=False, deny_emulator_simulator=True,
                                                    fences=fences)

        assertCountEqual(self, fences, geofence_policy.fences)
        self.assertEqual(fences, geofence_policy.fences)

    def test_old_fence_raises_exception(self):
        fences = [GeoFence(200, 100, 200, "OldFence")]

        with assertRaisesRegex(self, InvalidFenceType, "Invalid Fence object. Fence must be one of the following"):
            ConditionalGeoFencePolicy(
                self.DEFAULT_INSIDE_POLICY, self.DEFAULT_OUTSIDE_POLICY, deny_rooted_jailbroken=False,
                deny_emulator_simulator=True, fences=fences
            )

    def test_time_fence_throws_exception(self):
        from datetime import time
        fences = [TimeFence("TimeFence", time(hour=9), time(hour=17), monday=True)]
        with assertRaisesRegex(self, InvalidFenceType, "Invalid Fence object. Fence must be one of the following"):
            ConditionalGeoFencePolicy(
                self.DEFAULT_INSIDE_POLICY, self.DEFAULT_OUTSIDE_POLICY, fences=fences
            )

    def test_nested_conditional_geofence_raises_exception(self):
        conditional_policy = ConditionalGeoFencePolicy(self.DEFAULT_INSIDE_POLICY, self.DEFAULT_OUTSIDE_POLICY,
                                                       deny_rooted_jailbroken=False, deny_emulator_simulator=False)

        # Test Inside Policy
        with assertRaisesRegex(self, InvalidPolicyAttributes, "Inside and Outside policies must be one of the "
                                                             "following:"):
            ConditionalGeoFencePolicy(conditional_policy, self.DEFAULT_OUTSIDE_POLICY,
                                      deny_rooted_jailbroken=False, deny_emulator_simulator=True)

        # Test Outside Policy
        with assertRaisesRegex(self, InvalidPolicyAttributes, "Inside and Outside policies must be one of the "
                                                             "following:"):
            ConditionalGeoFencePolicy(self.DEFAULT_INSIDE_POLICY, conditional_policy,
                                      deny_rooted_jailbroken=False, deny_emulator_simulator=True)

    def test_to_dict_is_serializable(self):
        fences = [GeoCircleFence(100, 200, 300)]
        geofence_policy = ConditionalGeoFencePolicy(
            self.DEFAULT_INSIDE_POLICY, self.DEFAULT_OUTSIDE_POLICY, deny_rooted_jailbroken=False,
            deny_emulator_simulator=True, fences=fences
        )

        self.assertIsInstance(geofence_policy.to_dict(), dict)

    def test_deny_rooted_jailbroken_cannot_be_set_on_inner_policy(self):
        inside = FactorsPolicy(deny_rooted_jailbroken=True, deny_emulator_simulator=False, knowledge_required=True)
        outside = FactorsPolicy(deny_rooted_jailbroken=False, deny_emulator_simulator=False, possession_required=True)
        # TEST INSIDE
        with assertRaisesRegex(self, InvalidPolicyAttributes, "Setting deny_rooted_jailbroken is not allowed"):
            ConditionalGeoFencePolicy(inside, outside, deny_rooted_jailbroken=False, deny_emulator_simulator=True)
        # TEST OUTSIDE
        outside = FactorsPolicy(deny_rooted_jailbroken=True, deny_emulator_simulator=False, knowledge_required=True)
        with assertRaisesRegex(self, InvalidPolicyAttributes, "Setting deny_rooted_jailbroken is not allowed"):
            ConditionalGeoFencePolicy(inside, outside, deny_rooted_jailbroken=False, deny_emulator_simulator=True)

    def test_deny_emulator_simulator_cannot_be_set_on_inner_policy(self):
        inside = FactorsPolicy(deny_rooted_jailbroken=False, deny_emulator_simulator=True, knowledge_required=True)
        outside = FactorsPolicy(deny_rooted_jailbroken=False, deny_emulator_simulator=False, possession_required=True)
        # TEST INSIDE
        with assertRaisesRegex(self, InvalidPolicyAttributes, "Setting deny_emulator_simulator is not allowed"):
            ConditionalGeoFencePolicy(inside, outside, deny_rooted_jailbroken=False, deny_emulator_simulator=True)
        # TEST OUTSIDE
        outside = FactorsPolicy(deny_rooted_jailbroken=False, deny_emulator_simulator=True, knowledge_required=True)
        with assertRaisesRegex(self, InvalidPolicyAttributes, "Setting deny_emulator_simulator is not allowed"):
            ConditionalGeoFencePolicy(inside, outside, deny_rooted_jailbroken=False, deny_emulator_simulator=True)

    def test_inside_policy_fences_throws_exception(self):
        fences = [GeoCircleFence(100,200,300,"TestGeoCircleFence")]
        inside = FactorsPolicy(
            deny_rooted_jailbroken=False, deny_emulator_simulator=False,  knowledge_required=True, fences=fences
        )
        with assertRaisesRegex(self, InvalidPolicyAttributes,
                                    "Fences are not allowed on Inside or Outside Policy objects"):
            ConditionalGeoFencePolicy(inside=inside, outside=self.DEFAULT_OUTSIDE_POLICY)

    def test_repr(self):
        fences = [GeoCircleFence(200, 320, 350)]
        conditional_geo_fence = ConditionalGeoFencePolicy(self.DEFAULT_INSIDE_POLICY, self.DEFAULT_OUTSIDE_POLICY,
                                                          fences=fences)
        expected = "ConditionalGeoFencePolicy <inside=FactorsPolicy " \
                   "<deny_rooted_jailbroken=None, deny_emulator_simulator=None, " \
                   "inherence_required=False, knowledge_required=True, possession_required=False, fences=[]>, " \
                   "outside=FactorsPolicy <deny_rooted_jailbroken=None, " \
                   "deny_emulator_simulator=None, inherence_required=False, knowledge_required=False, " \
                   "possession_required=True, fences=[]>, deny_rooted_jailbroken=False, " \
                   "deny_emulator_simulator=False, fences=[GeoCircleFence " \
                   "<latitude=200.0, longitude=320.0, radius=350.0, name=\"None\">]>"
        self.assertEqual(repr(conditional_geo_fence), expected)


class TestMethodAmountPolicy(unittest.TestCase):
    def test_default_instantiation(self):
        method_policy = MethodAmountPolicy()

        self.assertEqual(0, method_policy.amount)
        self.assertEqual(False, method_policy.deny_rooted_jailbroken)
        self.assertEqual(False, method_policy.deny_emulator_simulator)
        self.assertEqual(list(), method_policy.fences)
        self.assertIsInstance(method_policy, MethodAmountPolicy)

    def test_setting_deny_rooted_jailbroken(self):
        method_policy = MethodAmountPolicy(deny_rooted_jailbroken=True)
        self.assertEqual(True, method_policy.deny_rooted_jailbroken)

    def test_setting_deny_emulator_simulator(self):
        method_policy = MethodAmountPolicy(deny_emulator_simulator=True)
        self.assertEqual(True, method_policy.deny_emulator_simulator)

    def test_setting_fences(self):
        fences = [GeoCircleFence(234, 567, 2323, "TestFence")]
        method_policy = MethodAmountPolicy(fences=fences)
        self.assertEqual(fences, method_policy.fences)

    def test_setting_old_fence_raises_invalid_fence_type(self):
        fences = [GeoFence(200, 100, 200, "OldFence")]
        with self.assertRaises(InvalidFenceType):
            MethodAmountPolicy(fences=fences)

    def test_to_dict_is_serializable(self):
        fences = [TerritoryFence("US", "US-CA", 90245)]
        method_policy = MethodAmountPolicy(deny_rooted_jailbroken=False, deny_emulator_simulator=True, amount=2,
                                           fences=fences)
        self.assertIsInstance(method_policy.to_dict(), dict)

    def test_repr(self):
        fences = [TerritoryFence("US", "US-CA", 90245)]
        method_policy = MethodAmountPolicy(deny_rooted_jailbroken=False, deny_emulator_simulator=True, amount=2,
                                           fences=fences)
        expected = "MethodAmountPolicy <amount=2, " \
                   "deny_rooted_jailbroken=False, " \
                   "deny_emulator_simulator=True, " \
                   "fences=[TerritoryFence <country=\"US\", " \
                   "administrative_area=\"US-CA\", postal_code=\"90245\", " \
                   "name=\"None\">]>"
        self.assertEqual(repr(method_policy), expected)


class TestFactorsPolicy(unittest.TestCase):
    def test_default_instantiation(self):
        factor_policy = FactorsPolicy()
        self.assertEqual(0, len(factor_policy.fences))
        self.assertEqual(False, factor_policy.deny_emulator_simulator)
        self.assertEqual(False, factor_policy.deny_rooted_jailbroken)
        self.assertFalse(factor_policy.inherence_required)
        self.assertFalse(factor_policy.knowledge_required)
        self.assertFalse(factor_policy.possession_required)
        self.assertIsInstance(factor_policy, FactorsPolicy)

    def test_setting_deny_rooted_jailbroken(self):
        factor_policy = FactorsPolicy(deny_rooted_jailbroken=True)
        self.assertEqual(True, factor_policy.deny_rooted_jailbroken)

    def test_setting_deny_emulator_simulator(self):
        factor_policy = FactorsPolicy(deny_emulator_simulator=True)
        self.assertEqual(True, factor_policy.deny_emulator_simulator)

    def test_setting_factors(self):
        factor_policy = FactorsPolicy(inherence_required=True, knowledge_required=True,
                                      possession_required=True)

        self.assertTrue(factor_policy.inherence_required)
        self.assertTrue(factor_policy.knowledge_required)
        self.assertTrue(factor_policy.possession_required)

    def test_factors_list(self):
        factors_dict = dict(FactorsPolicy(inherence_required=True, knowledge_required=True,
                                          possession_required=True))

        self.assertIn("INHERENCE", factors_dict["factors"])
        self.assertIn("KNOWLEDGE", factors_dict["factors"])
        self.assertIn("POSSESSION", factors_dict["factors"])

    def test_setting_fences(self):
        fences = [GeoCircleFence(234, 567, 2323, "TestFence")]
        factor_policy = FactorsPolicy(fences=fences)
        self.assertEqual(fences, factor_policy.fences)

    def test_setting_old_fences_raises_invalid_fence_type(self):
        fences = [GeoFence(200, 100, 200, "OldFence")]
        with self.assertRaises(InvalidFenceType):
            FactorsPolicy(fences=fences)

    def test_to_dict_is_serializable(self):
        factor_policy = FactorsPolicy(deny_rooted_jailbroken=False, deny_emulator_simulator=True,
                                      knowledge_required=True)

        self.assertIsInstance(factor_policy.to_dict(), dict)

    def test_repr(self):
        fences = [GeoCircleFence(100, 200, 300, "TestFence")]
        factor_policy = FactorsPolicy(deny_rooted_jailbroken=False, deny_emulator_simulator=True,
                                      knowledge_required=True, fences=fences)

        expected = "FactorsPolicy <" \
                   "deny_rooted_jailbroken=False, " \
                   "deny_emulator_simulator=True, " \
                   "inherence_required=False, " \
                   "knowledge_required=True, " \
                   "possession_required=False, " \
                   "fences=[GeoCircleFence <latitude=100.0, longitude=200.0, radius=300.0, name=\"TestFence\">]>"
        self.assertEqual(repr(factor_policy), expected)


class TestGeoCircleFence(unittest.TestCase):
    def test_default_instantiation(self):
        geo_circle_fence = GeoCircleFence(100, 200, 300)
        self.assertEqual(100, geo_circle_fence.latitude)
        self.assertEqual(200, geo_circle_fence.longitude)
        self.assertEqual(300, geo_circle_fence.radius)
        self.assertIsInstance(geo_circle_fence, GeoCircleFence)
        self.assertIsNone(geo_circle_fence.name)

    def test_name_can_be_set(self):
        geo_circle_fence = GeoCircleFence(100, 200, 300, "TestCircle")
        self.assertEqual("TestCircle", geo_circle_fence.name)

    def test_is_serializable(self):
        geo_circle_fence = GeoCircleFence(100, 200, 300, "TestCircle")
        json.dumps(dict(geo_circle_fence))

    def test_repr(self):
        geo_circle_fence = GeoCircleFence(100, 200, 300, "TestCircle")
        expected = "GeoCircleFence <latitude=100.0, longitude=200.0, " \
                   "radius=300.0, name=\"TestCircle\">"
        self.assertEqual(repr(geo_circle_fence), expected)

    def test_eq(self):
        geo_circle_fence = GeoCircleFence(latitude=30, longitude=30, radius=3000, name="Somewhere")
        matching_fence = GeoCircleFence(latitude=30, longitude=30, radius=3000, name="Somewhere")
        mismatching_fence = GeoCircleFence(latitude=30, longitude=30, radius=3000, name="Somewhere Else")
        different_kind_of_fence = TerritoryFence(country="US", name="America", administrative_area=None, postal_code=None)
        self.assertEqual(geo_circle_fence, matching_fence)
        self.assertNotEqual(geo_circle_fence, mismatching_fence)
        self.assertNotEqual(geo_circle_fence, different_kind_of_fence)


class TestTerritoryFence(unittest.TestCase):
    def test_default_instantiation(self):
        territory_fence = TerritoryFence("US", "US-CA", 90145)
        self.assertEqual("US", territory_fence.country)
        self.assertEqual("US-CA", territory_fence.administrative_area)
        self.assertEqual("90145", territory_fence.postal_code)
        self.assertIsInstance(territory_fence, TerritoryFence)
        self.assertIsNone(territory_fence.name)

    def test_name_can_be_set(self):
        territory_fence = TerritoryFence("US", "US-CA", 90145, "TestTerritory")
        self.assertEqual("TestTerritory", territory_fence.name)

    def test_is_serializable(self):
        territory_fence = TerritoryFence("US", "US-CA", 90145, "TestTerritory")
        json.dumps(dict(territory_fence))

    def test_repr(self):
        territory_fence = TerritoryFence("US", "US-CA", 90145, "TestTerritory")
        expected = "TerritoryFence <country=\"US\", administrative_area=" \
                   "\"US-CA\", postal_code=\"90145\", name=\"TestTerritory\">"
        self.assertEqual(repr(territory_fence), expected)

    def test_postal_code_integer_is_converted_to_string(self):
        expected = "90145"
        territory_fence = TerritoryFence("US", "US-CA", 90145, "TestTerritory")
        fence_dict = dict(territory_fence)
        self.assertEqual(territory_fence.postal_code, expected)
        self.assertEqual(fence_dict["postal_code"], expected)

    def test_postal_code_of_none_is_not_converted_to_string(self):
        territory_fence = TerritoryFence("US", "US-CA", None, "TestTerritory")
        fence_dict = dict(territory_fence)
        self.assertIsNone(territory_fence.postal_code)
        self.assertIsNone(fence_dict["postal_code"])

    def test_eq(self):
        territory_fence = TerritoryFence(country="US", name="America")
        matching_fence = TerritoryFence(country="US", name="America", administrative_area=None, postal_code=None)
        mismatching_fence = TerritoryFence(country="CA", name="Canada")
        different_kind_of_fence = GeoCircleFence(latitude=30, longitude=30, radius=3000, name="Somewhere")
        self.assertEqual(territory_fence, matching_fence)
        self.assertNotEqual(territory_fence, mismatching_fence)
        self.assertNotEqual(territory_fence, different_kind_of_fence)

class TestLegacyPolicy(unittest.TestCase):
    def setUp(self):
        self.legacy_policy = LegacyPolicy(amount=0, inherence_required=False, knowledge_required=True,
                                          possession_required=False, deny_rooted_jailbroken=True,
                                          fences=[], time_restrictions=[])

    def test_default_instantiation(self):
        self.assertIsInstance(self.legacy_policy, LegacyPolicy)
        self.assertEqual(self.legacy_policy.amount, 0)
        self.assertFalse(self.legacy_policy.inherence_required)
        self.assertFalse(self.legacy_policy.possession_required)
        self.assertTrue(self.legacy_policy.knowledge_required)
        self.assertTrue(self.legacy_policy.deny_rooted_jailbroken)
        self.assertEqual(self.legacy_policy.fences, [])
        self.assertEqual(self.legacy_policy.time_restrictions, [])

    def test_is_serializable(self):
        json.dumps(dict(self.legacy_policy))
        json.dumps(self.legacy_policy.to_dict())

    def test_repr(self):
        expected = "LegacyPolicy <" \
            "amount=0, " \
            "inherence_required=False, " \
            "knowledge_required=True, " \
            "possession_required=False, " \
            "deny_rooted_jailbroken=True, " \
            "fences=[], " \
            "time_restrictions=[]>"

        self.assertEqual(repr(self.legacy_policy), expected)

@ddt
class TestAuthorizationResponsePolicy(unittest.TestCase):
    def setUp(self):
        self.auth_res_policy = AuthorizationResponsePolicy(
            requirement=Requirement.COND_GEO, amount=1, fences=[],
            inherence_required=False, knowledge_required=False,
            possession_required=False)

    def test_default_instantiation(self):
        self.assertIsInstance(self.auth_res_policy, AuthorizationResponsePolicy)
        self.assertEqual(self.auth_res_policy.requirement, Requirement.COND_GEO)
        self.assertEqual(self.auth_res_policy.amount, 1)
        self.assertEqual(self.auth_res_policy.fences, [])
        self.assertFalse(self.auth_res_policy.inherence_required)
        self.assertFalse(self.auth_res_policy.knowledge_required)
        self.assertFalse(self.auth_res_policy.possession_required)

    @data("OTHER", "COND_GEO", 1, [Requirement.COND_GEO])
    def test_raises_when_requirement_is_not_valid_enum(self, req_value):
        with self.assertRaises(InvalidPolicyAttributes):
            AuthorizationResponsePolicy(requirement=req_value, amount=1,
                                        fences=[], inherence_required=False,
                                        knowledge_required=False,
                                        possession_required=False)

    def test_null_requirement_becomes_other(self):
        auth_res_policy = AuthorizationResponsePolicy(
            requirement=None, amount=1, fences=[],
            inherence_required=False, knowledge_required=False,
            possession_required=False)

        self.assertEqual(auth_res_policy.requirement, Requirement.OTHER)

    def test_is_serializable(self):
        json.dumps(dict(self.auth_res_policy))
        json.dumps(self.auth_res_policy.to_dict())

    def test_repr(self):
        expected = "AuthorizationResponsePolicy <" \
               "requirement=<Requirement.COND_GEO: 'COND_GEO'>, " \
               "fences=[], " \
               "amount=1, " \
               "inherence_required=False, " \
               "knowledge_required=False, " \
               "possession_required=False>"

        self.assertEqual(repr(self.auth_res_policy), expected)
