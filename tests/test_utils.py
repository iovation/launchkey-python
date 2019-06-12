import unittest
from datetime import datetime
from uuid import UUID

from mock import MagicMock, patch
from ddt import ddt, data
from formencode import Invalid
from jwkest import JWKESTException
import pytz

from launchkey.exceptions import InvalidIssuerVersion, InvalidIssuerFormat, WebhookAuthorizationError, JWTValidationFailure, XiovJWTValidationFailure, InvalidJWTResponse, XiovJWTDecryptionFailure
from launchkey.utils.shared import iso_format, UUIDHelper, XiovJWTService
from launchkey.entities.validation import ValidateISODate
from launchkey.transports import JOSETransport


class TestXiovJwtService(unittest.TestCase):

    def setUp(self):
        self._transport = MagicMock(spec=JOSETransport)
        self.x_iov_jwt_service = XiovJWTService(self._transport, "subject")
        self._headers = {"X-IOV-JWT": "jwt", "Other Header": "jwt"}

    def test_verify_jwt_request_returns_body_on_success(self):
        response = self.x_iov_jwt_service.verify_jwt_request(
            "body", self._headers, "method", "path"
        )
        self.assertEqual(response, "body")

    def test_verify_jwt_request_returns_decoded_body_when_given_as_bytes(self):
        response = self.x_iov_jwt_service.verify_jwt_request(
            b"body", self._headers, "method", "path"
        )
        self.assertEqual(response, u"body")

    def test_verify_jwt_missing_x_iov_jwt_raises_webhook_authorization_error(self):
        with self.assertRaises(WebhookAuthorizationError):
            self.x_iov_jwt_service.verify_jwt_request(
                "body", {}, "method", "path"
            )

    def test_transport_verify_jwt_request_called_with_correct_params(self):
        self.x_iov_jwt_service.verify_jwt_request(
            "body", self._headers, "method", "path"
        )
        self._transport.verify_jwt_request.assert_called_with(
            "jwt", "subject", "method", "path", "body"
        )

    def test_transport_verify_jwt_request_jwt_validation_failure_raises_x_iov_jwt_validation_failure(self):
        self._transport.verify_jwt_request.side_effect = JWTValidationFailure
        with self.assertRaises(XiovJWTValidationFailure):
            self.x_iov_jwt_service.verify_jwt_request(
                "body", self._headers, "method", "path"
            )

    def test_transport_verify_jwt_request_invalid_jwt_response_raises_x_iov_jwt_validation_failure(self):
        self._transport.verify_jwt_request.side_effect = InvalidJWTResponse
        with self.assertRaises(XiovJWTValidationFailure):
            self.x_iov_jwt_service.verify_jwt_request(
                "body", self._headers, "method", "path"
            )

    def test_decrypt_jwe_calls_verify_jwt_request(self):
        patched = patch.object(self.x_iov_jwt_service, 'verify_jwt_request')
        verify_jwt_request_patch = patched.start()
        self.addCleanup(patched.stop)

        self.x_iov_jwt_service.decrypt_jwe(
            "body", self._headers, "method", "path"
        )
        verify_jwt_request_patch.assert_called_with(
            "body", self._headers, "method", "path"
        )

    def test_decrypt_jwe_transport_decrtypt_response_params(self):
        patched = patch.object(self.x_iov_jwt_service, 'verify_jwt_request')
        verify_jwt_request_patch = patched.start()
        self.addCleanup(patched.stop)

        self.x_iov_jwt_service.decrypt_jwe(
            "body", self._headers, "method", "path"
        )
        self._transport.decrypt_response.assert_called_with(
            verify_jwt_request_patch.return_value
        )

    def test_decrypt_jwe_jwekest_exception_raises_x_iov_jwt_decryption_failure(self):
        self._transport.decrypt_response.side_effect = JWKESTException
        with self.assertRaises(XiovJWTDecryptionFailure):
            self.x_iov_jwt_service.decrypt_jwe(
                "body", self._headers, "method", "path"
            )


@ddt
class TestISODates(unittest.TestCase):

    def test_validate_iso_date_success(self):
        self.assertEqual(
            ValidateISODate.to_python("2017-10-03T22:50:15Z"),
            datetime(year=2017, month=10, day=3, hour=22, minute=50, second=15, tzinfo=pytz.timezone("UTC"))
        )

    def test_validate_iso_date_none(self):
        self.assertIsNone(ValidateISODate().to_python(None))

    @data('Not a date', 'aded3611-ad75-4549-a8ca-fcfacfb41f73')
    def test_invalid_iso_date(self, date):
        with self.assertRaises(Invalid):
            ValidateISODate().to_python(date)

    def test_iso_format_success(self):
        self.assertEqual(
            "2017-10-03T22:50:15Z",
            iso_format(datetime(year=2017, month=10, day=3, hour=22, minute=50, second=15, tzinfo=pytz.timezone("UTC")))
        )

    def test_iso_format_none(self):
        self.assertIsNone(iso_format(None))


@ddt
class TestUUIDHelper(unittest.TestCase):

    @data("425afc1f-ab52-4f41-ade8-eb25252f014", "25afc1f-ab52-4f41-ade8-eb25252f0149", 123456, True, False, None)
    def test_invalid_uuid_from_string(self, value):
        with self.assertRaises(InvalidIssuerFormat):
            UUIDHelper().from_string(value)

    @data("425afc1f-ab52-4f41-ade8-eb25252f014", "25afc1f-ab52-4f41-ade8-eb25252f0149", 123456, True, False, None)
    def test_invalid_uuid_validate_version(self, value):
        with self.assertRaises(InvalidIssuerFormat):
            UUIDHelper().validate_version(value, None)

    @data(UUID("b9817ef3-b389-11e7-aebc-acde48001122"), "b9817ef3-b389-11e7-aebc-acde48001122",  # uuid1
          UUID("5e2a66fc-50d9-315b-818e-c3a324636c28"), "5e2a66fc-50d9-315b-818e-c3a324636c28",  # uuid3
          UUID("22f2ae4e-ae01-4e7a-a097-b34d6a232509"), "22f2ae4e-ae01-4e7a-a097-b34d6a232509",  # uuid4
          UUID("4053bc07-b189-502e-badf-f4d7bebeb322"), "4053bc07-b189-502e-badf-f4d7bebeb322")  # uuid5
    def test_valid_uuid_default(self, value):
        UUIDHelper().from_string(value)

    @data(UUID("b9817ef3-b389-11e7-aebc-acde48001122"), "b9817ef3-b389-11e7-aebc-acde48001122")
    def test_valid_uuid_1(self, value):
        UUIDHelper().from_string(value, 1)

    @data(UUID("5e2a66fc-50d9-315b-818e-c3a324636c28"), "5e2a66fc-50d9-315b-818e-c3a324636c28",  # uuid3
          UUID("22f2ae4e-ae01-4e7a-a097-b34d6a232509"), "22f2ae4e-ae01-4e7a-a097-b34d6a232509",  # uuid4
          UUID("4053bc07-b189-502e-badf-f4d7bebeb322"), "4053bc07-b189-502e-badf-f4d7bebeb322")  # uuid5
    def test_invalid_uuid_1(self, value):
        with self.assertRaises(InvalidIssuerVersion):
            UUIDHelper().from_string(value, 1)

    @data(UUID("5e2a66fc-50d9-315b-818e-c3a324636c28"), "5e2a66fc-50d9-315b-818e-c3a324636c28")
    def test_valid_uuid_3(self, value):
        UUIDHelper().from_string(value, 3)

    @data(UUID("b9817ef3-b389-11e7-aebc-acde48001122"), "b9817ef3-b389-11e7-aebc-acde48001122",  # uuid1
          UUID("22f2ae4e-ae01-4e7a-a097-b34d6a232509"), "22f2ae4e-ae01-4e7a-a097-b34d6a232509",  # uuid4
          UUID("4053bc07-b189-502e-badf-f4d7bebeb322"), "4053bc07-b189-502e-badf-f4d7bebeb322")  # uuid5
    def test_invalid_uuid_3(self, value):
        with self.assertRaises(InvalidIssuerVersion):
            UUIDHelper().from_string(value, 3)

    @data(UUID("22f2ae4e-ae01-4e7a-a097-b34d6a232509"), "22f2ae4e-ae01-4e7a-a097-b34d6a232509")
    def test_valid_uuid_4(self, value):
        UUIDHelper().from_string(value, 4)

    @data(UUID("b9817ef3-b389-11e7-aebc-acde48001122"), "b9817ef3-b389-11e7-aebc-acde48001122",  # uuid1
          UUID("5e2a66fc-50d9-315b-818e-c3a324636c28"), "5e2a66fc-50d9-315b-818e-c3a324636c28",  # uuid3
          UUID("4053bc07-b189-502e-badf-f4d7bebeb322"), "4053bc07-b189-502e-badf-f4d7bebeb322")  # uuid5
    def test_invalid_uuid_4(self, value):
        with self.assertRaises(InvalidIssuerVersion):
            UUIDHelper().from_string(value, 4)

    @data(UUID("4053bc07-b189-502e-badf-f4d7bebeb322"), "4053bc07-b189-502e-badf-f4d7bebeb322")
    def test_valid_uuid_5(self, value):
        UUIDHelper().from_string(value, 5)

    @data(UUID("b9817ef3-b389-11e7-aebc-acde48001122"), "b9817ef3-b389-11e7-aebc-acde48001122",  # uuid1
          UUID("5e2a66fc-50d9-315b-818e-c3a324636c28"), "5e2a66fc-50d9-315b-818e-c3a324636c28",  # uuid3
          UUID("22f2ae4e-ae01-4e7a-a097-b34d6a232509"), "22f2ae4e-ae01-4e7a-a097-b34d6a232509")  # uuid4
    def test_invalid_uuid_5(self, value):
        with self.assertRaises(InvalidIssuerVersion):
            UUIDHelper().from_string(value, 5)
