import unittest
from mock import ANY
from launchkey.entities.service import Service, ServiceSecurityPolicy
from launchkey.transports.base import APIResponse
from launchkey.exceptions import LaunchKeyAPIException, InvalidParameters, ServiceNameTaken, LastRemainingKey, \
    PublicKeyDoesNotExist, ServiceNotFound, InvalidPublicKey, PublicKeyAlreadyInUse, Forbidden
from datetime import datetime
import pytz
from ddt import ddt, data


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
            self._transport.post.assert_called_once()
            self.assertIn({"service_id": "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public_key": "public-key"},
                          self._transport.post.call_args)
            self.assertEqual(key_id, "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")

        def test_add_service_public_key_expires(self):
            self._response.data = {"key_id": ANY}
            self._client.add_service_public_key("5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key",
                                                expires=datetime(year=2017, month=10, day=3, hour=22,
                                                                 minute=50, second=15))
            self._transport.post.assert_called_once()
            self.assertIn({"service_id": "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public_key": "public-key",
                           "date_expires": "2017-10-03T22:50:15Z"},
                          self._transport.post.call_args)

        @data(True, False)
        def test_add_service_public_key_active(self, active):
            self._response.data = {"key_id": ANY}
            self._client.add_service_public_key("5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key",
                                                active=active)
            self.assertIn({"service_id": "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public_key": "public-key",
                           "active": active}, self._transport.post.call_args)

        @data(True, False)
        def test_add_service_public_key_all(self, active):
            self._response.data = {"key_id": ANY}
            self._client.add_service_public_key("5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key",
                                                expires=datetime(year=2017, month=10, day=3, hour=22,
                                                                 minute=50, second=15), active=active)
            self._transport.post.assert_called_once()
            self.assertIn({"service_id": "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public_key": "public-key",
                           "date_expires": "2017-10-03T22:50:15Z", "active": active},
                          self._transport.post.call_args)

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
            public_keys = self._client.get_service_public_keys("3559a520-180f-4fee-ad52-75959286340d")
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
            self._client.remove_service_public_key(ANY, ANY)
            self._transport.delete.assert_called_once()

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

        def test_remove_service_last_remaining_key(self):
            self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "KEY-004", "error_detail": ""},
                                                                       400)
            with self.assertRaises(LastRemainingKey):
                self._client.remove_service_public_key(ANY, ANY)

        def test_remove_service_forbidden(self):
            self._transport.delete.side_effect = LaunchKeyAPIException({}, 403)
            with self.assertRaises(Forbidden):
                self._client.remove_service_public_key(ANY, ANY)

        def test_update_service_public_key(self):
            self._client.update_service_public_key("1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                                                   "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")
            self._transport.patch.assert_called_once()
            self.assertIn({"service_id": "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                           "key_id": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz"},
                          self._transport.patch.call_args)

        def test_update_service_public_key_expires(self):
            self._client.update_service_public_key("1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                                                   "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                                                   expires=datetime(year=2017, month=10, day=3, hour=22,
                                                                    minute=50, second=15))
            self._transport.patch.assert_called_once()
            self.assertIn({"service_id": "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                           "key_id": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                           "date_expires": "2017-10-03T22:50:15Z"},
                          self._transport.patch.call_args)

        @data(True, False)
        def test_update_service_public_key_active(self, active):
            self._client.update_service_public_key("1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                                                   "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                                                   active=active)
            self._transport.patch.assert_called_once()
            self.assertIn({"service_id": "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                           "key_id": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                           "active": active},
                          self._transport.patch.call_args)

        @data(True, False)
        def test_update_service_public_key_all(self, active):
            self._client.update_service_public_key("1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                                                   "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                                                   expires=datetime(year=2017, month=10, day=3, hour=22,
                                                                    minute=50, second=15),
                                                   active=active)
            self._transport.patch.assert_called_once()
            self.assertIn({"service_id": "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
                           "key_id": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                           "date_expires": "2017-10-03T22:50:15Z",
                           "active": active},
                          self._transport.patch.call_args)

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
                        'all': 1,
                        'inherence': 1,
                        'knowledge': 1
                    }
                ],
                'factors': []
            }
            policy = self._client.get_service_policy(ANY)
            self._transport.post.assert_called_once()
            self.assertIsInstance(policy, ServiceSecurityPolicy)
            self.assertEqual(policy.minimum_amount, 1)
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
            self._client.set_service_policy(ANY, ServiceSecurityPolicy())
            self._transport.put.assert_called_once()

        def test_set_service_policy_invalid_params(self):
            self._transport.put.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
            with self.assertRaises(InvalidParameters):
                self._client.set_service_policy(ANY, ServiceSecurityPolicy())

        def test_set_service_policy_service_not_found(self):
            self._transport.put.side_effect = LaunchKeyAPIException({"error_code": "SVC-004", "error_detail": ""}, 400)
            with self.assertRaises(ServiceNotFound):
                self._client.set_service_policy(ANY, ServiceSecurityPolicy())

        def test_remove_service_policy_success(self):
            self._client.remove_service_policy(ANY)
            self._transport.delete.assert_called_once()

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
