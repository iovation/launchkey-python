import unittest
from datetime import datetime, time

import pytz
from ddt import ddt, data
from mock import ANY, patch
from six import assertRaisesRegex

from launchkey.entities.service import Service, ServiceSecurityPolicy, TimeFence, GeoFence
from launchkey.entities.service.policy import ConditionalGeoFencePolicy, \
    FactorsPolicy, MethodAmountPolicy
from launchkey.exceptions import LaunchKeyAPIException, InvalidParameters, ServiceNameTaken, LastRemainingKey, \
    PublicKeyDoesNotExist, ServiceNotFound, InvalidPublicKey, PublicKeyAlreadyInUse, Forbidden, UnknownPolicyException, \
    InvalidFenceType
from launchkey.transports.base import APIResponse


class SharedTests(object):

    @ddt
    class Services(unittest.TestCase):

        def setup_client(self, client):
            self._client = client
            self._transport = self._client._transport
            self._response = APIResponse({}, {}, 200)
            self._transport.post.return_value = self._response
            self._transport.get.return_value = self._response
            self._transport.put.return_value = self._response
            self._transport.delete.return_value = self._response
            self._transport.patch.return_value = self._response

        def test_create_service_success(self):
            self._response.data = {"id": "8ea0c47c-4904-4f70-a721-ac195e0f98f2"}
            self.assertEqual(self._client.create_service(ANY), "8ea0c47c-4904-4f70-a721-ac195e0f98f2")
            self._transport.post.assert_called_once()

        def test_create_service_invalid_params(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
            with self.assertRaises(InvalidParameters):
                self._client.create_service(ANY)

        def test_create_service_service_name_taken(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "SVC-001", "error_detail": ""}, 400)
            with self.assertRaises(ServiceNameTaken):
                self._client.create_service(ANY)

        @data(True, False)
        def test_get_all_services_success(self, active):
            self._response.data = [
                {
                    "id": "abe9ff82-b665-4dd5-97e6-06fc599bb9cc",
                    "icon": "https://image.location.com/abc.png",
                    "name": "A Test Service",
                    "description": "This is a description",
                    "active": active,
                    "callback_url": "https://my.webhook.is/here"
                }
            ]
            response = self._client.get_all_services()
            self._transport.get.assert_called_once()
            self.assertEqual(len(response), 1)
            service = response[0]
            self.assertIsInstance(service, Service)
            self.assertEqual(service.id, "abe9ff82-b665-4dd5-97e6-06fc599bb9cc")
            self.assertEqual(service.icon, "https://image.location.com/abc.png")
            self.assertEqual(service.name, "A Test Service")
            self.assertEqual(service.description, "This is a description")
            self.assertEqual(service.active, active)
            self.assertEqual(service.callback_url, "https://my.webhook.is/here")

        @data(True, False)
        def test_get_services_success(self, active):
            self._response.data = [
                {
                    "id": "abe9ff82-b665-4dd5-97e6-06fc599bb9cc",
                    "icon": "https://image.location.com/abc.png",
                    "name": "A Test Service",
                    "description": "This is a description",
                    "active": active,
                    "callback_url": "https://my.webhook.is/here"
                }
            ]
            response = self._client.get_services("abe9ff82-b665-4dd5-97e6-06fc599bb9cc")
            self._transport.post.assert_called_once()
            self.assertEqual(len(response), 1)
            service = response[0]
            self.assertIsInstance(service, Service)
            self.assertEqual(service.id, "abe9ff82-b665-4dd5-97e6-06fc599bb9cc")
            self.assertEqual(service.icon, "https://image.location.com/abc.png")
            self.assertEqual(service.name, "A Test Service")
            self.assertEqual(service.description, "This is a description")
            self.assertEqual(service.active, active)
            self.assertEqual(service.callback_url, "https://my.webhook.is/here")

        def test_get_services_invalid_params(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
            with self.assertRaises(InvalidParameters):
                self._client.get_services("a69d46cf-aac4-42c6-ae3d-5fca8a2546bc")

        @data(True, False)
        def test_get_service_success(self, active):
            self._response.data = [
                {
                    "id": "abe9ff82-b665-4dd5-97e6-06fc599bb9cc",
                    "icon": "https://image.location.com/abc.png",
                    "name": "A Test Service",
                    "description": "This is a description",
                    "active": active,
                    "callback_url": "https://my.webhook.is/here"
                }
            ]
            service = self._client.get_service("abe9ff82-b665-4dd5-97e6-06fc599bb9cc")
            self._transport.post.assert_called_once()
            self.assertIsInstance(service, Service)
            self.assertEqual(service.id, "abe9ff82-b665-4dd5-97e6-06fc599bb9cc")
            self.assertEqual(service.icon, "https://image.location.com/abc.png")
            self.assertEqual(service.name, "A Test Service")
            self.assertEqual(service.description, "This is a description")
            self.assertEqual(service.active, active)
            self.assertEqual(service.callback_url, "https://my.webhook.is/here")

        def test_get_service_invalid_params(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
            with self.assertRaises(InvalidParameters):
                self._client.get_service(ANY)

        def test_update_service_success(self):
            self._client.update_service("23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf")
            self._transport.patch.assert_called_once()
            self.assertIn({"service_id": "23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf"}, self._transport.patch.call_args)

        def test_update_service_name(self):
            self._client.update_service("23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf", name="A Name")
            self._transport.patch.assert_called_once()
            self.assertIn({"service_id": "23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf",
                           "name": "A Name"}, self._transport.patch.call_args)

        def test_update_service_description(self):
            self._client.update_service("23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf", description="A Description")
            self._transport.patch.assert_called_once()
            self.assertIn({"service_id": "23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf",
                           "description": "A Description"}, self._transport.patch.call_args)

        def test_update_service_icon(self):
            self._client.update_service("23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf",
                                        icon="https://image.location.com/abc.png")
            self._transport.patch.assert_called_once()
            self.assertIn({"service_id": "23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf",
                           "icon": "https://image.location.com/abc.png"}, self._transport.patch.call_args)

        def test_update_service_callback_url(self):
            self._client.update_service("23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf",
                                        callback_url="https://my.webhook.is/here")
            self._transport.patch.assert_called_once()
            self.assertIn({"service_id": "23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf",
                           "callback_url": "https://my.webhook.is/here"}, self._transport.patch.call_args)

        @data(True, False)
        def test_update_service_active(self, active):
            self._client.update_service("23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf",
                                        active=active)
            self._transport.patch.assert_called_once()
            self.assertIn({"service_id": "23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf",
                           "active": active}, self._transport.patch.call_args)

        @data(True, False)
        def test_update_service_all(self, active):
            self._client.update_service(
                "23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf",
                name="A Name",
                description="A Description",
                icon="https://image.location.com/abc.png",
                callback_url="https://my.webhook.is/here",
                active=active
            )
            self._transport.patch.assert_called_once()
            self.assertIn(
                {
                    "service_id": "23c0e1a0-e7a5-4a26-befc-9fd4504b5bbf",
                    "name": "A Name",
                    "description": "A Description",
                    "icon": "https://image.location.com/abc.png",
                    "callback_url": "https://my.webhook.is/here",
                    "active": active
                },
                self._transport.patch.call_args
            )

        def test_update_service_invalid_params(self):
            self._transport.patch.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""},
                                                                      400)
            with self.assertRaises(InvalidParameters):
                self._client.update_service(ANY)

        def test_update_service_forbidden(self):
            self._transport.patch.side_effect = LaunchKeyAPIException({}, 403)
            with self.assertRaises(Forbidden):
                self._client.update_service(ANY)

        def test_add_service_public_key_success(self):
            self._response.data = {"key_id": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz"}
            key_id = self._client.add_service_public_key("5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key")
            self._transport.post.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + "/keys",
                self._expected_subject,
                service_id="5e49fc4c-ddcb-48db-8473-a5f996b85fbc",
                public_key="public-key")
            self.assertEqual(key_id, "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")

        def test_add_service_public_key_expires(self):
            self._response.data = {"key_id": ANY}
            self._client.add_service_public_key(
                "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key",
                expires=datetime(year=2017, month=10, day=3, hour=22,
                                 minute=50, second=15))
            self._transport.post.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + "/keys",
                self._expected_subject,
                service_id="5e49fc4c-ddcb-48db-8473-a5f996b85fbc",
                public_key="public-key", date_expires="2017-10-03T22:50:15Z")

        @data(True, False)
        def test_add_service_public_key_active(self, active):
            self._response.data = {"key_id": ANY}
            self._client.add_service_public_key(
                "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key",
                active=active)
            self._transport.post.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + "/keys",
                self._expected_subject,
                service_id="5e49fc4c-ddcb-48db-8473-a5f996b85fbc",
                public_key="public-key", active=active)

        @data(True, False)
        def test_add_service_public_key_all(self, active):
            self._response.data = {"key_id": ANY}
            self._client.add_service_public_key(
                "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key",
                expires=datetime(year=2017, month=10, day=3, hour=22,
                                 minute=50, second=15), active=active)
            self._transport.post.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + "/keys",
                self._expected_subject,
                service_id="5e49fc4c-ddcb-48db-8473-a5f996b85fbc",
                public_key="public-key", date_expires="2017-10-03T22:50:15Z",
                active=active)

        def test_add_service_public_key_invalid_params(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
            with self.assertRaises(InvalidParameters):
                self._client.add_service_public_key(ANY, ANY)

        def test_add_service_public_key_invalid_public_key(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "KEY-001", "error_detail": ""}, 400)
            with self.assertRaises(InvalidPublicKey):
                self._client.add_service_public_key(ANY, ANY)

        def test_add_service_public_key_invalid_key_already_in_use(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "KEY-002", "error_detail": ""}, 400)
            with self.assertRaises(PublicKeyAlreadyInUse):
                self._client.add_service_public_key(ANY, ANY)

        def test_add_service_public_key_forbidden(self):
            self._transport.post.side_effect = LaunchKeyAPIException({}, 403)
            with self.assertRaises(Forbidden):
                self._client.add_service_public_key(ANY, ANY)

        @data(True, False)
        def test_get_service_public_keys(self, active):
            self._response.data = [
                {
                    "id": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                    "active": active,
                    "date_created": "2017-10-03T22:50:15Z",
                    "date_expires": "2018-10-03T22:50:15Z",
                    "public_key": "A Public Key"
                }
            ]
            public_keys = self._client.get_service_public_keys(
                "3559a520-180f-4fee-ad52-75959286340d")

            self._transport.post.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + "/keys/list",
                self._expected_subject,
                service_id="3559a520-180f-4fee-ad52-75959286340d")

            self.assertEqual(len(public_keys), 1)
            key = public_keys[0]
            self.assertEqual(key.id, "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")
            self.assertEqual(key.active, active)
            self.assertEqual(key.created, datetime(year=2017, month=10, day=3, hour=22, minute=50,
                                                   second=15, tzinfo=pytz.timezone("UTC")))
            self.assertEqual(key.expires, datetime(year=2018, month=10, day=3, hour=22, minute=50,
                                                   second=15, tzinfo=pytz.timezone("UTC")))
            self.assertEqual(key.public_key, "A Public Key")

        def test_get_service_public_keys_invalid_params(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""},
                                                                     400)
            with self.assertRaises(InvalidParameters):
                self._client.get_service_public_keys(ANY)

        def test_get_service_public_keys_service_not_found(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "SVC-004", "error_detail": ""}, 400)
            with self.assertRaises(ServiceNotFound):
                self._client.get_service_public_keys(ANY)

        def test_get_service_public_keys_forbidden(self):
            self._transport.post.side_effect = LaunchKeyAPIException({}, 403)
            with self.assertRaises(Forbidden):
                self._client.get_service_public_keys(ANY)

        def test_remove_service_public_key_success(self):
            expected_service_id = "5e49fc4c-ddcb-48db-8473-a5f996b85fbc"
            expected_key_id = "expected-public-key"
            self._client.remove_service_public_key(expected_service_id[:],
                                                   expected_key_id[:])
            self._transport.delete.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + "/keys",
                self._expected_subject, service_id=expected_service_id,
                key_id=expected_key_id)

        def test_remove_service_invalid_params(self):
            self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""},
                                                                       400)
            with self.assertRaises(InvalidParameters):
                self._client.remove_service_public_key(ANY, ANY)

        def test_remove_service_public_key_public_key_does_not_exist(self):
            self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "KEY-003", "error_detail": ""},
                                                                       400)
            with self.assertRaises(PublicKeyDoesNotExist):
                self._client.remove_service_public_key(ANY, ANY)

        def test_remove_remove_service_public_key_last_remaining_key(self):
            self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "KEY-004", "error_detail": ""},
                                                                       400)
            with self.assertRaises(LastRemainingKey):
                self._client.remove_service_public_key(ANY, ANY)

        def test_remove_service_public_key_forbidden(self):
            self._transport.delete.side_effect = LaunchKeyAPIException({}, 403)
            with self.assertRaises(Forbidden):
                self._client.remove_service_public_key(ANY, ANY)

        def test_update_service_public_key(self):
            self._client.update_service_public_key(
                "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")
            self._transport.patch.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/keys',
                self._expected_subject,
                service_id="1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                key_id="ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")

        def test_update_service_public_key_expires(self):
            self._client.update_service_public_key(
                "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                expires=datetime(year=2017, month=10, day=3, hour=22,
                                 minute=50, second=15))
            self._transport.patch.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/keys',
                self._expected_subject,
                service_id="1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                key_id="ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                date_expires="2017-10-03T22:50:15Z")

        @data(True, False)
        def test_update_service_public_key_active(self, active):
            self._client.update_service_public_key(
                "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                active=active)
            self._transport.patch.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/keys',
                self._expected_subject,
                service_id="1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                key_id="ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                active=active)

        @data(True, False)
        def test_update_service_public_key_all(self, active):
            self._client.update_service_public_key(
                "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                expires=datetime(year=2017, month=10, day=3, hour=22,
                                 minute=50, second=15),
                active=active)
            self._transport.patch.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/keys',
                self._expected_subject,
                service_id="1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                key_id="ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                date_expires="2017-10-03T22:50:15Z",
                active=active)

        def test_update_service_public_key_public_key_invalid_params(self):
            self._transport.patch.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""},
                                                                      400)
            with self.assertRaises(InvalidParameters):
                self._client.update_service_public_key(ANY, ANY)

        def test_update_service_public_key_public_key_does_not_exist(self):
            self._transport.patch.side_effect = LaunchKeyAPIException({"error_code": "KEY-003", "error_detail": ""},
                                                                      400)
            with self.assertRaises(PublicKeyDoesNotExist):
                self._client.update_service_public_key(ANY, ANY)

        def test_update_service_public_key_forbidden(self):
            self._transport.patch.side_effect = LaunchKeyAPIException({}, 403)
            with self.assertRaises(Forbidden):
                self._client.update_service_public_key(ANY, ANY)

        def test_get_service_policy_success(self):
            self._response.data = {
                'minimum_requirements': [
                    {
                        'possession': 1,
                        'requirement': 'authenticated',
                        'any': 0,
                        'inherence': 1,
                        'knowledge': 1
                    }
                ],
                'factors': []
            }
            expected_service_id = 'expected-service-id'
            policy = self._client.get_service_policy(expected_service_id[:])
            self._transport.post.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/policy/item',
                self._expected_subject,
                service_id=expected_service_id
            )
            self.assertIsInstance(policy, ServiceSecurityPolicy)
            self.assertEqual(policy.minimum_amount, 0)
            self.assertIn('possession', policy.minimum_requirements)
            self.assertIn('inherence', policy.minimum_requirements)
            self.assertIn('knowledge', policy.minimum_requirements)

        def test_get_service_policy_invalid_params(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
            with self.assertRaises(InvalidParameters):
                self._client.get_service_policy(ANY)

        def test_get_service_policy_service_not_found(self):
            self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "SVC-004", "error_detail": ""}, 400)
            with self.assertRaises(ServiceNotFound):
                self._client.get_service_policy(ANY)

        def test_set_service_policy_success(self):
            expected_service_id = 'expected-service-id'
            policy_called_with = {
                'factors': [{
                    'factor': 'device integrity',
                              'requirement': 'forced requirement',
                              'quickfail': False,
                              'priority': 1,
                              'attributes': {'factor enabled': 0}
                    }],
                'minimum_requirements': []
            }

            self._client.set_service_policy(expected_service_id[:],
                                            ServiceSecurityPolicy())
            self._transport.put.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/policy',
                self._expected_subject, service_id=expected_service_id,
                policy=policy_called_with
            )

        def test_set_service_policy_invalid_params(self):
            self._transport.put.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
            with self.assertRaises(InvalidParameters):
                self._client.set_service_policy(ANY, ServiceSecurityPolicy())

        def test_set_service_policy_service_not_found(self):
            self._transport.put.side_effect = LaunchKeyAPIException({"error_code": "SVC-004", "error_detail": ""}, 400)
            with self.assertRaises(ServiceNotFound):
                self._client.set_service_policy(ANY, ServiceSecurityPolicy())

        def test_remove_service_policy_success(self):
            expected_service_id = 'expected-service-id'
            self._client.remove_service_policy(expected_service_id[:])
            self._transport.delete.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/policy',
                self._expected_subject, service_id=expected_service_id)

        def test_remove_service_policy_invalid_params(self):
            self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""},
                                                                       400)
            with self.assertRaises(InvalidParameters):
                self._client.remove_service_policy(ANY)

        def test_remove_service_policy_service_not_found(self):
            self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "SVC-004", "error_detail": ""},
                                                                       400)
            with self.assertRaises(ServiceNotFound):
                self._client.remove_service_policy(ANY)

        def test_get_service_policy_parses_timefences(self):
            self._response.data = {
                "factors": [{
                    "attributes": {
                        "time fences": [{
                            "days": ["Monday", "Sunday"],
                            "end hour": 23,
                            "end minute": 45,
                            "name": "sup",
                            "start hour": 12,
                            "start minute": 30,
                            "timezone": "UTC"
                        }]
                    },
                    "factor": "timefence",
                    "priority": 1,
                    "quickfail": False,
                    "requirement": "forced requirement"
                }],
                "minimum_requirements": []
            }

            expected_service_id = 'expected-service-id'
            policy = self._client.get_service_policy(expected_service_id)
            self.assertIsInstance(policy, ServiceSecurityPolicy)
            self.assertIsInstance(policy.timefences[0], TimeFence)

        def test_get_service_policy_parses_geofences(self):
            self._response.data = {
                "factors": [{
                    "attributes": {
                        "locations": [{
                            "latitude": 30.0,
                            "longitude": 30.0,
                            "name": "AWESOME geofence",
                            "radius": 3000.0
                        }]
                    },
                    "factor": "geofence",
                    "priority": 1,
                    "quickfail": False,
                    "requirement": "forced requirement"
                }],
                "minimum_requirements": []
            }

            expected_service_id = 'expected-service-id'
            policy = self._client.get_service_policy(expected_service_id)
            self.assertIsInstance(policy, ServiceSecurityPolicy)
            self.assertIsInstance(policy.geofences[0], GeoFence)

        def test_get_service_policy_throws_when_geofence_has_no_name(self):
            self._response.data = {
                "factors": [{
                    "attributes": {
                        "locations": [{
                            "latitude": 30.0,
                            "longitude": 30.0,
                            "radius": 3000.0
                        }]
                    },
                    "factor": "geofence",
                    "priority": 1,
                    "quickfail": False,
                    "requirement": "forced requirement"
                }],
                "minimum_requirements": []
            }

            expected_service_id = 'expected-service-id'

            with self.assertRaises(ValueError):
                self._client.get_service_policy(expected_service_id)

        @patch('launchkey.clients.base.warnings.warn')
        def test_get_service_policy_warns_when_not_a_legacy_policy(self, warn):
            self._response.data = {
                "type": "COND_GEO",
                "fences": [{
                               "name": "Ontario",
                               "type": "TERRITORY",
                               "country": "CA",
                               "administrative_area": "CA-ON"}
                ],
                "inside": {
                    "type": "FACTORS",
                    "fences": [],
                    "factors": ["POSSESSION"]
                },
                "outside": {
                    "type": "METHOD_AMOUNT",
                    "fences": [],
                    "amount": 1
                },
                "deny_rooted_jailbroken": False,
                "deny_emulator_simulator": False
            }

            expected_service_id = 'expected-service-id'
            policy = self._client.get_service_policy(expected_service_id)
            self.assertIsNone(policy)
            warn.assert_called_with("Policy received was not a legacy policy and cannot "
                                             "be converted into a ServiceSecurityPolicy.",
                                             category=DeprecationWarning)

        def test_get_advanced_service_policy_conditional_geofence(self):
            self._response.data = {
                "type": "COND_GEO",
                "fences": [{
                    "name": "Ontario",
                    "type": "TERRITORY",
                    "country": "CA",
                    "administrative_area": "CA-ON"}
                ],
                "inside": {
                    "type": "FACTORS",
                    "fences": [],
                    "factors": ["POSSESSION"]
                },
                "outside": {
                    "type": "METHOD_AMOUNT",
                    "fences": [],
                    "amount": 1
                },
                "deny_rooted_jailbroken": False,
                "deny_emulator_simulator": False
            }

            expected_service_id = 'expected-service-id'
            policy = self._client.get_advanced_service_policy(expected_service_id[:])
            self._transport.post.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/policy/item',
                self._expected_subject,
                service_id=expected_service_id
            )
            self.assertIsInstance(policy, ConditionalGeoFencePolicy)
            self.assertIsInstance(policy, ConditionalGeoFencePolicy)
            self.assertIsInstance(policy.inside, FactorsPolicy)
            self.assertIsInstance(policy.inside, FactorsPolicy)
            self.assertTrue(policy.inside.possession_required)
            self.assertEqual(0, len(policy.inside.fences))
            self.assertIsInstance(policy.outside, MethodAmountPolicy)
            self.assertIsInstance(policy.outside, MethodAmountPolicy)
            self.assertEqual(0, len(policy.outside.fences))
            self.assertEqual(1, policy.outside.amount)

        def test_get_service_policy_legacy(self):
            self._response.data = {
                'minimum_requirements': [
                    {
                        'possession': 1,
                        'requirement': 'authenticated',
                        'any': 0,
                        'inherence': 1,
                        'knowledge': 1
                    }
                ],
                'factors': []
            }

            expected_service_id = 'expected-service-id'
            policy = self._client.get_service_policy(expected_service_id[:])
            self._transport.post.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/policy/item',
                self._expected_subject,
                service_id=expected_service_id
            )
            self.assertIsInstance(policy, ServiceSecurityPolicy)
            self.assertEqual(0, len(policy.geofences))
            self.assertEqual(0, len(policy.timefences))
            self.assertEqual(3, len(policy.minimum_requirements))
            self.assertEqual(0, policy.minimum_amount)

        def test_get_advanced_service_policy_method_amount(self):
            self._response.data = {
                "type": "METHOD_AMOUNT",
                "amount": 1,
                "fences": [
                    {
                        "name": "LV-89102",
                        "type": "TERRITORY",
                        "country": "US",
                        "postal_code": "89012"
                    },
                    {
                        "name": "California",
                        "type": "TERRITORY",
                        "country": "US",
                        "administrative_area": "US-CA",
                        "postal_code": "92535"
                    },
                    {
                        "name": "Ontario",
                        "type": "TERRITORY",
                        "country": "CA",
                        "administrative_area": "CA-ON"
                    }
                ]
            }

            expected_service_id = 'expected-service-id'
            policy = self._client.get_advanced_service_policy(expected_service_id[:])
            self._transport.post.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/policy/item',
                self._expected_subject,
                service_id=expected_service_id
            )
            self.assertIsInstance(policy, MethodAmountPolicy)
            self.assertEqual(policy.amount, 1)
            self.assertEqual(len(policy.fences), 3)

        def test_get_advanced_service_policy_factors(self):
            self._response.data = {
                "type": "FACTORS",
                "factors": ["POSSESSION"],
                "fences": [
                    {
                        "name": "LV-89102",
                        "type": "TERRITORY",
                        "country": "US",
                        "postal_code": "89012"
                    },
                    {
                        "name": "Point A",
                        "type": "GEO_CIRCLE",
                        "latitude": 123.45,
                        "longitude": -23.45,
                        "radius": 105
                    }
                ]
            }

            expected_service_id = 'expected-service-id'
            policy = self._client.get_advanced_service_policy(expected_service_id[:])
            self._transport.post.assert_called_once_with(
                self._expected_base_endpoint[0:-1] + '/policy/item',
                self._expected_subject,
                service_id=expected_service_id
            )
            self.assertIsInstance(policy, FactorsPolicy)
            self.assertTrue(policy.possession_required)
            self.assertEqual(len(policy.fences), 2)

        def test_nested_conditional_throws_exception(self):
            self._response.data = {
                "type": "COND_GEO",
                "fences": [{
                    "name": "Ontario",
                    "type": "TERRITORY",
                    "country": "CA",
                    "administrative_area": "CA-ON"}
                ],
                "inside": {
                    "type": "FACTORS",
                    "fences": [],
                    "factors": ["POSSESSION"]
                },
                "outside": {
                    "type": "COND_GEO",
                    "fences": [{
                        "name": "Ontario",
                        "type": "TERRITORY",
                        "country": "CA",
                        "administrative_area": "CA-ON"}
                    ],
                    "inside": {
                        "type": "FACTORS",
                        "fences": [],
                        "factors": ["POSSESSION"]
                    },
                    "outside": {
                        "type": "METHOD_AMOUNT",
                        "fences": [],
                        "amount": 1
                    }
                }
            }

            expected_service_id = 'expected-service-id'
            with assertRaisesRegex(self, UnknownPolicyException,
                                   "Valid nested Policy types for ConditionalGeofence Policies are:"):
                self._client.get_service_policy(expected_service_id[:])

        def test_invalid_geofence_raises_not_implemented(self):
            self._response.data = {
                "type": "COND_GEO",
                "fences": [{
                    "type": "OLD_GEOFENCE",
                    "name": "GEOFENCE",
                    "latitude": 123.45,
                    "longitude": -23.45,
                    "radius": 105
                }],
                "inside": {
                    "type": "FACTORS",
                    "fences": [],
                    "factors": ["POSSESSION"]
                },
                "outside": {
                    "type": "FACTORS",
                    "fences": [],
                    "factors": ["POSSESSION", "KNOWLEDGE"]
                }
            }

            expected_service_id = 'expected-service-id'
            with self.assertRaises(InvalidFenceType):
                self._client.get_service_policy(expected_service_id[:])


        def test_new_policy_type_raises_unknown_policy_exception(self):
            self._response.data = {
                "type": "NEW_POLICY",
                "fences": [],
                "inside": {
                    "type": "FACTORS",
                    "fences": [],
                    "factors": ["POSSESSION"]
                },
                "outside": {
                    "type": "FACTORS",
                    "fences": [],
                    "factors": ["POSSESSION", "KNOWLEDGE"]
                }
            }

            expected_service_id = 'expected-service-id'
            with self.assertRaises(UnknownPolicyException):
                self._client.get_service_policy(expected_service_id[:])
