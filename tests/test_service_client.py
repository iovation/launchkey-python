import unittest
from mock import MagicMock, ANY, patch
from uuid import uuid4
from json import dumps
from formencode import Invalid
from launchkey.transports.base import APIResponse
from launchkey.clients import ServiceClient
from launchkey.clients.service import AuthorizationResponse, SessionEndRequest, AuthPolicy
from launchkey.exceptions import LaunchKeyAPIException, InvalidParameters, InvalidPolicyInput, PolicyFailure, \
    EntityNotFound, RateLimited, RequestTimedOut, UnexpectedAPIResponse, UnexpectedDeviceResponse, UnexpectedKeyID
from datetime import datetime


class TestServiceClient(unittest.TestCase):

    def setUp(self):
        self._transport = MagicMock()
        self._response = APIResponse({}, {}, 200)
        self._transport.post.return_value = self._response
        self._transport.get.return_value = self._response
        self._transport.put.return_value = self._response
        self._transport.delete.return_value = self._response
        self._device_response = {"auth_request": str(uuid4()), "response": True, "device_id": str(uuid4()),
                                 "service_pins": "1234,3456,5678"}
        self._transport.loaded_issuer_private_key.decrypt.return_value = dumps(self._device_response)
        self._service_client = ServiceClient(uuid4(), self._transport)
        self._service_client._transport._verify_jwt_response = MagicMock()

    def test_authorize_success(self):
        self._response.data = {"auth_request": ANY}
        self._service_client.authorize(ANY, ANY, MagicMock(spec=AuthPolicy))

    def test_authorize_invalid_policy_input(self):
        self._response.data = {"auth_request": ANY}
        with self.assertRaises(InvalidParameters):
            self._service_client.authorize(ANY, ANY, ANY)

    def test_authorize_unexpected_result(self):
        self._response.data = {MagicMock(spec=str): ANY}
        with self.assertRaises(UnexpectedAPIResponse):
            self._service_client.authorize(ANY)

    def test_authorize_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._service_client.authorize(ANY)

    def test_authorize_invalid_policy(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "SVC-002", "error_detail": ""}, 400)
        with self.assertRaises(InvalidPolicyInput):
            self._service_client.authorize(ANY)

    def test_authorize_policy_failure(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "SVC-003", "error_detail": ""}, 400)
        with self.assertRaises(PolicyFailure):
            self._service_client.authorize(ANY)

    def test_authorize_entity_not_found(self):
        self._transport.post.side_effect = LaunchKeyAPIException({}, 404)
        with self.assertRaises(EntityNotFound):
            self._service_client.authorize(ANY)

    def test_authorize_rate_limited(self):
        self._transport.post.side_effect = LaunchKeyAPIException({}, 429)
        with self.assertRaises(RateLimited):
            self._service_client.authorize(ANY)

    @patch("launchkey.clients.service.b64decode")
    @patch("launchkey.clients.service.loads")
    @patch("launchkey.clients.service.AuthorizationResponsePackageValidator")
    def test_get_authorization_response_success(self, b64decode_patch, json_loads_patch,
                                                auth_response_package_validator_patch):
        b64decode_patch.return_value = MagicMock(spec=str)
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
        self.assertIsInstance(self._service_client.get_authorization_response(ANY), AuthorizationResponse)

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
        self.assertIsNone(self._service_client.session_start(ANY, ANY))

    def test_session_start_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._service_client.session_start(ANY, ANY)

    def test_session_start_entity_not_found(self):
        self._transport.post.side_effect = LaunchKeyAPIException({}, 404)
        with self.assertRaises(EntityNotFound):
            self._service_client.session_start(ANY, ANY)

    def test_session_end_success(self):
        self.assertIsNone(self._service_client.session_end(ANY))

    def test_session_end_invalid_params(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._service_client.session_end(ANY)

    def test_session_end_entity_not_found(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({}, 404)
        with self.assertRaises(EntityNotFound):
            self._service_client.session_end(ANY)

    def test_webhook_session_end(self):
        request = dumps({"service_user_hash": str(uuid4()),
                         "api_time": str(datetime.utcnow())[:19].replace(" ", "T") + "Z"})
        self.assertIsInstance(self._service_client.handle_webhook(request, ANY), SessionEndRequest)

    def test_webhook_session_end_invalid_input(self):
        request = dumps({"service_user_hash": str(uuid4())})
        with self.assertRaises(UnexpectedAPIResponse):
            self.assertIsInstance(self._service_client.handle_webhook(request, ANY), SessionEndRequest)

    @patch("launchkey.clients.service.b64decode")
    @patch("launchkey.clients.service.loads")
    @patch("launchkey.clients.service.AuthorizeSSEValidator")
    @patch("launchkey.clients.service.AuthorizationResponsePackageValidator")
    def test_webhook_authorization_response(self, auth_response_package_validator_patch,
                                            auth_sse_validator_patch, json_loads_patch, b64decode_patch):
        b64decode_patch.return_value = MagicMock(spec=str)
        json_loads_patch.return_value = MagicMock(spec=dict)
        auth_sse_validator_patch.return_value = MagicMock(spec=dict)
        auth_response_package_validator_patch.return_value = MagicMock(spec=dict)
        self._transport.loaded_issuer_private_keys = {json_loads_patch().get(): MagicMock()}
        self.assertIsInstance(self._service_client.handle_webhook(MagicMock(), ANY), AuthorizationResponse)


class TestAuthorizationResponse(unittest.TestCase):

    def setUp(self):
        self.data = MagicMock()
        key_id = MagicMock()
        self.loaded_issuer_private_keys = {key_id: MagicMock()}
        self.data.get.return_value = key_id

    @patch("launchkey.clients.service.b64decode")
    @patch("launchkey.clients.service.loads")
    @patch("launchkey.clients.service.AuthorizationResponsePackageValidator")
    def test_authorization_response_success(self, b64decode_patch, json_loads_patch,
                                            auth_response_package_validator_patch):
        b64decode_patch.return_value = MagicMock(spec=str)
        json_loads_patch.return_value = MagicMock(spec=dict)
        auth_response_package_validator_patch.return_value = MagicMock(spec=dict)
        decrypted = b64decode_patch.to_python()
        response = AuthorizationResponse(self.data, self.loaded_issuer_private_keys)
        self.assertEqual(response.authorization_request_id, decrypted.get('auth_request'))
        self.assertEqual(response.authorized, decrypted.get('response'))
        self.assertEqual(response.device_id, decrypted.get('device_id'))
        self.assertEqual(response.service_pins, decrypted.get('service_pins').split())
        self.assertEqual(response.service_user_hash, self.data.get('service_user_hash'))
        self.assertEqual(response.organization_user_hash, self.data.get('org_user_hash'))
        self.assertEqual(response.user_push_id, self.data.get('user_push_id'))

    @patch("launchkey.clients.service.b64decode")
    def test_decrypt_auth_package_base64_exception(self, b64decode_patch):
        b64decode_patch.side_effect = TypeError()
        with self.assertRaises(UnexpectedDeviceResponse):
            AuthorizationResponse(self.data, self.loaded_issuer_private_keys)

    @patch("launchkey.clients.service.b64decode")
    @patch("launchkey.clients.service.loads")
    def test_decrypt_auth_package_json_loads_exception(self, b64decode_patch, json_loads_patch):
        b64decode_patch.return_value = MagicMock(spec=str)
        json_loads_patch.side_effect = TypeError()
        with self.assertRaises(UnexpectedDeviceResponse):
            AuthorizationResponse(self.data, self.loaded_issuer_private_keys)

    @patch("launchkey.clients.service.b64decode")
    @patch("launchkey.clients.service.loads")
    @patch("launchkey.clients.service.AuthorizationResponsePackageValidator")
    def test_decrypt_auth_package_validator_exception(self, b64decode_patch, json_loads_patch,
                                                      auth_response_package_validator_patch):
        b64decode_patch.return_value = MagicMock(spec=str)
        json_loads_patch.side_effect = MagicMock(spec=dict)
        auth_response_package_validator_patch.side_effect = Invalid(ANY, ANY, ANY)
        with self.assertRaises(UnexpectedDeviceResponse):
            AuthorizationResponse(self.data, self.loaded_issuer_private_keys)

    def test_decrypt_auth_unexpected_key_id(self):
        with self.assertRaises(UnexpectedKeyID):
            AuthorizationResponse(self.data, {MagicMock(): MagicMock()})


class TestPolicyObject(unittest.TestCase):

    def test_integer_knowledge_factor_success(self):
        AuthPolicy(knowledge=1)

    def test_integer_inherence_factor_success(self):
        AuthPolicy(inherence=1)

    def test_integer_possession_factor_success(self):
        AuthPolicy(possession=1)

    def test_boolean_knowledge_factor_success(self):
        AuthPolicy(knowledge=True)

    def test_boolean_inherence_factor_success(self):
        AuthPolicy(inherence=True)

    def test_boolean_possession_factor_success(self):
        AuthPolicy(possession=True)

    def test_integer_knowledge_factor_failure(self):
        with self.assertRaises(InvalidParameters):
            AuthPolicy(knowledge=2)

    def test_integer_inherence_factor_failure(self):
        with self.assertRaises(InvalidParameters):
            AuthPolicy(inherence=2)

    def test_integer_possession_factor_failure(self):
        with self.assertRaises(InvalidParameters):
            AuthPolicy(possession=2)

    def test_mixing_factor_requirements_exception(self):
        with self.assertRaises(InvalidParameters):
            AuthPolicy(any=MagicMock(spec=int), knowledge=MagicMock(spec=int), inherence=MagicMock(spec=int),
                       possession=MagicMock(spec=int))

    def test_empty_policy_creation(self):
        policy = AuthPolicy()
        self.assertNotIn('minimum_requirements', policy.get_policy())

    def test_setting_any_requirement(self):
        value = MagicMock(spec=int)
        policy = AuthPolicy(any=value)
        self.assertEqual(policy.get_policy()['minimum_requirements'][0]['any'], int(value))

    def test_setting_specific_requirement(self):
        knowledge = MagicMock(spec=int)
        inherence = MagicMock(spec=int)
        possession = MagicMock(spec=int)
        policy = AuthPolicy(knowledge=knowledge, inherence=inherence, possession=possession)
        self.assertEqual(policy.get_policy()['minimum_requirements'][0]['knowledge'], int(knowledge))
        self.assertEqual(policy.get_policy()['minimum_requirements'][0]['inherence'], int(inherence))
        self.assertEqual(policy.get_policy()['minimum_requirements'][0]['possession'], int(possession))

    def test_jailbreak_protection_default(self):
        policy = AuthPolicy()
        self.assertEqual(len(policy.get_policy()['factors']), 0)

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
        self.assertEqual(len(retrieved['factors']), 1)
        factor = retrieved['factors'][0]
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
        self.assertEqual(len(retrieved['factors']), 1)
        factor = retrieved['factors'][0]
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

    def test_invalid_policy(self):
        policy = AuthPolicy()
        policy._policy['factors'].append(uuid4())
        with self.assertRaises(InvalidParameters):
            policy.get_policy()
