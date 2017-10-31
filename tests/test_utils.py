import unittest
from launchkey.utils import iso_format, UUIDHelper
from launchkey.entities.validation import ValidateISODate
from ddt import ddt, data
from formencode import Invalid
from datetime import datetime
import pytz
from uuid import UUID
from launchkey.exceptions import InvalidIssuerVersion, InvalidIssuerFormat


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
