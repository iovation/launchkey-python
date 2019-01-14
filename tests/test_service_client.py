import json
import unittest

from jwkest import JWKESTException
from mock import MagicMock, ANY, patch
from uuid import uuid4
from json import dumps
from formencode import Invalid

from launchkey.entities.service import AuthorizationRequest, DenialReason
from launchkey.transports import JOSETransport
from launchkey.transports.base import APIResponse
from launchkey.clients import ServiceClient
from launchkey.clients.service import AuthorizationResponse, SessionEndRequest, AuthPolicy
from launchkey.exceptions import LaunchKeyAPIException, InvalidParameters, \
    InvalidPolicyInput, PolicyFailure, \
    EntityNotFound, RateLimited, RequestTimedOut, UnexpectedAPIResponse, \
    UnexpectedDeviceResponse, UnexpectedKeyID, \
    InvalidGeoFenceName, InvalidPolicyFormat, InvalidJWTResponse, \
    UnexpectedWebhookRequest, \
    UnableToDecryptWebhookRequest, UnexpectedAuthorizationResponse, \
    WebhookAuthorizationError
from datetime import datetime
from ddt import ddt, data, unpack


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

    def test_get_authorization_response_timeout(self):
        self._transport.get.side_effect = LaunchKeyAPIException({}, 408)
        with self.assertRaises(RequestTimedOut):
            self._service_client.get_authorization_response(ANY)

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


class TestHandleWebhook(unittest.TestCase):

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

    def test_handle_webhook_auth_response_requests_handles_unexpected_key(self,):
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


@ddt
class TestPolicyObject(unittest.TestCase):

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

    def test_add_geofence_invalid_input(self):
        policy = AuthPolicy()
        with self.assertRaises(InvalidParameters):
            policy.add_geofence(ANY, ANY, ANY)

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
        self.assertFalse(policy == policy2)

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
