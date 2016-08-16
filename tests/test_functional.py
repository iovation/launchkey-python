from __future__ import absolute_import
from launchkey import API, generate_rsa
from mock import patch, MagicMock
import unittest
import requests

api_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8zQos4iDSjmUVrFUAg5G
uhU6GehNKb8MCXFadRWiyLGjtbGZAk8fusQU0Uj9E3o0mne0SYESACkhyK+3M1Er
bHlwYJHN0PZHtpaPWqsRmNzui8PvPmhm9QduF4KBFsWu1sBw0ibBYsLrua67F/wK
PaagZRnUgrbRUhQuYt+53kQNH9nLkwG2aMVPxhxcLJYPzQCat6VjhHOX0bgiNt1i
HRHU2phxBcquOW2HpGSWcpzlYgFEhPPQFAxoDUBYZI3lfRj49gBhGQi32qQ1YiWp
aFxOB8GA0Ny5SfI67u6w9Nz9Z9cBhcZBfJKdq5uRWjZWslHjBN3emTAKBpAUPNET
nwIDAQAB
-----END PUBLIC KEY-----
"""


def ping_get():
    import datetime
    return {"date_stamp": "2013-04-20 21:40:02", "key": api_key, 'api_time': str(datetime.datetime.now())[:19]}


def auths_post():
    return {"auth_request": "o2jf89r0wmnxnxzshaw9185yebsj4re3"}


class FunctionalTestAPI(unittest.TestCase):
    __poll_responses = [
        {"successful": False, "status_code": 400, "message": "Error message", "message_code": 1, "response": {}}]

    def __response_to_get(self):

        def _responder(*args, **kwargs):
            del kwargs
            response = MagicMock()
            if args[0].endswith('poll'):
                response.json = MagicMock(return_value=self.__poll_responses.pop())
            else:
                response.json = MagicMock(return_value=ping_get())
            return response

        return _responder

    def setUp(self):
        super(FunctionalTestAPI, self).setUp()

        self.__get = requests.get
        requests.get = MagicMock(side_effect=self.__response_to_get())

        self.__put = requests.put
        requests.put = MagicMock(return_value=None)

        self.__post = requests.post
        post_response = MagicMock()
        post_response.json = MagicMock(return_value=auths_post())
        requests.post = MagicMock(return_value=post_response)

        self.__delete = requests.delete
        requests.delete = MagicMock()

    def tearDown(self):
        super(FunctionalTestAPI, self).tearDown()
        requests.get = self.__get
        requests.put = self.__put
        requests.post = self.__post
        requests.delete = self.__delete

    def _create_API(self):
        from launchkey import API, generate_rsa
        self.private_key, self.public_key = generate_rsa()
        return API(1234567890, "abcdefghijklmnopqrstuvwyz1234567", self.private_key,
                   "testdomain.com", "v1")

    def test_authorize(self):
        api = self._create_API()
        response = api.authorize("testuser")
        self.assertEqual(auths_post()['auth_request'], response)

    def test_poll_request(self):
        api = self._create_API()
        auth_request = "b" * 32
        self.__poll_responses = [
            {"successful": False, "status_code": 400, "message": "There is no pending request",
             "message_code": 70402, "response": {}}
        ]

        response = api.poll_request(auth_request)
        self.assertEqual(70402, response['message_code'])
        self.assertEqual("There is no pending request", response['message'])
        self.__poll_responses = [{'auth': "c" * 360}]
        response = api.poll_request(auth_request)
        self.assertIn('auth', response)
        self.assertEqual("c" * 360, response['auth'])


class FunctionalTestAPI2(unittest.TestCase):
    def tearDown(self):
        super(FunctionalTestAPI2, self).tearDown()
        del self._api
        del self._api_key
        del self._private_key
        del self._public_key
        del self._ping_response

    def setUp(self):
        super(FunctionalTestAPI2, self).setUp()
        self._private_key, self._public_key = generate_rsa()
        self._api_key = """-----BEGIN PUBLIC KEY-----

MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8zQos4iDSjmUVrFUAg5G
uhU6GehNKb8MCXFadRWiyLGjtbGZAk8fusQU0Uj9E3o0mne0SYESACkhyK+3M1Er
bHlwYJHN0PZHtpaPWqsRmNzui8PvPmhm9QduF4KBFsWu1sBw0ibBYsLrua67F/wK
PaagZRnUgrbRUhQuYt+53kQNH9nLkwG2aMVPxhxcLJYPzQCat6VjhHOX0bgiNt1i
HRHU2phxBcquOW2HpGSWcpzlYgFEhPPQFAxoDUBYZI3lfRj49gBhGQi32qQ1YiWp
aFxOB8GA0Ny5SfI67u6w9Nz9Z9cBhcZBfJKdq5uRWjZWslHjBN3emTAKBpAUPNET
nwIDAQAB

-----END PUBLIC KEY-----
"""
        self._api = API(1234567890, 'abcdefghijklmnopqrstuvwyz1234567', self._private_key,
                        'testdomain.com', 'v1')
        self._ping_response = MagicMock()
        self._ping_response.json.return_value = {
            'date_stamp': '2013-04-20 21:40:02',
            'api_time': '2015-01-01 00:00:00',
            'key': self._api_key
        }
        self._ping_mock = MagicMock(return_value=self._ping_response)

    def test_authorize(self):
        with patch('requests.get', self._ping_mock):
            expected = 'o2jf89r0wmnxnxzshaw9185yebsj4re3'
            auths_response = MagicMock()
            auths_response.json.return_value = {'auth_request': expected}
            auths_mock = MagicMock(return_value=auths_response)
            with patch('requests.post', auths_mock):
                response = self._api.authorize('testuser')
                self.assertEqual(expected, response)

    def test_poll_request_returns_json_response(self):
        get_response = MagicMock()
        expected = {'expected': 'response'}
        responses = [
            expected,
            {
                'date_stamp': '2013-04-20 21:40:02',
                'api_time': '2015-01-01 00:00:00',
                'key': self._api_key
            }
        ]

        def _side_effect():
            return responses.pop()

        get_response.json.side_effect = _side_effect

        with patch('requests.get', return_value=get_response) as get_mock:
            get_mock.json.return_value = MagicMock()

            response = self._api.poll_request('auth request')
            self.assertEqual(response, expected)
