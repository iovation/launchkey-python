from datetime import datetime
from unittest import TestCase

from dateutil.tz import tzutc
from ddt import data, ddt
from formencode import Invalid
from six import assertRaisesRegex

from launchkey.entities.validation import AuthorizeValidator, ConditionalGeoFenceValidator, PolicyFenceValidator
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


@ddt
class TestPolicyFenceValidator(TestCase):
    def setUp(self):
        self._validator = PolicyFenceValidator()
        self._data = {}

    def test_name_is_optional(self):
        self._data = {
            "type": "TERRITORY",
            "country": "US"
        }
        parsed = self._validator.to_python(self._data)
        self.assertIsNone(parsed["name"])

    @data("United States", "Home Town", "Las Vegas")
    def test_valid_names(self, name):
        self._data = {
            "type": "TERRITORY",
            "country": "US",
            "name": name
        }
        parsed = self._validator.to_python(self._data)
        self.assertEqual(name, parsed["name"])

    @data(None, "")
    def test_invalid_names(self, name):
        self._data = {
            "type": "TERRITORY",
            "country": "US",
            "name": name
        }
        with assertRaisesRegex(self, Invalid, r"^name: Please enter a value$"):
            self._validator.to_python(self._data)

    def test_territory_type(self):
        self._data = {
            "type": "TERRITORY",
            "country": "US"
        }
        parsed = self._validator.to_python(self._data)
        self.assertEqual(
            {
                "type": "TERRITORY",
                "country": "US",
                "name": None,
                "postal_code": None,
                "administrative_area": None
            },
            parsed
        )

    def test_geo_circle_type(self):
        self._data = {
            "type": "GEO_CIRCLE",
            "latitude": 90,
            "longitude": -90,
            "radius": 105
        }
        parsed = self._validator.to_python(self._data)
        self.assertEqual(
            {
                "type": "GEO_CIRCLE",
                "name": None,
                "latitude": 90,
                "longitude": -90,
                "radius": 105
            },
            parsed
        )


class TestConditionalGeoFenceValidator(TestCase):
    def setUp(self):
        self._validator = ConditionalGeoFenceValidator()
        self._data = {}

    def test_embedded_factors_inside_and_outside_factor(self):
        self._data = {
            "type": "COND_GEO",
            "deny_rooted_jailbroken": False,
            "deny_emulator_simulator": False,
            "fences": [
                {
                    "name": "Ontario",
                    "type": "TERRITORY",
                    "country": "CA",
                    "administrative_area": "CA-ON"
                }
            ],
            "inside": {
                "type": "FACTORS",
                "fences": [],
                "factors": ["KNOWLEDGE"]
            },
            "outside": {
                "type": "FACTORS",
                "fences": [],
                "factors": ["POSSESSION"]
            }
        }
        parsed = self._validator().to_python(self._data)
        self.assertEqual(
            self._data,
            parsed
        )

    def test_embedded_amount_inside_and_outside_method(self):
        self._data = {
            "type": "COND_GEO",
            "deny_rooted_jailbroken": False,
            "deny_emulator_simulator": False,
            "fences": [
                {
                    "name": "Ontario",
                    "type": "TERRITORY",
                    "country": "CA",
                    "administrative_area": "CA-ON"
                }
            ],
            "inside": {
                "type": "METHOD_AMOUNT",
                "fences": [],
                "amount": 0
            },
            "outside": {
                "type": "METHOD_AMOUNT",
                "fences": [],
                "amount": 1
            }
        }
        parsed = self._validator().to_python(self._data)
        self.assertEqual(
            self._data,
            parsed
        )

    def test_stacked_conditional_geo_policy(self):
        self._data = {
            "type": "COND_GEO",
            "deny_rooted_jailbroken": False,
            "deny_emulator_simulator": False,
            "fences": [
                {
                    "name": "Ontario",
                    "type": "TERRITORY",
                    "country": "CA",
                    "administrative_area": "CA-ON"
                }
            ],
            "inside": {
                "type": "COND_GEO",
                "fences": [
                    {
                        "name": "Canada",
                        "type": "TERRITORY",
                        "country": "CA",
                        'administrative_area': None,
                        "postal_code": None
                    }
                ],
                "inside": {
                    "type": "METHOD_AMOUNT",
                    "fences": [],
                    "amount": 0
                },
                "outside": {
                    "type": "METHOD_AMOUNT",
                    "fences": [],
                    "amount": 1
                }
            },
            "outside": {
                "type": "COND_GEO",
                "fences": [
                    {
                        "name": "USA",
                        "type": "TERRITORY",
                        "country": "US",
                        'administrative_area': None,
                        "postal_code": None
                    }
                ],
                "inside": {
                    "type": "FACTORS",
                    "fences": [],
                    "factors": ["KNOWLEDGE"]
                },
                "outside": {
                    "type": "FACTORS",
                    "fences": [],
                    "factors": ["KNOWLEDGE", "INHERENCE", "POSSESSION"]
                }
            }
        }
        parsed = self._validator().to_python(self._data)

        self.assertEqual(
            self._data,
            parsed
        )

    def test_missing_inside(self):
        self._data = {
            "fences": [
                {
                    "name": "Ontario",
                    "type": "TERRITORY",
                    "country": "CA",
                    "administrative_area": "CA-ON"
                }
            ],
            "outside": {
                "type": "FACTORS",
                "fences": [],
                "factors": ["KNOWLEDGE", "INHERENCE", "POSSESSION"]
            }
        }
        with assertRaisesRegex(self, Invalid, "^inside: Missing value$"):
            self._validator().to_python(self._data)

    def test_missing_outside(self):
        self._data = {
            "fences": [
                {
                    "name": "Ontario",
                    "type": "TERRITORY",
                    "country": "CA",
                    "administrative_area": "CA-ON"
                }
            ],
            "inside": {
                "type": "FACTORS",
                "fences": [],
                "factors": ["KNOWLEDGE", "INHERENCE", "POSSESSION"]
            }
        }
        with assertRaisesRegex(self, Invalid, "^outside: Missing value$"):
            self._validator().to_python(self._data)
