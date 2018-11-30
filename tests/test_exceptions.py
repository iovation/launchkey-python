import unittest
from mock import patch
from formencode import Invalid
from datetime import datetime

from launchkey.exceptions import AuthorizationInProgress


class TestAuthorizationInProgressException(unittest.TestCase):

    def setUp(self):
        self.warnings_patch = \
            patch("launchkey.exceptions.warnings").start()
        self.validator_patch = patch(
            "launchkey.exceptions.AuthorizationInProgressValidator").start()
        self.addCleanup(patch.stopall)

    def test_warning_thrown_when_data_is_not_expected(self):
        self.validator_patch.side_effect = Invalid("Message", "Value", "State")
        AuthorizationInProgress(
            "Error Detail", 400
        )
        self.warnings_patch.warn.assert_called_once()

    def test_warning_not_thrown_when_data_is_expected(self):
        AuthorizationInProgress(
            "Error Detail", 400
        )
        self.warnings_patch.warn.assert_not_called()

    def test_defaults_when_data_is_not_expected(self):
        self.validator_patch.side_effect = Invalid("Message", "Value", "State")
        exception = AuthorizationInProgress(
            "Error Detail", 400
        )
        self.assertIsNone(exception.my_authorization_request)
        self.assertIsNone(exception.expires)
        self.assertIsNone(exception.authorization_request_id)

    def test_validator_receives_input_data(self):
        AuthorizationInProgress(
            "Error Detail",
            400,
            error_data="input data"
        )
        self.validator_patch.return_value.to_python.assert_called_with(
            "input data"
        )

    def test_parsed_data(self):
        self.validator_patch.return_value.to_python.return_value = {
            "my_auth": True,
            "auth_request": "fdd7fd97-f432-11e8-a00c-acde48001122",
            "expires": datetime(2018, 1, 1, 1)
        }
        exception = AuthorizationInProgress(
            "Error Detail", 400
        )
        self.assertTrue(exception.my_authorization_request)
        self.assertEqual(
            exception.expires,
            datetime(2018, 1, 1, 1)
        )
        self.assertEqual(
            exception.authorization_request_id,
            "fdd7fd97-f432-11e8-a00c-acde48001122"
        )
