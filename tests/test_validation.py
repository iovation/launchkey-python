from unittest import TestCase
from datetime import datetime

from dateutil.tz import tzutc
from formencode import Invalid
from ddt import data, ddt

from launchkey.entities.validation import AuthorizeValidator
from launchkey.exceptions.validation import AuthorizationInProgressValidator


class TestAuthorizeValidator(TestCase):

    def setUp(self):
        self._data = {
            'auth_request': 'Expected Auth Request',
            'push_package': 'Expected Push Package'
        }
        self._validator = AuthorizeValidator()

    def test_no_auth_request_fails(self):
        del self._data['auth_request']
        with self.assertRaises(Invalid):
            self._validator.to_python(self._data)

    def test_none_auth_request_fails(self):
        self._data['auth_request'] = None
        with self.assertRaises(Invalid):
            self._validator.to_python(self._data)

    def test_empty_auth_request_fails(self):
        self._data['auth_request'] = ''
        with self.assertRaises(Invalid):
            self._validator.to_python(self._data)

    def test_auth_request_returns_unchanged_string(self):
        expected = self._data.copy()
        actual = self._validator.to_python(self._data)
        self.assertEqual(actual, expected)

    def test_no_push_package_is_none(self):
        del self._data['push_package']
        actual = self._validator.to_python(self._data)
        self.assertIn('push_package', actual)
        self.assertEqual(actual['push_package'], None)

    def test_none_push_package_fails(self):
        self._data['push_package'] = None
        with self.assertRaises(Invalid):
            self._validator.to_python(self._data)

    def test_empty_push_package_fails(self):
        self._data['push_package'] = ''
        with self.assertRaises(Invalid):
            self._validator.to_python(self._data)

    def test_push_package_returns_unchanged_string(self):
        expected = self._data['push_package'] = "Expected Push Package"
        actual = self._validator.to_python(self._data)
        self.assertIn('push_package', actual)
        self.assertEqual(actual['push_package'], expected)


@ddt
class TestAuthorizationInProgressValidator(TestCase):

    def setUp(self):
        self.data = {
            "auth_request": "d57c6e0a-f436-11e8-ae2a-acde48001122",
            "expires": "2018-11-28T22:04:44Z",
            "from_same_service": True
        }

    @data("0856e7cf-f437-11e8-9872-acde48001122", "Auth Request")
    def test_auth_request_valid(self, auth_request):
        self.data['auth_request'] = auth_request
        parsed = AuthorizationInProgressValidator().to_python(self.data)
        self.assertEqual(
            parsed['auth_request'],
            auth_request
        )

    def test_auth_request_missing(self):
        del self.data['auth_request']
        with self.assertRaises(Invalid):
            AuthorizationInProgressValidator().to_python(self.data)

    @data("0856e7cf-f437-11e8-9872-acde48001122", "Auth Request")
    def test_auth_request_valid(self, auth_request):
        self.data['auth_request'] = auth_request
        parsed = AuthorizationInProgressValidator().to_python(self.data)
        self.assertEqual(
            parsed['auth_request'],
            auth_request
        )

    def test_from_same_service_missing(self):
        del self.data['from_same_service']
        parsed = AuthorizationInProgressValidator().to_python(self.data)
        self.assertFalse(parsed['from_same_service'])

    @data(True, False)
    def test_from_same_service_valid(self, from_same_service):
        self.data['from_same_service'] = from_same_service
        parsed = AuthorizationInProgressValidator().to_python(self.data)
        self.assertEqual(
            parsed['from_same_service'],
            from_same_service
        )

    def test_expires(self):
        self.data['expires'] = "2018-11-28T22:04:44Z"
        parsed = AuthorizationInProgressValidator().to_python(self.data)
        self.assertEqual(
            parsed['expires'],
            datetime(2018, 11, 28, 22, 4, 44, tzinfo=tzutc())
        )
