import unittest
from mock import MagicMock, ANY
from launchkey.transports.base import APIResponse, APIErrorResponse


class TestAPIResponses(unittest.TestCase):

    def test_api_response_success(self):
        data = MagicMock(spec=str)
        headers = MagicMock(spec=dict)
        status_code = MagicMock(spec=int)
        response = APIResponse(data, headers, status_code)
        self.assertEqual(response.data, data)
        self.assertEqual(response.headers, headers)
        self.assertEqual(response.status_code, status_code)

    def test_api_response_string_repr(self):
        data = MagicMock(spec=str)
        headers = MagicMock(spec=dict)
        status_code = MagicMock(spec=int)
        response = APIResponse(data, headers, status_code)
        self.assertIn(str(data), str(response))
        self.assertIn(str(status_code), str(response))

    def test_error_response_type(self):
        self.assertIsInstance(APIErrorResponse(ANY, ANY, ANY), APIResponse)
