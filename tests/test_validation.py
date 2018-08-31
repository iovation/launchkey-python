from unittest import TestCase

from formencode import Invalid

from launchkey.entities.validation import AuthorizeValidator


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
