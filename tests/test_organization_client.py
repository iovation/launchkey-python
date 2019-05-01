import unittest
from mock import MagicMock, ANY
from uuid import uuid4
from launchkey.clients import OrganizationClient
from launchkey.clients.organization import Directory
from launchkey.transports.base import APIResponse
from launchkey.exceptions import LaunchKeyAPIException, InvalidParameters, LastRemainingKey, PublicKeyDoesNotExist, \
    InvalidPublicKey, PublicKeyAlreadyInUse, LastRemainingSDKKey, InvalidSDKKey, Forbidden, EntityNotFound
from datetime import datetime
import pytz
from .shared import SharedTests
from ddt import ddt, data

try:
    from base64 import encodebytes as encodestring
except ImportError:
    from base64 import encodestring


class TestOrganizationClient(SharedTests.Services):

    def setUp(self):
        self._organization_id = uuid4()
        client = OrganizationClient(self._organization_id, MagicMock())
        self._expected_base_endpoint = '/organization/v3/services'
        self._expected_subject = 'org:{}'.format(str(self._organization_id))
        self.setup_client(client)


@ddt
class TestOrganizationClientDirectories(unittest.TestCase):

    def setUp(self):
        self._transport = MagicMock()
        self._response = APIResponse({}, {}, 200)
        self._transport.post.return_value = self._response
        self._transport.get.return_value = self._response
        self._transport.put.return_value = self._response
        self._transport.delete.return_value = self._response
        self._transport.patch.return_value = self._response
        self._organization_id = uuid4()
        self._expected_subject = 'org:{}'.format(str(self._organization_id))
        self._organization_client = OrganizationClient(self._organization_id,
                                                       self._transport)

    def test_create_directory_success(self):
        self._response.data = {"id": "2ee0bd0a-a493-4376-9ff3-5936bd7da67b"}
        directory_id = self._organization_client.create_directory("name")
        self.assertEqual(directory_id, "2ee0bd0a-a493-4376-9ff3-5936bd7da67b")
        self._transport.post.assert_called_once_with(
            "/organization/v3/directories", self._expected_subject,
            name="name")

    def test_get_all_directories(self):
        self._response.data = [
            {
                "id": "abe9ff82-b665-4dd5-97e6-06fc599bb9cc",
                "service_ids": ["9d2038f8-8e46-4106-b4b7-94929e474ffc", "a2670521-d66c-4761-93c7-474537a6bd5f"],
                "sdk_keys": ["a99db42d-0aab-4e7f-80a6-163b31ef9f31", "b9a949d1-ec5b-4395-b978-47fc7183ffce"],
                "premium": True,
                "name": "A Test Directory",
                "android_key": "afb1ad83-09d5-427a-b097-e8aa982c4d6c",
                "ios_certificate_fingerprint": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                "active": True
            }
        ]
        response = self._organization_client.get_all_directories()
        self._transport.get.assert_called_once_with(
            "/organization/v3/directories", self._expected_subject)
        self.assertEqual(len(response), 1)
        directory = response[0]
        self.assertIsInstance(directory, Directory)
        self.assertEqual(directory.id, "abe9ff82-b665-4dd5-97e6-06fc599bb9cc")
        self.assertIsInstance(directory.service_ids, list)
        self.assertIn("9d2038f8-8e46-4106-b4b7-94929e474ffc", directory.service_ids)
        self.assertIn("a2670521-d66c-4761-93c7-474537a6bd5f", directory.service_ids)
        self.assertIsInstance(directory.sdk_keys, list)
        self.assertIn("a99db42d-0aab-4e7f-80a6-163b31ef9f31", directory.sdk_keys)
        self.assertIn("b9a949d1-ec5b-4395-b978-47fc7183ffce", directory.sdk_keys)
        self.assertEqual(directory.premium, True)
        self.assertEqual(directory.name, "A Test Directory")
        self.assertEqual(directory.android_key, "afb1ad83-09d5-427a-b097-e8aa982c4d6c")
        self.assertEqual(directory.ios_certificate_fingerprint, "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")
        self.assertEqual(directory.active, True)

    def test_get_directories(self):
        self._response.data = [
            {
                "id": "abe9ff82-b665-4dd5-97e6-06fc599bb9cc",
                "service_ids": ["9d2038f8-8e46-4106-b4b7-94929e474ffc", "a2670521-d66c-4761-93c7-474537a6bd5f"],
                "sdk_keys": ["a99db42d-0aab-4e7f-80a6-163b31ef9f31", "b9a949d1-ec5b-4395-b978-47fc7183ffce"],
                "premium": True,
                "name": "A Test Directory",
                "android_key": "afb1ad83-09d5-427a-b097-e8aa982c4d6c",
                "ios_certificate_fingerprint": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                "active": True
            }
        ]
        response = self._organization_client.get_directories(["760b2ae5-b44b-49ac-a83c-d3421b30936f"])
        self._transport.post.assert_called_once_with(
            "/organization/v3/directories/list", self._expected_subject,
            directory_ids=["760b2ae5-b44b-49ac-a83c-d3421b30936f"])
        self.assertEqual(len(response), 1)
        directory = response[0]
        self.assertIsInstance(directory, Directory)
        self.assertEqual(directory.id, "abe9ff82-b665-4dd5-97e6-06fc599bb9cc")
        self.assertIsInstance(directory.service_ids, list)
        self.assertIn("9d2038f8-8e46-4106-b4b7-94929e474ffc", directory.service_ids)
        self.assertIn("a2670521-d66c-4761-93c7-474537a6bd5f", directory.service_ids)
        self.assertIsInstance(directory.sdk_keys, list)
        self.assertIn("a99db42d-0aab-4e7f-80a6-163b31ef9f31", directory.sdk_keys)
        self.assertIn("b9a949d1-ec5b-4395-b978-47fc7183ffce", directory.sdk_keys)
        self.assertEqual(directory.premium, True)
        self.assertEqual(directory.name, "A Test Directory")
        self.assertEqual(directory.android_key, "afb1ad83-09d5-427a-b097-e8aa982c4d6c")
        self.assertEqual(directory.ios_certificate_fingerprint, "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")
        self.assertEqual(directory.active, True)

    def test_get_directories_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._organization_client.get_directories("c7d4ffcd-069d-4ea7-9994-03c25ce42bd8")

    def test_get_directory(self):
        self._response.data = [
            {
                "id": "abe9ff82-b665-4dd5-97e6-06fc599bb9cc",
                "service_ids": ["9d2038f8-8e46-4106-b4b7-94929e474ffc", "a2670521-d66c-4761-93c7-474537a6bd5f"],
                "sdk_keys": ["a99db42d-0aab-4e7f-80a6-163b31ef9f31", "b9a949d1-ec5b-4395-b978-47fc7183ffce"],
                "premium": True,
                "name": "A Test Directory",
                "android_key": "afb1ad83-09d5-427a-b097-e8aa982c4d6c",
                "ios_certificate_fingerprint": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                "active": True
            }
        ]
        directory = self._organization_client.get_directory("directory_id")
        self._transport.post.assert_called_once_with(
            "/organization/v3/directories/list", self._expected_subject,
            directory_ids=["directory_id"])
        self.assertIsInstance(directory, Directory)
        self.assertEqual(directory.id, "abe9ff82-b665-4dd5-97e6-06fc599bb9cc")
        self.assertIsInstance(directory.service_ids, list)
        self.assertIn("9d2038f8-8e46-4106-b4b7-94929e474ffc", directory.service_ids)
        self.assertIn("a2670521-d66c-4761-93c7-474537a6bd5f", directory.service_ids)
        self.assertIsInstance(directory.sdk_keys, list)
        self.assertIn("a99db42d-0aab-4e7f-80a6-163b31ef9f31", directory.sdk_keys)
        self.assertIn("b9a949d1-ec5b-4395-b978-47fc7183ffce", directory.sdk_keys)
        self.assertEqual(directory.premium, True)
        self.assertEqual(directory.name, "A Test Directory")
        self.assertEqual(directory.android_key, "afb1ad83-09d5-427a-b097-e8aa982c4d6c")
        self.assertEqual(directory.ios_certificate_fingerprint, "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")
        self.assertEqual(directory.active, True)

    def test_get_directory_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._organization_client.get_directory(ANY)

    def test_update_directory_success(self):
        self._organization_client.update_directory("683e9dea-5128-471e-8264-6f8f6ba522ab")
        self._transport.patch.assert_called_once()
        self.assertIn({"directory_id": "683e9dea-5128-471e-8264-6f8f6ba522ab"}, self._transport.patch.call_args)

    def test_update_directory_ios_p12(self):
        self._organization_client.update_directory("683e9dea-5128-471e-8264-6f8f6ba522ab", ios_p12=b'An iOS P12')
        self._transport.patch.assert_called_once_with(
            "/organization/v3/directories", self._expected_subject,
            directory_id="683e9dea-5128-471e-8264-6f8f6ba522ab",
            ios_p12=encodestring(b'An iOS P12').decode('utf-8'))

    def test_update_directory_android_key(self):
        self._organization_client.update_directory(
            "683e9dea-5128-471e-8264-6f8f6ba522ab",
           android_key="465e74df-13a0-4049-8f31-a9715cb8c12b")
        self._transport.patch.assert_called_once_with(
            "/organization/v3/directories", self._expected_subject,
            directory_id="683e9dea-5128-471e-8264-6f8f6ba522ab",
            android_key="465e74df-13a0-4049-8f31-a9715cb8c12b")

    def test_update_directory_active(self):
        self._organization_client.update_directory(
            "683e9dea-5128-471e-8264-6f8f6ba522ab", active=True)
        self._transport.patch.assert_called_once_with(
            "/organization/v3/directories", self._expected_subject,
            directory_id="683e9dea-5128-471e-8264-6f8f6ba522ab", active=True)

    def test_update_directory_denial_context_inquiry_enabled(self):
        self._organization_client.update_directory(
            "683e9dea-5128-471e-8264-6f8f6ba522ab",
            denial_context_inquiry_enabled=True)
        self._transport.patch.assert_called_once_with(
            "/organization/v3/directories", self._expected_subject,
            directory_id="683e9dea-5128-471e-8264-6f8f6ba522ab",
            denial_context_inquiry_enabled=True)

    def test_update_directory_all(self):
        self._organization_client.update_directory(
            "683e9dea-5128-471e-8264-6f8f6ba522ab", ios_p12=b'An iOS P12',
            android_key="465e74df-13a0-4049-8f31-a9715cb8c12b", active=True,
            denial_context_inquiry_enabled=False)
        self._transport.patch.assert_called_once_with(
            "/organization/v3/directories", self._expected_subject,
            directory_id="683e9dea-5128-471e-8264-6f8f6ba522ab",
            ios_p12=encodestring(b'An iOS P12').decode('utf-8'),
            android_key="465e74df-13a0-4049-8f31-a9715cb8c12b",
            active=True, denial_context_inquiry_enabled=False)

    def test_update_directory_invalid_params(self):
        self._transport.patch.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._organization_client.update_directory(ANY)

    def test_add_directory_public_key_success(self):
        self._response.data = {"key_id": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz"}
        key_id = self._organization_client.add_directory_public_key(
            "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key")
        self._transport.post.assert_called_once_with(
            "/organization/v3/directory/keys", self._expected_subject,
            directory_id="5e49fc4c-ddcb-48db-8473-a5f996b85fbc",
            public_key="public-key")
        self.assertEqual(key_id, "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")

    def test_add_directory_public_key_expires(self):
        self._response.data = {"key_id": ANY}
        self._organization_client.add_directory_public_key(
            "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key",
            expires=datetime(year=2017, month=10, day=3, hour=22,
                             minute=50, second=15))
        self._transport.post.assert_called_once_with(
            "/organization/v3/directory/keys", self._expected_subject,
            directory_id="5e49fc4c-ddcb-48db-8473-a5f996b85fbc",
            public_key="public-key", date_expires="2017-10-03T22:50:15Z")

    def test_add_directory_public_key_active(self):
        self._response.data = {"key_id": ANY}
        self._organization_client.add_directory_public_key(
            "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key", active=True)
        self._transport.post.assert_called_once_with(
            "/organization/v3/directory/keys", self._expected_subject,
            directory_id="5e49fc4c-ddcb-48db-8473-a5f996b85fbc",
            public_key="public-key", active=True)

    def test_add_directory_public_key_all(self):
        self._response.data = {"key_id": ANY}
        self._organization_client.add_directory_public_key(
            "5e49fc4c-ddcb-48db-8473-a5f996b85fbc", "public-key",
            expires=datetime(year=2017, month=10, day=3, hour=22,
                             minute=50, second=15),
            active=True)
        self._transport.post.assert_called_once_with(
            "/organization/v3/directory/keys", self._expected_subject,
            directory_id="5e49fc4c-ddcb-48db-8473-a5f996b85fbc",
            public_key="public-key", date_expires="2017-10-03T22:50:15Z",
            active=True)

    def test_add_directory_public_key_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._organization_client.add_directory_public_key(ANY, ANY)

    def test_add_directory_public_key_invalid_public_key(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "KEY-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidPublicKey):
            self._organization_client.add_directory_public_key(ANY, ANY)

    def test_add_directory_public_key_invalid_key_already_in_use(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "KEY-002", "error_detail": ""}, 400)
        with self.assertRaises(PublicKeyAlreadyInUse):
            self._organization_client.add_directory_public_key(ANY, ANY)

    def test_add_directory_public_key_forbidden(self):
        self._transport.post.side_effect = LaunchKeyAPIException({}, 403)
        with self.assertRaises(Forbidden):
            self._organization_client.add_directory_public_key(ANY, ANY)

    @data(True, False)
    def test_get_directory_public_keys(self, active):
        self._response.data = [
            {
                "id": "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
                "active": active,
                "date_created": "2017-10-03T22:50:15Z",
                "date_expires": "2018-10-03T22:50:15Z",
                "public_key": "A Public Key"
            }
        ]
        public_keys = self._organization_client.get_directory_public_keys(
            "a08eab76-4094-4d60-aca1-30efbab3179b")
        self._transport.post.assert_called_once_with(
            "/organization/v3/directory/keys/list", self._expected_subject,
            directory_id="a08eab76-4094-4d60-aca1-30efbab3179b")
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
            self._organization_client.get_directory_public_keys(ANY)

    def test_get_service_public_keys_forbidden(self):
        self._transport.post.side_effect = LaunchKeyAPIException({}, 403)
        with self.assertRaises(Forbidden):
            self._organization_client.get_directory_public_keys(ANY)

    def test_remove_directory_public_key_success(self):
        self._organization_client.remove_directory_public_key(
            "a08eab76-4094-4d60-aca1-30efbab3179b", "key-id")
        self._transport.delete.assert_called_once_with(
            "/organization/v3/directory/keys", self._expected_subject,
            directory_id="a08eab76-4094-4d60-aca1-30efbab3179b",
            key_id="key-id")

    def test_remove_directory_invalid_params(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._organization_client.remove_directory_public_key(ANY, ANY)

    def test_remove_directory_last_remaining_key(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "KEY-004", "error_detail": ""}, 400)
        with self.assertRaises(LastRemainingKey):
            self._organization_client.remove_directory_public_key(ANY, ANY)

    def test_remove_directory_public_key_public_key_does_not_exist(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "KEY-003", "error_detail": ""},
                                                                   400)
        with self.assertRaises(PublicKeyDoesNotExist):
            self._organization_client.remove_directory_public_key(ANY, ANY)

    def test_remove_directory_public_key_public_key_forbidden(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({}, 403)
        with self.assertRaises(Forbidden):
            self._organization_client.remove_directory_public_key(ANY, ANY)

    def test_update_directory_public_key(self):
        self._organization_client.update_directory_public_key(
            "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
            "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")
        self._transport.patch.assert_called_once_with(
            "/organization/v3/directory/keys", self._expected_subject,
            directory_id="1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
            key_id="ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz")

    def test_update_directory_public_key_expires(self):
        self._organization_client.update_directory_public_key(
            "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
            "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
            expires=datetime(year=2017, month=10, day=3, hour=22,
                             minute=50, second=15))
        self._transport.patch.assert_called_once_with(
            "/organization/v3/directory/keys", self._expected_subject,
            directory_id="1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
            key_id="ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
            date_expires="2017-10-03T22:50:15Z")

    def test_update_directory_public_key_active(self):
        self._organization_client.update_directory_public_key(
            "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
            "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz", active=True)
        self._transport.patch.assert_called_once_with(
            "/organization/v3/directory/keys", self._expected_subject,
            directory_id="1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
            key_id="ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz", active=True)

    def test_update_directory_public_key_all(self):
        self._organization_client.update_directory_public_key(
            "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
            "ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
            expires=datetime(year=2017, month=10, day=3, hour=22,
                             minute=50, second=15),
            active=True)
        self._transport.patch.assert_called_once_with(
            "/organization/v3/directory/keys", self._expected_subject,
            directory_id="1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
            key_id="ab:cd:ef:gh:ij:kl:mn:op:qr:st:uv:wx:yz",
            date_expires="2017-10-03T22:50:15Z", active=True)

    def test_update_directory_public_key_public_key_invalid_params(self):
        self._transport.patch.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._organization_client.update_service_public_key(ANY, ANY)

    def test_update_directory_public_key_public_key_does_not_exist(self):
        self._transport.patch.side_effect = LaunchKeyAPIException({"error_code": "KEY-003", "error_detail": ""}, 400)
        with self.assertRaises(PublicKeyDoesNotExist):
            self._organization_client.update_service_public_key(ANY, ANY)

    def test_update_directory_public_key_forbidden(self):
        self._transport.patch.side_effect = LaunchKeyAPIException({}, 403)
        with self.assertRaises(Forbidden):
            self._organization_client.update_service_public_key(ANY, ANY)

    def test_generate_and_add_directory_sdk_key_success(self):
        self._response.data = {
            "sdk_key": "249b1df4-91f2-42e9-9599-da48f982404e"}
        sdk_key = self._organization_client.generate_and_add_directory_sdk_key(
            "b4ce1d35-63e3-4bd3-affc-dd073d391107"
        )
        self._transport.post.assert_called_once_with(
            "/organization/v3/directory/sdk-keys", self._expected_subject,
            directory_id="b4ce1d35-63e3-4bd3-affc-dd073d391107")
        self.assertEqual(sdk_key, "249b1df4-91f2-42e9-9599-da48f982404e")

    def test_generate_and_add_directory_sdk_key_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._organization_client.generate_and_add_directory_sdk_key(ANY)

    def test_remove_directory_sdk_key_success(self):
        self._organization_client.remove_directory_sdk_key(
            "1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
            "249b1df4-91f2-42e9-9599-da48f982404e")
        self._transport.delete.assert_called_once_with(
            "/organization/v3/directory/sdk-keys", self._expected_subject,
            directory_id="1fa129ee-bb63-4705-a8cb-1c5be8000a0e",
            sdk_key="249b1df4-91f2-42e9-9599-da48f982404e"
        )

    def test_remove_directory_sdk_key_invalid_params(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._organization_client.remove_directory_sdk_key(ANY, ANY)

    def test_remove_directory_sdk_key_last_remaining_sdk_key(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ORG-005", "error_detail": ""}, 400)
        with self.assertRaises(LastRemainingSDKKey):
            self._organization_client.remove_directory_sdk_key(ANY, ANY)

    def test_remove_directory_sdk_key_invalid_sdk_key(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ORG-006", "error_detail": ""}, 400)
        with self.assertRaises(InvalidSDKKey):
            self._organization_client.remove_directory_sdk_key(ANY, ANY)

    def test_get_all_directory_sdk_keys_transport_params(self):
        self._organization_client.get_all_directory_sdk_keys(
            "1fa129ee-bb63-4705-a8cb-1c5be8000a0e")
        self._transport.post.assert_called_once_with(
            "/organization/v3/directory/sdk-keys/list", self._expected_subject,
            directory_id="1fa129ee-bb63-4705-a8cb-1c5be8000a0e"
        )

    def test_get_all_directory_sdk_keys_return_value(self):
        result = self._organization_client.get_all_directory_sdk_keys(
            "1fa129ee-bb63-4705-a8cb-1c5be8000a0e")
        self.assertEqual(
            result,
            self._transport.post.return_value.data
        )

    def test_get_all_directory_sdk_keys_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException(
            {"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._organization_client.get_all_directory_sdk_keys(
                "1fa129ee-bb63-4705-a8cb-1c5be8000a0e")

    def test_get_all_directory_sdk_keys_entity_not_found(self):
        self._transport.post.side_effect = LaunchKeyAPIException(
            {}, 404)
        with self.assertRaises(EntityNotFound):
            self._organization_client.get_all_directory_sdk_keys(
                "1fa129ee-bb63-4705-a8cb-1c5be8000a0e")
