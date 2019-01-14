import unittest

from mock import MagicMock, ANY, patch
from ddt import data, unpack, ddt
from formencode import Invalid

from launchkey.entities.service import AuthorizationResponse, \
    AuthResponseType, AuthResponseReason
from launchkey.exceptions import UnexpectedDeviceResponse, UnexpectedKeyID
from launchkey.transports.jose_auth import JOSETransport


@ddt
class TestAuthorizationResponse(unittest.TestCase):

    def setUp(self):
        self.data = {
            "auth": "auth data",
            "auth_jwe": "auth jwe data",
            "service_user_hash": "vf8fg663aauTkVUFCiR0Er6kctIN9d6958hkzznVHF9",
            "user_push_id": "399e1d6c-f651-5b82-9dff-d5d63f16c849",
            "org_user_hash": "SlwSGZz0M9kPtZUL6mzAGjdYcmdUS1jHccRKOJ9rTMO",
            "public_key_id": "56:66:9d:72:f8:c3:e0:0b:3d:52:f4:81:36:f1:cc:74"
        }
        self.transport = MagicMock(spec=JOSETransport)
        self.json_loads_patch = patch('launchkey.entities.service.loads').start()

        self.json_loads_patch.return_value = {
            "auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008",
            "type": "AUTHORIZED",
            "reason": "APPROVED",
            "denial_reason": "32",
            "service_pins": ["1", "2", "3"],
            "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008"
        }

        self.addCleanup(patch.stopall)

    def test_authorization_response_jwe_response_data(self):
        self.data = {
            "auth": "auth data",
            "auth_jwe": "auth jwe data",
            "service_user_hash": "Service User Hash",
            "user_push_id": "User Push ID",
            "org_user_hash": "Org User Hash",
            "public_key_id": "56:66:9d:72:f8:c3:e0:0b:3d:52:f4:81:36:f1:cc:74"
        }

        self.json_loads_patch.return_value = {
            "auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008",
            "type": "AUTHORIZED",
            "reason": "APPROVED",
            "denial_reason": "32",
            "service_pins": ["1", "2", "3"],
            "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008"
        }

        response = AuthorizationResponse(self.data, self.transport)
        self.json_loads_patch.assert_called_with(self.transport.decrypt_response.return_value)
        self.assertEqual(response.authorization_request_id, "62e09ff8-f9a9-11e8-bbe2-0242ac130008")
        self.assertEqual(response.authorized, True)
        self.assertEqual(response.device_id, "31e5b804-f9a7-11e8-97ef-0242ac130008")
        self.assertEqual(response.service_pins, ["1", "2", "3"])
        self.assertEqual(response.service_user_hash, "Service User Hash")
        self.assertEqual(response.organization_user_hash, "Org User Hash")
        self.assertEqual(response.user_push_id, "User Push ID")
        self.assertEqual(response.type.value, "AUTHORIZED")
        self.assertEqual(response.reason.value, "APPROVED")
        self.assertEqual(response.denial_reason, "32")

    def test_authorization_response_response_jwe_authorized_true(self):
        self.json_loads_patch.return_value['type'] = "AUTHORIZED"
        self.json_loads_patch.return_value['reason'] = "APPROVED"
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.authorized, True)

    @data(
        ("DENIED", "DISAPPROVED"),
        ("DENIED", "FRAUDULENT"),
        ("FAILED", "BUSY_LOCAL"),
        ("FAILED", "PERMISSION"),
        ("FAILED", "AUTHENTICATION"),
        ("FAILED", "CONFIGURATION"),
        ("FAILED", "BUSY_LOCAL"),
        ("OTHER", "OTHER"),
        ("TESTING", "TESTING")
    )
    @unpack
    def test_authorization_response_response_jwe_authorized_false(self,
                                                                  resp_type,
                                                                  resp_reason):
        self.json_loads_patch.return_value['type'] = resp_type
        self.json_loads_patch.return_value['reason'] = resp_reason
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.authorized, False)

    @data(
        ("AUTHORIZED", "APPROVED"),
        ("DENIED", "DISAPPROVED"),
        ("DENIED", "FRAUDULENT"),
        ("FAILED", "BUSY_LOCAL"),
        ("FAILED", "PERMISSION"),
        ("FAILED", "AUTHENTICATION"),
        ("FAILED", "CONFIGURATION"),
        ("FAILED", "BUSY_LOCAL"),
        ("OTHER", "OTHER")
    )
    @unpack
    def test_authorization_response_response_jwe_response_context(self,
                                                                  resp_type,
                                                                  resp_reason):
        self.json_loads_patch.return_value['type'] = resp_type
        self.json_loads_patch.return_value['reason'] = resp_reason
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType(resp_type))
        self.assertEqual(response.reason, AuthResponseReason(resp_reason))

    @data(
        "APPROVED",
        "DISAPPROVED",
        "FRAUDULENT",
        "BUSY_LOCAL",
        "PERMISSION",
        "AUTHENTICATION",
        "CONFIGURATION",
        "BUSY_LOCAL",
        "OTHER"
    )
    def test_authorization_response_response_jwe_response_context_unknown_type(
            self,
            resp_reason):
        self.json_loads_patch.return_value['type'] = "UNKNOWN"
        self.json_loads_patch.return_value['reason'] = resp_reason
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.OTHER)
        self.assertEqual(response.reason, AuthResponseReason(resp_reason))

    @data("AUTHORIZED", "DENIED", "FAILED")
    def test_authorization_response_response_jwe_response_context_unknown_reas(
            self,
            resp_type):
        self.json_loads_patch.return_value['type'] = resp_type
        self.json_loads_patch.return_value['reason'] = "UNKNOWN"
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType(resp_type))
        self.assertEqual(response.reason, AuthResponseReason.OTHER)

    @data("AUTHORIZED", "DENIED", "FAILED")
    def test_authorization_response_response_jwe_response_context_fraud(
            self,
            resp_type):
        self.json_loads_patch.return_value['type'] = resp_type
        self.json_loads_patch.return_value['reason'] = "FRAUDULENT"
        response = AuthorizationResponse(self.data, self.transport)
        self.assertTrue(response.fraud, True)

    @data(
        "APPROVED",
        "DISAPPROVED",
        "BUSY_LOCAL",
        "PERMISSION",
        "AUTHENTICATION",
        "CONFIGURATION",
        "BUSY_LOCAL",
        "OTHER"
    )
    def test_authorization_response_response_jwe_response_context_not_fraud(
            self,
            resp_reason):
        self.json_loads_patch.return_value['type'] = "UNKNOWN"
        self.json_loads_patch.return_value['reason'] = resp_reason
        response = AuthorizationResponse(self.data, self.transport)
        self.assertFalse(response.fraud)

    @data(Invalid, TypeError, ValueError)
    def test_authorization_response_response_jwe_unexpected_device_response(
            self, exc):
        self.transport.decrypt_response.side_effect = exc
        with self.assertRaises(UnexpectedDeviceResponse):
            AuthorizationResponse(self.data, self.transport)

    def test_authorization_response_rsa_response_data(self):
        self.data = {
            "auth": "auth data",
            "service_user_hash": "Service User Hash",
            "user_push_id": "User Push ID",
            "org_user_hash": "Org User Hash",
            "public_key_id": "56:66:9d:72:f8:c3:e0:0b:3d:52:f4:81:36:f1:cc:74"
        }

        self.json_loads_patch.return_value = {
            "auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008",
            "response": True,
            "service_pins": ["1", "2", "3"],
            "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008"
        }

        response = AuthorizationResponse(self.data, self.transport)
        self.json_loads_patch.assert_called_with(
            self.transport.decrypt_rsa_response.return_value)
        self.assertEqual(response.authorization_request_id, "62e09ff8-f9a9-11e8-bbe2-0242ac130008")
        self.assertEqual(response.authorized, True)
        self.assertEqual(response.device_id, "31e5b804-f9a7-11e8-97ef-0242ac130008")
        self.assertEqual(response.service_pins, ["1", "2", "3"])
        self.assertEqual(response.service_user_hash, "Service User Hash")
        self.assertEqual(response.organization_user_hash, "Org User Hash")
        self.assertEqual(response.user_push_id, "User Push ID")
        self.assertIsNone(response.type)
        self.assertIsNone(response.reason)
        self.assertIsNone(response.denial_reason)
        self.assertIsNone(response.fraud)

    def test_authorization_response_response_rsa_authorized_true(self):
        del self.data['auth_jwe']
        self.json_loads_patch.return_value['response'] = True
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.authorized, True)

    def test_authorization_response_response_rsa_authorized_false(self):
        del self.data['auth_jwe']
        self.json_loads_patch.return_value['response'] = False
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.authorized, False)

    @data(Invalid, TypeError, ValueError)
    def test_authorization_response_response_rsa_unexpected_device_response(
            self, exc):
        del self.data['auth_jwe']
        self.transport.decrypt_rsa_response.side_effect = exc
        with self.assertRaises(UnexpectedDeviceResponse):
            AuthorizationResponse(self.data, self.transport)
