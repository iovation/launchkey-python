import unittest
from mock import MagicMock, ANY
from uuid import uuid4
from launchkey.clients import DirectoryClient
from launchkey.clients.directory import DeviceStatus
from launchkey.exceptions import LaunchKeyAPIException, InvalidParameters, InvalidDirectoryIdentifier, EntityNotFound, \
    UnexpectedAPIResponse, InvalidDeviceStatus
from launchkey.transports.base import APIResponse
import six


class TestDirectoryClient(unittest.TestCase):

    def setUp(self):
        self._transport = MagicMock()
        self._response = APIResponse({}, {}, 200)
        self._transport.post.return_value = self._response
        self._transport.get.return_value = self._response
        self._transport.put.return_value = self._response
        self._transport.delete.return_value = self._response
        self._directory_client = DirectoryClient(uuid4(), self._transport)

    def test_link_device_success(self):
        self._response.data = {"qrcode": ANY, "code": "abcdefg"}
        self._directory_client.link_device(ANY)

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
        result = self._directory_client.get_linked_devices(ANY)
        self.assertEqual(len(result), 3)

    def test_get_linked_devices_status(self):
        for key, map in six.iteritems(DeviceStatus._status_map):
            self._response.data = [{"id": ANY, "name": ANY, "status": key, "type": ANY}]
            device = self._directory_client.get_linked_devices(ANY)[0]
            self.assertEqual(device.status.status_code, map[0])
            self.assertEqual(device.status.is_active, map[1])

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

    def test_unlink_device_success(self):
        self._directory_client.unlink_device(ANY, ANY)

    def test_unlink_device_invalid_params(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._directory_client.unlink_device(ANY, ANY)

    def test_unlink_device_entity_not_found(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({}, 404)
        with self.assertRaises(EntityNotFound):
            self._directory_client.unlink_device(ANY, ANY)

    def test_end_all_service_sessions_success(self):
        self._directory_client.end_all_service_sessions(ANY)

    def test_end_all_service_sessions_invalid_params(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({"error_code": "ARG-001", "error_detail": ""}, 400)
        with self.assertRaises(InvalidParameters):
            self._directory_client.end_all_service_sessions(ANY)

    def test_end_all_service_sessions_entity_not_found(self):
        self._transport.delete.side_effect = LaunchKeyAPIException({}, 404)
        with self.assertRaises(EntityNotFound):
            self._directory_client.end_all_service_sessions(ANY)
