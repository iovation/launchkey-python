import unittest
from datetime import datetime
from json import dumps
from uuid import uuid4

import pytz
import six
from mock import MagicMock, ANY, patch

from launchkey.clients import DirectoryClient
from launchkey.clients.directory import Session, DirectoryUserTOTP
from launchkey.entities.directory import DeviceLinkCompletionResponse
from launchkey.entities.directory import DeviceStatus
from launchkey.exceptions import LaunchKeyAPIException, InvalidParameters, \
    InvalidDirectoryIdentifier, EntityNotFound, \
    UnexpectedAPIResponse, InvalidDeviceStatus, UnexpectedWebhookRequest, \
    XiovJWTValidationFailure, XiovJWTDecryptionFailure, \
    UnableToDecryptWebhookRequest
from launchkey.transports import JOSETransport
from launchkey.transports.base import APIResponse
from .shared import SharedTests


class TestDirectoryClientServices(SharedTests.Services):

    def setUp(self):
        self._directory_id = uuid4()
        client = DirectoryClient(self._directory_id , MagicMock())
        self._expected_base_endpoint = '/directory/v3/services'
        self._expected_subject = 'dir:{}'.format(str(self._directory_id))
        self.setup_client(client)


class TestDirectoryClient(unittest.TestCase):

    def setUp(self):
        self._transport = MagicMock()
        self._response = APIResponse({}, {}, 200)
        self._transport.post.return_value = self._response
        self._transport.get.return_value = self._response
        self._transport.put.return_value = self._response
        self._transport.delete.return_value = self._response
        self._transport.patch.return_value = self._response
        self._directory_id = uuid4()
        self._expected_subject = 'dir:{}'.format(str(self._directory_id))
        self._directory_client = DirectoryClient(self._directory_id,
                                                 self._transport)

    def test_link_device_success(self):
        self._response.data = {"qrcode": ANY, "code": "abcdefg",
                               "device_id": ANY}
        expected_identifier = "user_id"
        self._directory_client.link_device(expected_identifier[:])
        self._transport.post.assert_called_once_with(
            "/directory/v3/devices", self._expected_subject,
            identifier=expected_identifier)

    def test_link_device_with_ttl_includes_kwarg_to_transport(self):
        self._response.data = {"qrcode": ANY, "code": "abcdefg",
                               "device_id": ANY}
        expected_identifier = "user_id"
        expected_ttl = 123
        self._directory_client.link_device(expected_identifier[:],
                                           ttl=expected_ttl)
        self._transport.post.assert_called_once_with(
            "/directory/v3/devices", self._expected_subject,
            identifier=expected_identifier, ttl=123)

    def test_link_device_unexpected_result(self):
        self._response.data = {MagicMock(), MagicMock()}
        with self.assertRaises(UnexpectedAPIResponse):
            self._directory_client.link_device(ANY)

    def test_link_device_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._directory_client.link_device(ANY)

    def test_link_device_invalid_directory_identifier(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "DIR-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidDirectoryIdentifier):
            self._directory_client.link_device(ANY)

    def test_get_linked_devices_list_success(self):
        self._response.data = [
            {"id": ANY, "name": ANY, "status": 0, "type": ANY},
            {"id": ANY, "name": ANY, "status": 1, "type": ANY},
            {"id": ANY, "name": ANY, "status": 2, "type": ANY}
        ]
        expected_identifier = "user_id"
        result = self._directory_client.get_linked_devices(
            expected_identifier[:])
        self.assertEqual(len(result), 3)
        self._transport.post.assert_called_once_with(
            "/directory/v3/devices/list", self._expected_subject,
            identifier=expected_identifier
        )

    def test_get_linked_devices_status(self):
        for key, value in six.iteritems(DeviceStatus._status_map):
            self._response.data = [{"id": ANY, "name": ANY, "status": key, "type": ANY}]
            device = self._directory_client.get_linked_devices(ANY)[0]
            self.assertEqual(device.status.status_code, value[0])
            self.assertEqual(device.status.is_active, value[1])

    def test_get_linked_devices_invalid_status_code(self):
        self._response.data = [{"id": ANY, "name": ANY, "status": ANY, "type": ANY}]
        with self.assertRaises(InvalidDeviceStatus):
            self._directory_client.get_linked_devices(ANY)

    def test_get_linked_devices_empty_success(self):
        self._response.data = []
        self.assertEqual(self._directory_client.get_linked_devices(ANY), [])

    def test_get_linked_devices_unexpected_result(self):
        self._response.data = [MagicMock()]
        with self.assertRaises(UnexpectedAPIResponse):
            self._directory_client.get_linked_devices(ANY)

    def test_get_linked_devices_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._directory_client.get_linked_devices(ANY)

    def test_get_linked_devices_calls_transport_correctly(self):
        expected_identifier = "user_id"
        expected_subject = 'dir:{}'.format(str(self._directory_id))
        self._directory_client.get_linked_devices(expected_identifier[:])
        self._transport.post.assert_called_once_with(
            "/directory/v3/devices/list", expected_subject, identifier=expected_identifier)

    def test_unlink_device_success(self):
        self._directory_client.unlink_device("user-id", "device-id")
        self._transport.delete.assert_called_once_with(
            "/directory/v3/devices", self._expected_subject,
            identifier="user-id", device_id="device-id")

    def test_unlink_device_invalid_params(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._directory_client.unlink_device(ANY, ANY)

    def test_unlink_device_entity_not_found(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({}, 404)
        with self.assertRaises(EntityNotFound):
            self._directory_client.unlink_device(ANY, ANY)

    def test_end_all_service_sessions_success(self):
        self._directory_client.end_all_service_sessions("user_id")
        self._transport.delete.assert_called_once_with(
            "/directory/v3/sessions", self._expected_subject,
            identifier="user_id")

    def test_end_all_service_sessions_invalid_params(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._directory_client.end_all_service_sessions(ANY)

    def test_end_all_service_sessions_entity_not_found(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({}, 404)
        with self.assertRaises(EntityNotFound):
            self._directory_client.end_all_service_sessions(ANY)

    def test_get_all_service_sessions_success(self):
        self._response.data = [
            {
                "auth_request": "cf6a29b9-e807-4a13-a2d7-88b6b89673bc",
                "date_created": "2017-10-03T22:50:15Z",
                "service_icon": "https://image.location.com/abc.png",
                "service_id": "e743e23d-e2cb-4191-a905-cd23cfd0cefe",
                "service_name": "atestservice"
            }
        ]
        response = self._directory_client.get_all_service_sessions("user_id")
        self._transport.post.assert_called_once_with(
            "/directory/v3/sessions/list", self._expected_subject,
            identifier="user_id")

        self.assertEqual(len(response), 1)
        session = response[0]
        self.assertIsInstance(session, Session)
        self.assertEqual(session.auth_request,
                         "cf6a29b9-e807-4a13-a2d7-88b6b89673bc")
        self.assertEqual(session.service_id,
                         "e743e23d-e2cb-4191-a905-cd23cfd0cefe")
        self.assertEqual(session.service_icon,
                         "https://image.location.com/abc.png")
        self.assertEqual(session.service_name, "atestservice")
        self.assertEqual(session.created,
                         datetime(year=2017, month=10, day=3, hour=22,
                                  minute=50, second=15,
                                  tzinfo=pytz.timezone("UTC")))

    def test_get_all_service_sessions_invalid_params(self):
        self._transport.post.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._directory_client.get_all_service_sessions(ANY)

    def test_generate_user_totp_transport_call(self):
        self._response.data = {
            "algorithm": "SHA1",
            "digits": 6,
            "period": 30,
            "secret": "abcdefghijklmnop"
        }
        self._directory_client.generate_user_totp("expected user id")
        self._transport.post.assert_called_once_with(
            "/directory/v3/totp",
            self._expected_subject,
            identifier="expected user id"
        )

    def test_generate_user_totp_return_object(self):
        self._response.data = {
            "algorithm": "SHA256",
            "digits": 8,
            "period": 60,
            "secret": "qrstuvwxyz"
        }
        return_data = self._directory_client.generate_user_totp(
            "expected user id")
        self.assertIsInstance(return_data, DirectoryUserTOTP)
        self.assertEqual("SHA256", return_data.algorithm)
        self.assertEqual(8, return_data.digits)
        self.assertEqual(60, return_data.period)
        self.assertEqual("qrstuvwxyz", return_data.secret)

    def test_remove_user_totp_transport_call(self):
        self._directory_client.remove_user_totp("expected user id")
        self._transport.delete.assert_called_once_with(
            "/directory/v3/totp",
            self._expected_subject,
            identifier="expected user id"
        )

    def test_remove_user_totp_return_object(self):
        return_data = self._directory_client.remove_user_totp(
            "expected user id")
        self.assertIsNone(return_data)


class TestHandleWebhook(unittest.TestCase):

    def setUp(self):
        patcher = patch("launchkey.clients.directory.XiovJWTService")
        self._x_iov_jwt_service_patch = patcher.start().return_value
        self._x_iov_jwt_service_patch.decrypt_jwe.return_value = dumps(
            {
                "type": "DEVICE_LINK_COMPLETION",
                "device_public_key": "public key",
                "device_public_key_id": "public key id",
                "device_id": "device id"
            }
        )
        self.addCleanup(patcher.stop)

        self._directory_id = uuid4()
        self._transport = MagicMock(spec=JOSETransport)
        self._headers = {"X-IOV-JWT": "jwt", "Other Header": "jwt"}
        self.client = DirectoryClient(self._directory_id, self._transport)

    def test_x_iov_jwt_validation_failure_raises_unexpected_webhook_request(self):
        self._x_iov_jwt_service_patch.decrypt_jwe.side_effect = XiovJWTValidationFailure
        with self.assertRaises(UnexpectedWebhookRequest):
            self.client.handle_webhook("body", self._headers, "method", "path")

    @patch("launchkey.clients.directory.warnings")
    def test_invalid_webhook_payload_causes_warning(self, warnings_patch):
        self._x_iov_jwt_service_patch.decrypt_jwe.return_value = dumps(
            {
                "type": "UNKNOWN_WEBHOOK_TYPE",
                "device_public_key": "public key",
                "device_public_key_id": "public key id",
                "device_id": "device id"
            }
        )
        self.client.handle_webhook("body", self._headers, "method", "path")
        warnings_patch.warn.assert_called_with(
            "Invalid Directory Webhook received. There may be an update "
            "available to add support."
        )

    def test_x_iov_jwt_decryption_failure_raises_unable_to_decrypt_webhook_request(self):
        self._x_iov_jwt_service_patch.decrypt_jwe.side_effect = XiovJWTDecryptionFailure
        with self.assertRaises(UnableToDecryptWebhookRequest):
            self.client.handle_webhook("body", self._headers, "method", "path")

    def test_decrypt_jwe_params(self):
        self.client.handle_webhook("body", self._headers, "method", "path")
        self._x_iov_jwt_service_patch.decrypt_jwe.assert_called_with(
            "body",
            self._headers,
            "method",
            "path"
        )

    def test_returns_directory_user_device_link_completion_webhook_package(self):
        returned = self.client.handle_webhook("body", self._headers, "method", "path")
        self.assertIsInstance(returned, DeviceLinkCompletionResponse)
        self.assertEqual(returned.device_id, 'device id')
        self.assertEqual(returned.device_public_key, 'public key')
        self.assertEqual(returned.device_public_key_id, 'public key id')
