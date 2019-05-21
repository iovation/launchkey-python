import unittest

from launchkey.entities.directory import Directory, DeviceStatus, Device


class TestDirectoryEntity(unittest.TestCase):

    def test_input_attributes(self):
        directory = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )
        self.assertEqual(directory.service_ids,
                         ['740c36bd-43cb-4238-8f4b-a75307c5ef62'])
        self.assertEqual(directory.sdk_keys,
                         ["7acf6dc0-8db8-40e4-8045-2a73471adc58"])
        self.assertTrue(directory.premium)
        self.assertEqual(directory.name, "Directory Name")
        self.assertEqual(directory.android_key, "A Key")
        self.assertEqual(directory.ios_certificate_fingerprint,
                         "A Fingerprint")
        self.assertTrue(directory.active)
        self.assertEqual(directory.id, "d36f81de-7683-48aa-b3cb-d4c6bffef3c5")
        self.assertTrue(directory.denial_context_inquiry_enabled)

    def test_equal_directories(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        self.assertTrue(directory_1 == directory_2)

    def test_different_service_ids(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef61'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        self.assertFalse(directory_1 == directory_2)

    def test_different_sdk_keys(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc57"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        self.assertFalse(directory_1 == directory_2)

    def test_different_premium(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": False,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        self.assertFalse(directory_1 == directory_2)

    def test_different_name(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name 2",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        self.assertFalse(directory_1 == directory_2)

    def test_different_android_key(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "Another Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        self.assertFalse(directory_1 == directory_2)

    def test_different_ios_cert_fingerprint(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "Another Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        self.assertFalse(directory_1 == directory_2)

    def test_different_active(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": False,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        self.assertFalse(directory_1 == directory_2)

    def test_different_id(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c4",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        self.assertFalse(directory_1 == directory_2)

    def test_different_denial_context_inquery_enabled(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": False,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        self.assertFalse(directory_1 == directory_2)

    def test_different_webhook_url(self):
        directory_1 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        directory_2 = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": False,
                "webhook_url": "https://my.webhook.url/otherpath"
            }
        )

        self.assertFalse(directory_1 == directory_2)

    def test_different_type(self):
        directory = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )

        not_directory = {
            "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
            "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
            "premium": True,
            "name": "Directory Name",
            "android_key": "A Key",
            "ios_certificate_fingerprint": "A Fingerprint",
            "active": True,
            "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
            "denial_context_inquiry_enabled": False,
            "webhook_url": "https://my.webhook.url/path"
        }

        self.assertFalse(directory == not_directory)

    def test_repr(self):
        directory = Directory(
            {
                "service_ids": ['740c36bd-43cb-4238-8f4b-a75307c5ef62'],
                "sdk_keys": ["7acf6dc0-8db8-40e4-8045-2a73471adc58"],
                "premium": True,
                "name": "Directory Name",
                "android_key": "A Key",
                "ios_certificate_fingerprint": "A Fingerprint",
                "active": True,
                "id": "d36f81de-7683-48aa-b3cb-d4c6bffef3c5",
                "denial_context_inquiry_enabled": True,
                "webhook_url": "https://my.webhook.url/path"
            }
        )
        self.assertEqual(
            str(directory),
            'Directory <id="d36f81de-7683-48aa-b3cb-d4c6bffef3c5", '
            'name="Directory Name", '
            'service_ids=[\'740c36bd-43cb-4238-8f4b-a75307c5ef62\'], '
            'sdk_keys=[\'7acf6dc0-8db8-40e4-8045-2a73471adc58\'], '
            'premium=True, ios_certificate_fingerprint="A Fingerprint", '
            'active=True, denial_context_inquiry_enabled=True, '
            'webhook_url="https://my.webhook.url/path">'
        )


class TestDeviceEntity(unittest.TestCase):
    def test_device_repr(self):
        device = Device(
            {
                "id": '740c36bd-43cb-4238-8f4b-a75307c5ef62',
                "name": "A Device",
                "status": 1,
                "type": "Android"
            }
        )
        self.assertEqual(
            str(device),
            'Device <id="740c36bd-43cb-4238-8f4b-a75307c5ef62", '
            'name="A Device", status=DeviceStatus <status_code="LINKED", '
            'is_active=True>, type="Android">'
        )


class TestDeviceStatusEntity(unittest.TestCase):
    def test_0(self):
        status = DeviceStatus(0)
        self.assertEqual(status.status_code, "LINK_PENDING")
        self.assertFalse(status.is_active)

    def test_device_repr_0(self):
        device = DeviceStatus(0)
        self.assertEqual(
            str(device),
            'DeviceStatus <status_code="LINK_PENDING", is_active=False>'
        )

    def test_1(self):
        status = DeviceStatus(1)
        self.assertEqual(status.status_code, "LINKED")
        self.assertTrue(status.is_active)

    def test_device_repr_1(self):
        device = DeviceStatus(1)
        self.assertEqual(
            str(device),
            'DeviceStatus <status_code="LINKED", is_active=True>'
        )

    def test_2(self):
        status = DeviceStatus(2)
        self.assertEqual(status.status_code, "UNLINK_PENDING")
        self.assertTrue(status.is_active)

    def test_device_repr_2(self):
        device = DeviceStatus(2)
        self.assertEqual(
            str(device),
            'DeviceStatus <status_code="UNLINK_PENDING", is_active=True>'
        )
