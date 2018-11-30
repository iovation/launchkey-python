import unittest
from mock import MagicMock, ANY, patch
from uuid import uuid4
from formencode import Schema, Invalid
import six

from launchkey.clients.base import api_call, ERROR_CODE_MAP, STATUS_CODE_MAP, \
    BaseClient
from launchkey.exceptions import LaunchKeyAPIException, InvalidEntityID, \
    UnexpectedAPIResponse
from launchkey.transports.base import APIResponse


class TestAPICallDecorator(unittest.TestCase):

    def setUp(self):
        self._failure_method = MagicMock()
        self._failure_method.__name__ = str(uuid4())
        patch("launchkey.exceptions.warnings").start()
        self.addCleanup(patch.stopall)

    def test_success(self):
        method = MagicMock()
        method.__name__ = str(uuid4())
        self.assertEqual(api_call(method)(), method())

    def test_error_code_map_without_error_data(self):
        for code, exception in six.iteritems(ERROR_CODE_MAP):
            self._failure_method.side_effect = LaunchKeyAPIException(
                {"error_code": code, "error_detail": {}}, 400
            )
            with self.assertRaises(exception):
                api_call(self._failure_method)()

    def test_error_code_map_with_error_data(self):
        for code, exception in six.iteritems(ERROR_CODE_MAP):
            self._failure_method.side_effect = LaunchKeyAPIException(
                {"error_code": code, "error_detail": {}, "error_data": {}}, 400
            )
            with self.assertRaises(exception):
                api_call(self._failure_method)()

    def test_status_code_map(self):
        for code, exception in six.iteritems(STATUS_CODE_MAP):
            self._failure_method.side_effect = LaunchKeyAPIException({}, code)
            with self.assertRaises(exception):
                api_call(self._failure_method)()

    def test_unexpected_error(self):
        self._failure_method.side_effect = LaunchKeyAPIException()
        with self.assertRaises(LaunchKeyAPIException):
            api_call(self._failure_method)()


class TestBaseClient(unittest.TestCase):

    def test_success(self):
        BaseClient(ANY, uuid4(), ANY)

    def test_invalid_entity_id(self):
        with self.assertRaises(InvalidEntityID):
            BaseClient(ANY, ANY, ANY)


class TestBaseClientValidateResponse(unittest.TestCase):

    def setUp(self):
        self._client = BaseClient(ANY, uuid4(), ANY)

    def test_validate_response_on_api_response(self):
        response = APIResponse(MagicMock(), ANY, ANY)
        self._client._validate_response(response, MagicMock(spec=Schema))

    def test_validate_response_on_other_response(self):
        response = MagicMock()
        self._client._validate_response(response, MagicMock(spec=Schema))
        response.data.assert_not_called()

    def test_validation_failure(self):
        response = MagicMock()
        validator = MagicMock(spec=Schema)
        validator.to_python.side_effect = Invalid(ANY, ANY, ANY)
        with self.assertRaises(UnexpectedAPIResponse):
            self._client._validate_response(response, validator)
