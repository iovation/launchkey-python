import unittest

import json
from mock import MagicMock, patch
from ddt import data, unpack, ddt
from formencode import Invalid
from datetime import time

from launchkey.entities.service import AuthorizationResponse, \
    AuthResponseType, AuthResponseReason, GeoFence, TimeFence, \
    AuthMethodType, AuthPolicy, AuthorizationRequest, AuthMethod, \
    AdvancedAuthorizationResponse
from launchkey.exceptions import UnexpectedDeviceResponse
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
        ("FAILED", "SENSOR"),
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
        ("FAILED", "SENSOR"),
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
        "SENSOR",
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
        "SENSOR",
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


class TestAdvancedAuthorizationResponse(unittest.TestCase):
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
        self.json_data = {
            "auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008",
            "type": "AUTHORIZED",
            "reason": "APPROVED",
            "denial_reason": "32",
            "service_pins": ["1", "2", "3"],
            "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008"
        }

        self.json_loads_patch.return_value = self.json_data
        self.addCleanup(patch.stopall)

    def test_default_instantiation(self):
        response = AdvancedAuthorizationResponse(self.data, self.transport)
        self.json_loads_patch.assert_called_with(self.transport.decrypt_response.return_value)
        self.assertEqual(response.authorization_request_id, self.json_data["auth_request"])
        self.assertEqual(response.authorized, True)
        self.assertEqual(response.device_id, self.json_data["device_id"])
        self.assertEqual(response.service_pins, self.json_data["service_pins"])
        self.assertEqual(response.service_user_hash, self.data["service_user_hash"])
        self.assertEqual(response.organization_user_hash, self.data["org_user_hash"])
        self.assertEqual(response.user_push_id, self.data["user_push_id"])
        self.assertEqual(response.type.value, self.json_data["type"])
        self.assertEqual(response.reason.value, self.json_data["reason"])
        self.assertEqual(response.denial_reason, self.json_data["denial_reason"])

    def test_instantiates_with_any_type_of_geofence(self):
        json_data = {
            "auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008",
            "type": "AUTHORIZED",
            "reason": "APPROVED",
            "denial_reason": "32",
            "service_pins": ["1", "2", "3"],
            "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008",
            "auth_policy": {
                "requirement": None,
                "geofences": [
                    {"latitude": 30, "longitude": 30, "radius": 3000, "name": "cool"},
                    {"type": "GEO_CIRCLE", "latitude": 30, "longitude": 30, "radius": 3000, "name": "awesome"},
                    {"type": "TERRITORY", "country": "US", "administrative_area": "US-NV", "name": "Nevada"},
                ]
            }
        }

        self.json_loads_patch.return_value = json_data
        AdvancedAuthorizationResponse(self.data, self.transport)

    def test_raises_when_invalid_fence_type_received(self):
        json_data = {
            "auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008",
            "type": "AUTHORIZED",
            "reason": "APPROVED",
            "denial_reason": "32",
            "service_pins": ["1", "2", "3"],
            "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008",
            "auth_policy": {
                "requirement": None,
                "geofences": [
                    {"type": "NOT_A_FENCE", "latitude": 30, "longitude": 30, "radius": 3000, "name": "awesome"},
                ]
            }
        }

        self.json_loads_patch.return_value = json_data
        with self.assertRaises(UnexpectedDeviceResponse):
            AdvancedAuthorizationResponse(self.data, self.transport)


@ddt
class TestAuthorizationResponseAuthPolicy(unittest.TestCase):

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
        self.transport.decrypt_response.return_value = "{}"

        self.json_loads_patch = patch(
            "launchkey.entities.service.loads").start()
        self.addCleanup(patch.stopall)
        self.json_loads_patch.return_value = {
            "auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008",
            "type": "AUTHORIZED",
            "reason": "APPROVED",
            "denial_reason": "32",
            "service_pins": ["1", "2", "3"],
            "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008",
            "auth_policy": {
                "requirement": None,
                "geofences": [
                    {"latitude": 36.083548, "longitude": -115.157517, "radius": 150, "name": "work"}
                ]
            },
            "auth_methods": [
                {"method": "wearables", "set": False, "active": False, "allowed": True, "supported": True, "user_required": None, "passed": None, "error": None },
                {"method": "geofencing", "set": None, "active": True, "allowed": True, "supported": True, "user_required": None, "passed": None, "error": None },
                {"method": "locations", "set": False, "active": False, "allowed": True, "supported": True, "user_required": None, "passed": None, "error": None },
                {"method": "pin_code", "set": True, "active": True, "allowed": True, "supported": True, "user_required": False, "passed": None, "error": None },
                {"method": "circle_code", "set": True, "active": True, "allowed": True, "supported": True, "user_required": False, "passed": None, "error": None },
                {"method": "face", "set": False, "active": False, "allowed": True, "supported": True, "user_required": None, "passed": None, "error": None },
                {"method": "fingerprint", "set": False, "active": False, "allowed": True, "supported": True, "user_required": None, "passed": None, "error": None }
            ]
        }

    def test_missing_auth_policy(self):
        del self.json_loads_patch.return_value['auth_policy']
        response = AuthorizationResponse(self.data, self.transport)
        self.assertIsNone(response.auth_policy)

    def test_geofence_auth_policy(self):
        self.json_loads_patch.return_value['auth_policy']['geofences'] = [
            {"latitude": 36.083548, "longitude": -115.157517, "radius": 150,
             "name": "work"},
            {"latitude": 40.55, "longitude": -90.12, "radius": 100,
             "name": "home"}
        ]
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(
            response.auth_policy.geofences,
            [
                GeoFence(latitude=36.083548, longitude=-115.157517,
                         radius=150.0, name="work"),
                GeoFence(latitude=40.55, longitude=-90.12, radius=100.0,
                         name="home")
            ]
        )

    def test_empty_geofence_auth_policy(self):
        self.json_loads_patch.return_value['auth_policy']['geofences'] = []
        response = AuthorizationResponse(self.data, self.transport)
        self.assertIsNone(response.auth_policy)

    def test_missing_geofence_auth_policy(self):
        del self.json_loads_patch.return_value['auth_policy']['geofences']
        response = AuthorizationResponse(self.data, self.transport)
        self.assertIsNone(response.auth_policy)

    def test_invalid_requirement(self):
        self.json_loads_patch.return_value['auth_policy']['requirement'] = 'invalid'
        self.json_loads_patch.return_value['auth_policy']['types'] = ['knowledge', 'inherence']
        self.json_loads_patch.return_value['auth_policy']['amount'] = 2
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            []
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            0
        )

    def test_types_requirement(self):
        self.json_loads_patch.return_value['auth_policy']['requirement'] = 'types'
        self.json_loads_patch.return_value['auth_policy']['types'] = ['knowledge', 'inherence']
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            ['knowledge', 'inherence']
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            0
        )

    def test_types_requirement_with_amount_included(self):
        self.json_loads_patch.return_value['auth_policy']['requirement'] = 'types'
        self.json_loads_patch.return_value['auth_policy']['types'] = ['inherence']
        self.json_loads_patch.return_value['auth_policy']['amount'] = 3
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            ['inherence']
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            0
        )

    @patch('launchkey.entities.service.warnings')
    def test_types_requirement_invalid_type(self, warnings_patch):
        self.json_loads_patch.return_value['auth_policy']['requirement'] = 'types'
        self.json_loads_patch.return_value['auth_policy']['types'] = ['knowledge', 'invalid']
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            ['knowledge']
        )
        warnings_patch.warn.assert_called()

    def test_amount_requirement(self):
        self.json_loads_patch.return_value['auth_policy']['requirement'] = 'amount'
        self.json_loads_patch.return_value['auth_policy']['amount'] = 3
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(
            response.auth_policy.minimum_amount,
            3
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            []
        )

    def test_amount_requirement_with_types_included(self):
        self.json_loads_patch.return_value['auth_policy']['requirement'] = 'amount'
        self.json_loads_patch.return_value['auth_policy']['amount'] = 3
        self.json_loads_patch.return_value['auth_policy']['types'] = ['knowledge', 'invalid']
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(
            response.auth_policy.minimum_amount,
            3
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            []
        )

    def test_auth_policy_repr_default(self):
        auth_policy = AuthPolicy()
        self.assertEqual(
            str(auth_policy),
            "AuthPolicy <minimum_requirements=[], minimum_amount=0, "
            "geofences=[]>"
        )

    def test_auth_policy_min_amount_repr(self):
        auth_policy = AuthPolicy(any=3)
        self.assertEqual(
            str(auth_policy),
            "AuthPolicy <minimum_requirements=[], "
            "minimum_amount=3, geofences=[]>"
        )

    def test_auth_policy_min_requirements_repr(self):
        auth_policy = AuthPolicy(knowledge=True, inherence=True, possession=True)
        self.assertEqual(
            str(auth_policy),
            "AuthPolicy <minimum_requirements="
            "['knowledge', 'inherence', 'possession'], "
            "minimum_amount=0, geofences=[]>"
        )

    def test_auth_policy_repr_geofences(self):
        auth_policy = AuthPolicy()
        auth_policy.add_geofence(1, 2, 3)
        auth_policy.add_geofence(4.1, 5.2, 6.3, name='test')
        self.assertEqual(
            str(auth_policy),
            'AuthPolicy <minimum_requirements=[], minimum_amount=0, '
            'geofences=[GeoFence <name="None", latitude=1.0, longitude=2.0, '
            'radius=3.0>, GeoFence <name="test", latitude=4.1, longitude=5.2, '
            'radius=6.3>]>'
        )


@ddt
class TestAuthorizationResponseAuthMethodInsight(unittest.TestCase):

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
        self.transport.decrypt_response.return_value = "{}"

    def test_missing_auth_methods(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "AUTHORIZED", "reason": "APPROVED", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": "types", "types": ["possession"], "geofences": [] } }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertIsNone(response.auth_methods)

    def test_unknown_auth_method(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "AUTHORIZED", "reason": "APPROVED", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": null, "geofences": [ ] }, "auth_methods": [{"method": "wearables", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": true, "error": false }, {"method": "pin_code", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": true, "error": false }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "something_new", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        unknown = response.auth_methods[7]
        self.assertEqual(unknown.method, AuthMethodType.OTHER)
        self.assertFalse(unknown.set)
        self.assertFalse(unknown.active)
        self.assertTrue(unknown.allowed)
        self.assertTrue(unknown.supported)
        self.assertIsNone(unknown.user_required)
        self.assertIsNone(unknown.passed)
        self.assertIsNone(unknown.error)

    def test_1_pin_code_and_locations_success(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "AUTHORIZED", "reason": "APPROVED", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": null, "geofences": [ ] }, "auth_methods": [{"method": "wearables", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": true, "error": false }, {"method": "pin_code", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": true, "error": false }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.AUTHORIZED)
        self.assertEqual(response.reason, AuthResponseReason.APPROVED)
        locations = response.auth_methods[2]
        self.assertEqual(locations.method, AuthMethodType.LOCATIONS)
        self.assertTrue(locations.set)
        self.assertTrue(locations.active)
        self.assertTrue(locations.allowed)
        self.assertTrue(locations.supported)
        self.assertTrue(locations.user_required)
        self.assertTrue(locations.passed)
        self.assertFalse(locations.error)
        pin_code = response.auth_methods[3]
        self.assertEqual(pin_code.method, AuthMethodType.PIN_CODE)
        self.assertTrue(pin_code.set)
        self.assertTrue(pin_code.active)
        self.assertTrue(pin_code.allowed)
        self.assertTrue(pin_code.supported)
        self.assertTrue(pin_code.user_required)
        self.assertTrue(pin_code.passed)
        self.assertFalse(pin_code.error)
        self.assertIsNone(response.auth_policy)

    def test_2_location_failure_unchecked_pincode(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "FAILED", "reason": "AUTHENTICATION", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": null, "geofences": [ ] }, "auth_methods": [{"method": "wearables", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": false, "error": false }, {"method": "pin_code", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": null, "error": null }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.FAILED)
        self.assertEqual(response.reason, AuthResponseReason.AUTHENTICATION)
        locations = response.auth_methods[2]
        self.assertEqual(locations.method, AuthMethodType.LOCATIONS)
        self.assertTrue(locations.set)
        self.assertTrue(locations.active)
        self.assertTrue(locations.allowed)
        self.assertTrue(locations.supported)
        self.assertTrue(locations.user_required)
        self.assertFalse(locations.passed)
        self.assertFalse(locations.error)
        pin_code = response.auth_methods[3]
        self.assertEqual(pin_code.method, AuthMethodType.PIN_CODE)
        self.assertTrue(pin_code.set)
        self.assertTrue(pin_code.active)
        self.assertTrue(pin_code.allowed)
        self.assertTrue(pin_code.supported)
        self.assertTrue(pin_code.user_required)
        self.assertIsNone(pin_code.passed)
        self.assertIsNone(pin_code.error)
        self.assertIsNone(response.auth_policy)

    def test_3_possession_failure_unchecked_circle_code(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "FAILED", "reason": "POLICY", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": "types", "types": ["possession"], "geofences": [ ] }, "auth_methods": [{"method": "wearables", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "pin_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "circle_code", "set": true, "active": true, "allowed": true, "supported": true, "user_required": false, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.FAILED)
        self.assertEqual(response.reason, AuthResponseReason.POLICY)
        circle_code = response.auth_methods[4]
        self.assertEqual(circle_code.method, AuthMethodType.CIRCLE_CODE)
        self.assertTrue(circle_code.set)
        self.assertTrue(circle_code.active)
        self.assertTrue(circle_code.allowed)
        self.assertTrue(circle_code.supported)
        self.assertFalse(circle_code.user_required)
        self.assertIsNone(circle_code.passed)
        self.assertIsNone(circle_code.error)
        self.assertEqual(
            response.auth_policy.geofences,
            []
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            0
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            ['possession']
        )

    def test_4_amount_failure_unchecked_fingerprint(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "FAILED", "reason": "POLICY", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": "amount", "amount": 2, "geofences": [ ] }, "auth_methods": [{"method": "wearables", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "pin_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.FAILED)
        self.assertEqual(response.reason, AuthResponseReason.POLICY)
        fingerprint = response.auth_methods[6]
        self.assertEqual(fingerprint.method, AuthMethodType.FINGERPRINT)
        self.assertTrue(fingerprint.set)
        self.assertTrue(fingerprint.active)
        self.assertTrue(fingerprint.allowed)
        self.assertTrue(fingerprint.supported)
        self.assertTrue(fingerprint.user_required)
        self.assertIsNone(fingerprint.passed)
        self.assertIsNone(fingerprint.error)
        self.assertEqual(
            response.auth_policy.geofences,
            []
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            2
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            []
        )

    def test_5_amount_success_failed_wearable_sensor_unchecked_fingerprint(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "FAILED", "reason": "SENSOR", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": "amount", "amount": 2, "geofences": [ ] }, "auth_methods": [{"method": "wearables", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": null, "error": true }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "pin_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.FAILED)
        self.assertEqual(response.reason, AuthResponseReason.SENSOR)
        wearable = response.auth_methods[0]
        self.assertEqual(wearable.method, AuthMethodType.WEARABLES)
        self.assertTrue(wearable.set)
        self.assertTrue(wearable.active)
        self.assertTrue(wearable.allowed)
        self.assertTrue(wearable.supported)
        self.assertTrue(wearable.user_required)
        self.assertIsNone(wearable.passed)
        self.assertTrue(wearable.error)
        fingerprint = response.auth_methods[6]
        self.assertEqual(fingerprint.method, AuthMethodType.FINGERPRINT)
        self.assertTrue(fingerprint.set)
        self.assertTrue(fingerprint.active)
        self.assertTrue(fingerprint.allowed)
        self.assertTrue(fingerprint.supported)
        self.assertTrue(fingerprint.user_required)
        self.assertIsNone(fingerprint.passed)
        self.assertIsNone(fingerprint.error)
        self.assertEqual(
            response.auth_policy.geofences,
            []
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            2
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            []
        )

    def test_6_required_amount_2_failed_wearable_unchecked_location_unchecked_fingerprint(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "FAILED", "reason": "AUTHENTICATION", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": "amount", "amount": 2, "geofences": [ ] }, "auth_methods": [{"method": "wearables", "set": true, "active": true, "allowed": true, "supported": true, "user_required": false, "passed": false, "error": false }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": true, "active": true, "allowed": true, "supported": true, "user_required": false, "passed": null, "error": null }, {"method": "pin_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.FAILED)
        self.assertEqual(response.reason, AuthResponseReason.AUTHENTICATION)
        wearable = response.auth_methods[0]
        self.assertEqual(wearable.method, AuthMethodType.WEARABLES)
        self.assertTrue(wearable.set)
        self.assertTrue(wearable.active)
        self.assertTrue(wearable.allowed)
        self.assertTrue(wearable.supported)
        self.assertFalse(wearable.user_required)
        self.assertFalse(wearable.passed)
        self.assertFalse(wearable.error)
        locations = response.auth_methods[2]
        self.assertEqual(locations.method, AuthMethodType.LOCATIONS)
        self.assertTrue(locations.set)
        self.assertTrue(locations.active)
        self.assertTrue(locations.allowed)
        self.assertTrue(locations.supported)
        self.assertFalse(locations.user_required)
        self.assertIsNone(locations.passed)
        self.assertIsNone(locations.error)
        fingerprint = response.auth_methods[6]
        self.assertEqual(fingerprint.method, AuthMethodType.FINGERPRINT)
        self.assertTrue(fingerprint.set)
        self.assertTrue(fingerprint.active)
        self.assertTrue(fingerprint.allowed)
        self.assertTrue(fingerprint.supported)
        self.assertTrue(fingerprint.user_required)
        self.assertIsNone(fingerprint.passed)
        self.assertIsNone(fingerprint.error)
        self.assertEqual(
            response.auth_policy.geofences,
            []
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            2
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            []
        )

    def test_7_required_amount_2_successful_fingerprint_successful_locations_unchecked_wearable(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "AUTHORIZED", "reason": "APPROVED", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": "amount", "amount": 2, "geofences": [ ] }, "auth_methods": [{"method": "wearables", "set": true, "active": true, "allowed": true, "supported": true, "user_required": false, "passed": null, "error": null }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": true, "error": false }, {"method": "pin_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": true, "error": false } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.AUTHORIZED)
        self.assertEqual(response.reason, AuthResponseReason.APPROVED)
        wearable = response.auth_methods[0]
        self.assertEqual(wearable.method, AuthMethodType.WEARABLES)
        self.assertTrue(wearable.set)
        self.assertTrue(wearable.active)
        self.assertTrue(wearable.allowed)
        self.assertTrue(wearable.supported)
        self.assertFalse(wearable.user_required)
        self.assertIsNone(wearable.passed)
        self.assertIsNone(wearable.error)
        locations = response.auth_methods[2]
        self.assertEqual(locations.method, AuthMethodType.LOCATIONS)
        self.assertTrue(locations.set)
        self.assertTrue(locations.active)
        self.assertTrue(locations.allowed)
        self.assertTrue(locations.supported)
        self.assertTrue(locations.user_required)
        self.assertTrue(locations.passed)
        self.assertFalse(locations.error)
        fingerprint = response.auth_methods[6]
        self.assertEqual(fingerprint.method, AuthMethodType.FINGERPRINT)
        self.assertTrue(fingerprint.set)
        self.assertTrue(fingerprint.active)
        self.assertTrue(fingerprint.allowed)
        self.assertTrue(fingerprint.supported)
        self.assertTrue(fingerprint.user_required)
        self.assertTrue(fingerprint.passed)
        self.assertFalse(fingerprint.error)
        self.assertEqual(
            response.auth_policy.geofences,
            []
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            2
        )

    def test_8_required_amount_3_passed_geofence_failed_amount_skipped_face_skipped_pin(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "FAILED", "reason": "POLICY", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": "amount", "amount": 3, "geofences": [{"latitude": 36.083548, "longitude": -115.157517, "radius": 150, "name": "work"} ] }, "auth_methods": [{"method": "wearables", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "pin_code", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": null, "error": null }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": null, "error": null }, {"method": "fingerprint", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.FAILED)
        self.assertEqual(response.reason, AuthResponseReason.POLICY)
        geofencing = response.auth_methods[1]
        self.assertEqual(geofencing.method, AuthMethodType.GEOFENCING)
        self.assertIsNone(geofencing.set)
        self.assertTrue(geofencing.active)
        self.assertTrue(geofencing.allowed)
        self.assertTrue(geofencing.supported)
        self.assertIsNone(geofencing.user_required)
        self.assertIsNone(geofencing.passed)
        self.assertIsNone(geofencing.error)
        pin_code = response.auth_methods[3]
        self.assertEqual(pin_code.method, AuthMethodType.PIN_CODE)
        self.assertTrue(pin_code.set)
        self.assertTrue(pin_code.active)
        self.assertTrue(pin_code.allowed)
        self.assertTrue(pin_code.supported)
        self.assertTrue(pin_code.user_required)
        self.assertIsNone(pin_code.passed)
        self.assertIsNone(pin_code.error)
        face = response.auth_methods[5]
        self.assertEqual(face.method, AuthMethodType.FACE)
        self.assertTrue(face.set)
        self.assertTrue(face.active)
        self.assertTrue(face.allowed)
        self.assertTrue(face.supported)
        self.assertTrue(face.user_required)
        self.assertIsNone(face.passed)
        self.assertIsNone(face.error)
        self.assertEqual(
            response.auth_policy.geofences,
            [
                GeoFence(latitude=36.083548, longitude=-115.157517,
                         radius=150.0, name="work")
            ]
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            3
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            []
        )

    def test_9_required_amount_2_failed_geofence_unchecked_face_unchecked_pin(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "FAILED", "reason": "AUTHENTICATION", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": "amount", "amount": 2, "geofences": [{"latitude": 36.083548, "longitude": -115.157517, "radius": 150, "name": "work"} ] }, "auth_methods": [{"method": "wearables", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": false, "error": false }, {"method": "locations", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "pin_code", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": null, "error": null }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": null, "error": null }, {"method": "fingerprint", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.FAILED)
        self.assertEqual(response.reason, AuthResponseReason.AUTHENTICATION)
        geofencing = response.auth_methods[1]
        self.assertEqual(geofencing.method, AuthMethodType.GEOFENCING)
        self.assertIsNone(geofencing.set)
        self.assertTrue(geofencing.active)
        self.assertTrue(geofencing.allowed)
        self.assertTrue(geofencing.supported)
        self.assertIsNone(geofencing.user_required)
        self.assertFalse(geofencing.passed)
        self.assertFalse(geofencing.error)
        pin_code = response.auth_methods[3]
        self.assertEqual(pin_code.method, AuthMethodType.PIN_CODE)
        self.assertTrue(pin_code.set)
        self.assertTrue(pin_code.active)
        self.assertTrue(pin_code.allowed)
        self.assertTrue(pin_code.supported)
        self.assertTrue(pin_code.user_required)
        self.assertIsNone(pin_code.passed)
        self.assertIsNone(pin_code.error)
        face = response.auth_methods[5]
        self.assertEqual(face.method, AuthMethodType.FACE)
        self.assertTrue(face.set)
        self.assertTrue(face.active)
        self.assertTrue(face.allowed)
        self.assertTrue(face.supported)
        self.assertTrue(face.user_required)
        self.assertIsNone(face.passed)
        self.assertIsNone(face.error)
        self.assertEqual(
            response.auth_policy.geofences,
            [
                GeoFence(latitude=36.083548, longitude=-115.157517,
                         radius=150.0, name="work")
            ]
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            2
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            []
        )

    def test_10_location_failure_unchecked_fingerprint_passed_geofence(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "FAILED", "reason": "AUTHENTICATION", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": null, "geofences": [{"latitude": 36.083548, "longitude": -115.157517, "radius": 150, "name": "work"} ] }, "auth_methods": [{"method": "wearables", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": true, "error": false }, {"method": "locations", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": false, "error": false }, {"method": "pin_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": true, "active": true, "allowed": true, "supported": true, "user_required": true, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.FAILED)
        self.assertEqual(response.reason, AuthResponseReason.AUTHENTICATION)
        geofencing = response.auth_methods[1]
        self.assertEqual(geofencing.method, AuthMethodType.GEOFENCING)
        self.assertIsNone(geofencing.set)
        self.assertTrue(geofencing.active)
        self.assertTrue(geofencing.allowed)
        self.assertTrue(geofencing.supported)
        self.assertIsNone(geofencing.user_required)
        self.assertTrue(geofencing.passed)
        self.assertFalse(geofencing.error)
        locations = response.auth_methods[2]
        self.assertEqual(locations.method, AuthMethodType.LOCATIONS)
        self.assertTrue(locations.set)
        self.assertTrue(locations.active)
        self.assertTrue(locations.allowed)
        self.assertTrue(locations.supported)
        self.assertTrue(locations.user_required)
        self.assertFalse(locations.passed)
        self.assertFalse(locations.error)
        fingerprint = response.auth_methods[6]
        self.assertEqual(fingerprint.method, AuthMethodType.FINGERPRINT)
        self.assertTrue(fingerprint.set)
        self.assertTrue(fingerprint.active)
        self.assertTrue(fingerprint.allowed)
        self.assertTrue(fingerprint.supported)
        self.assertTrue(fingerprint.user_required)
        self.assertIsNone(fingerprint.passed)
        self.assertIsNone(fingerprint.error)
        self.assertEqual(
            response.auth_policy.geofences,
            [
                GeoFence(latitude=36.083548, longitude=-115.157517,
                         radius=150.0, name="work")
            ]
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            0
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            []
        )

    def test_11_required_possession_failure_unchecked_pin_unchecked_circle_code(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "FAILED", "reason": "POLICY", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": "types", "types": ["possession"], "geofences": [] }, "auth_methods": [{"method": "wearables", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "pin_code", "set": true, "active": true, "allowed": true, "supported": true, "user_required": false, "passed": null, "error": null }, {"method": "circle_code", "set": true, "active": true, "allowed": true, "supported": true, "user_required": false, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.FAILED)
        self.assertEqual(response.reason, AuthResponseReason.POLICY)
        pin_code = response.auth_methods[3]
        self.assertEqual(pin_code.method, AuthMethodType.PIN_CODE)
        self.assertTrue(pin_code.set)
        self.assertTrue(pin_code.active)
        self.assertTrue(pin_code.allowed)
        self.assertTrue(pin_code.supported)
        self.assertFalse(pin_code.user_required)
        self.assertIsNone(pin_code.passed)
        self.assertIsNone(pin_code.error)
        circle_code = response.auth_methods[4]
        self.assertEqual(circle_code.method, AuthMethodType.CIRCLE_CODE)
        self.assertTrue(circle_code.set)
        self.assertTrue(circle_code.active)
        self.assertTrue(circle_code.allowed)
        self.assertTrue(circle_code.supported)
        self.assertFalse(circle_code.user_required)
        self.assertIsNone(circle_code.passed)
        self.assertIsNone(circle_code.error)
        self.assertEqual(
            response.auth_policy.geofences,
            []
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            0
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            ['possession']
        )

    def test_12_required_amount_1_failed_wearable_sensor_unchecked_locations(self):
        self.transport.decrypt_response.return_value = '{"auth_request": "62e09ff8-f9a9-11e8-bbe2-0242ac130008", "type": "FAILED", "reason": "SENSOR", "denial_reason": "32", "service_pins": ["1", "2", "3"], "device_id": "31e5b804-f9a7-11e8-97ef-0242ac130008", "auth_policy": {"requirement": "amount", "amount": 1, "geofences": [] }, "auth_methods": [{"method": "wearables", "set": true, "active": true, "allowed": true, "supported": true, "user_required": false, "passed": null, "error": true }, {"method": "geofencing", "set": null, "active": true, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "locations", "set": true, "active": true, "allowed": true, "supported": true, "user_required": false, "passed": null, "error": null }, {"method": "pin_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "circle_code", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "face", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null }, {"method": "fingerprint", "set": false, "active": false, "allowed": true, "supported": true, "user_required": null, "passed": null, "error": null } ] }'
        response = AuthorizationResponse(self.data, self.transport)
        self.assertEqual(response.type, AuthResponseType.FAILED)
        self.assertEqual(response.reason, AuthResponseReason.SENSOR)
        wearable = response.auth_methods[0]
        self.assertEqual(wearable.method, AuthMethodType.WEARABLES)
        self.assertTrue(wearable.set)
        self.assertTrue(wearable.active)
        self.assertTrue(wearable.allowed)
        self.assertTrue(wearable.supported)
        self.assertFalse(wearable.user_required)
        self.assertIsNone(wearable.passed)
        self.assertTrue(wearable.error)
        locations = response.auth_methods[2]
        self.assertEqual(locations.method, AuthMethodType.LOCATIONS)
        self.assertTrue(locations.set)
        self.assertTrue(locations.active)
        self.assertTrue(locations.allowed)
        self.assertTrue(locations.supported)
        self.assertFalse(locations.user_required)
        self.assertIsNone(locations.passed)
        self.assertIsNone(locations.error)
        self.assertEqual(
            response.auth_policy.geofences,
            []
        )
        self.assertEqual(
            response.auth_policy.minimum_amount,
            1
        )
        self.assertEqual(
            response.auth_policy.minimum_requirements,
            []
        )


class TestGeoFence(unittest.TestCase):
    def test_equals_same_geofence(self):
        geo_1 = GeoFence(1, 2, 3, name='name')
        geo_2 = GeoFence(1, 2, 3, name='name')
        self.assertTrue(geo_1 == geo_2)

    def test_different_lat(self):
        geo_1 = GeoFence(1, 2, 3, name='name')
        geo_2 = GeoFence(2, 2, 3, name='name')
        self.assertFalse(geo_1 == geo_2)

    def test_different_long(self):
        geo_1 = GeoFence(1, 2, 3, name='name')
        geo_2 = GeoFence(1, 3, 3, name='name')
        self.assertFalse(geo_1 == geo_2)

    def test_different_radius(self):
        geo_1 = GeoFence(1, 2, 3, name='name')
        geo_2 = GeoFence(1, 2, 4, name='name')
        self.assertFalse(geo_1 == geo_2)

    def test_different_name(self):
        geo_1 = GeoFence(1, 2, 3, name='name')
        geo_2 = GeoFence(1, 2, 3, name='name2')
        self.assertFalse(geo_1 == geo_2)

    def test_not_equal(self):
        geofence = GeoFence(1, 2, 3, name='name')
        geofence_2 = GeoFence(2, 2, 3, name='name')
        self.assertTrue(geofence != geofence_2)

    def test_different_type(self):
        geofence = GeoFence(1, 2, 3, name='name')
        timefence = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertFalse(geofence == timefence)

    def test_repr(self):
        geo_1 = GeoFence(1, 2, 3, name='My Name')
        self.assertEqual(
            str(geo_1),
            'GeoFence <name="My Name", latitude=1.0, '
            'longitude=2.0, radius=3.0>'
        )


class TestTimeFence(unittest.TestCase):
    def test_equals_same_timefence(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertTrue(fence_1 == fence_2)

    def test_different_name(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name2",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertFalse(fence_1 == fence_2)

    def test_different_start_time(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name",
            time(hour=1, minute=5),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertFalse(fence_1 == fence_2)

    def test_different_end_time(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=5),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertFalse(fence_1 == fence_2)

    def test_different_monday(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=False,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertFalse(fence_1 == fence_2)

    def test_different_tuesday(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=False,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertFalse(fence_1 == fence_2)

    def test_different_wednesday(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=False,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertFalse(fence_1 == fence_2)

    def test_different_thursday(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=False,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertFalse(fence_1 == fence_2)

    def test_different_friday(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=False,
            saturday=True,
            sunday=True
        )
        self.assertFalse(fence_1 == fence_2)

    def test_different_saturday(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=False,
            sunday=True
        )
        self.assertFalse(fence_1 == fence_2)

    def test_different_sunday(self):
        fence_1 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        fence_2 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=False
        )
        self.assertFalse(fence_1 == fence_2)

    def test_not_equal(self):
        timefence = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        timefence_2 = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=False,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertTrue(timefence != timefence_2)

    def test_different_type(self):
        timefence = TimeFence(
            "Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        geofence = GeoFence(1, 2, 3, "Name")
        self.assertFalse(timefence == geofence)


    def test_repr(self):
        fence_1 = TimeFence(
            "My Name",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        self.assertEqual(
            str(fence_1),
            'TimeFence <name="My Name", start_time="01:02:00", '
            'end_time="03:04:00", monday=True, tuesday=True, wednesday=True, '
            'thursday=True, friday=True, saturday=True, sunday=True>'
        )

    def test_is_serializable(self):
        fence = TimeFence(
            "AWESOME timefence",
            time(hour=1, minute=2),
            time(hour=3, minute=4),
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
            sunday=True
        )
        json.dumps(dict(fence))


class TestAuthorizationRequest(unittest.TestCase):
    def test_repr(self):
        auth_request = AuthorizationRequest('auth', 'package')
        self.assertEqual(
            str(auth_request),
            'AuthorizationRequest <auth_request="auth", '
            'push_package="package">'
        )


class TestAuthMethod(unittest.TestCase):
    def test_repr(self):
        auth_method = AuthMethod(
            AuthMethodType.FINGERPRINT,
            True,
            True,
            False,
            False,
            True,
            True,
            False
        )
        self.assertEqual(
            str(auth_method),
            'AuthMethod <method=FINGERPRINT, set=True, active=True, '
            'allowed=False, supported=False, user_required=True, passed=True, '
            'error=False>'
        )

    def test_eq_match(self):
        self.assertEqual(
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ),
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            )
        )

    def test_eq_different_method(self):
        self.assertNotEqual(
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ),
            AuthMethod(
                AuthMethodType.FACE,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            )
        )

    def test_eq_different_set(self):
        self.assertNotEqual(
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ),
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                False,
                True,
                True,
                True,
                True,
                True,
                True
            )
        )

    def test_eq_different_active(self):
        self.assertNotEqual(
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ),
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                False,
                True,
                True,
                True,
                True,
                True
            )
        )

    def test_eq_different_allowed(self):
        self.assertNotEqual(
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ),
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                False,
                True,
                True,
                True,
                True
            )
        )

    def test_eq_different_supported(self):
        self.assertNotEqual(
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ),
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                False,
                True,
                True,
                True
            )
        )

    def test_eq_different_user_required(self):
        self.assertNotEqual(
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ),
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                False,
                True,
                True
            )
        )

    def test_eq_different_user_passed(self):
        self.assertNotEqual(
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ),
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                False,
                True
            )
        )

    def test_eq_different_user_error(self):
        self.assertNotEqual(
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ),
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                False
            )
        )

    def test_eq_different_object(self):
        self.assertNotEqual(
            AuthMethod(
                AuthMethodType.FINGERPRINT,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ),
            True
        )

    def test_not_equal(self):
        method_1 = AuthMethod(
            AuthMethodType.FINGERPRINT,
            True,
            True,
            True,
            True,
            True,
            True,
            True
        )
        method_2 = AuthMethod(
            AuthMethodType.FINGERPRINT,
            False,
            True,
            True,
            True,
            True,
            True,
            True
        )
        self.assertTrue(
             method_1 != method_2
        )
