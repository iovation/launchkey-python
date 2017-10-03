import unittest
from mock import MagicMock, patch
from requests import Response
from requests.exceptions import HTTPError
from launchkey.transports import RequestsTransport
from launchkey.transports.base import APIResponse
from launchkey.transports.base import APIErrorResponse
from launchkey import LAUNCHKEY_PRODUCTION


class TestRequestsHTTPTransportParseResponse(unittest.TestCase):

    def setUp(self):
        self._transport = RequestsTransport()
        self._requests_response = MagicMock(spec=Response())

    def test_parse_response_success(self):
        transport_response = self._transport._parse_response(self._requests_response)
        self.assertIsInstance(transport_response, APIResponse)
        self.assertEqual(self._requests_response.json(), transport_response.data)
        self.assertEqual(self._requests_response.headers, transport_response.headers)
        self.assertEqual(self._requests_response.status_code, transport_response.status_code)

    def test_parse_response_json_success(self):
        transport_response = self._transport._parse_response(self._requests_response)
        self.assertIsInstance(transport_response, APIResponse)
        self._requests_response.json.assert_called_once()
        self.assertNotEqual(self._requests_response.text, transport_response.data)
        self.assertEqual(self._requests_response.json(), transport_response.data)
        self.assertEqual(self._requests_response.headers, transport_response.headers)
        self.assertEqual(self._requests_response.status_code, transport_response.status_code)

    def test_parse_response_text_success(self):
        self._requests_response.json.side_effect = ValueError()
        transport_response = self._transport._parse_response(self._requests_response)
        self.assertIsInstance(transport_response, APIResponse)
        with self.assertRaises(ValueError):
            self._requests_response.json()
        self.assertEqual(self._requests_response.text, transport_response.data)
        self.assertEqual(self._requests_response.headers, transport_response.headers)
        self.assertEqual(self._requests_response.status_code, transport_response.status_code)

    def test_parse_response_400_failure(self):
        self._requests_response.raise_for_status.side_effect = HTTPError()
        self._requests_response.status_code = 400
        transport_response = self._transport._parse_response(self._requests_response)
        self.assertIsInstance(transport_response, APIErrorResponse)
        self.assertEqual(self._requests_response.json(), transport_response.data)
        self.assertEqual(self._requests_response.headers, transport_response.headers)
        self.assertEqual(self._requests_response.status_code, transport_response.status_code)

    def test_parse_response_500_failure(self):
        self._requests_response.raise_for_status.side_effect = HTTPError()
        self._requests_response.status_code = 500
        with self.assertRaises(HTTPError):
            self._transport._parse_response(self._requests_response)


class TestRequestsHTTPTransport(unittest.TestCase):

    def setUp(self):
        self._transport = RequestsTransport()

    def test_defaults(self):
        self.assertEqual(self._transport.url, LAUNCHKEY_PRODUCTION)
        self.assertEqual(self._transport.testing, False)
        self.assertEqual(self._transport.verify_ssl, True)

    def test_set_url(self):
        url = MagicMock(spec=str)
        testing = MagicMock(spec=bool)
        self._transport.set_url(url, testing)
        self.assertNotEqual(self._transport.url, LAUNCHKEY_PRODUCTION)
        self.assertEqual(self._transport.url, url)
        self.assertEqual(self._transport.testing, testing)
        self.assertEqual(self._transport.verify_ssl, not testing)

    @patch("requests.get")
    def test_get(self, requests_patch):
        self._transport.get(MagicMock())
        requests_patch.assert_called_once()

    @patch("requests.post")
    def test_post(self, requests_patch):
        self._transport.post(MagicMock())
        requests_patch.assert_called_once()

    @patch("requests.put")
    def test_put(self, requests_patch):
        self._transport.put(MagicMock())
        requests_patch.assert_called_once()

    @patch("requests.delete")
    def test_delete(self, requests_patch):
        self._transport.delete(MagicMock())
        requests_patch.assert_called_once()
        
    @patch("requests.patch")
    def test_patch(self, requests_patch):
        self._transport.patch(MagicMock())
        requests_patch.assert_called_once()
