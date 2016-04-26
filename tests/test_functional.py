from __future__ import absolute_import
import unittest
from .mock_test import RequestReplacer


def get_api_key():
    return "-----BEGIN PUBLIC KEY-----\n\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8zQos4iDSjmUVrFUAg5G\nuhU6GehNKb8MCXFadRWiyLGjtbGZAk8fusQU0Uj9E3o0mne0SYESACkhyK+3M1Er\nbHlwYJHN0PZHtpaPWqsRmNzui8PvPmhm9QduF4KBFsWu1sBw0ibBYsLrua67F/wK\nPaagZRnUgrbRUhQuYt+53kQNH9nLkwG2aMVPxhxcLJYPzQCat6VjhHOX0bgiNt1i\nHRHU2phxBcquOW2HpGSWcpzlYgFEhPPQFAxoDUBYZI3lfRj49gBhGQi32qQ1YiWp\naFxOB8GA0Ny5SfI67u6w9Nz9Z9cBhcZBfJKdq5uRWjZWslHjBN3emTAKBpAUPNET\nnwIDAQAB\n-----END PUBLIC KEY-----\n"

def ping_get(launchkey_time=None):
    import datetime
    response = {"date_stamp": "2013-04-20 21:40:02", "key": get_api_key()}
    if launchkey_time is None:
        response['launchkey_time'] = str(datetime.datetime.now())[:19]
    else:
        response['launchkey_time'] = launchkey_time
    return response

def poll_get(iteration=0, error=0):
    if error > 0:
        return {"successful": False, "status_code": 400, "message": "Error message", "message_code": error, "response": {}}
    if iteration == 1:
        return {'auth': "c" * 360}
    else:
        return {"successful": False, "status_code": 400, "message": "There is no pending request", "message_code": 70402, "response": {}}

def auths_post():
    return {"auth_request": "o2jf89r0wmnxnxzshaw9185yebsj4re3"}

class FunctionalTestAPI(unittest.TestCase):

    def _create_API(self):
        from launchkey import API, generate_RSA
        self.private_key, self.public_key = generate_RSA()
        return API(1234567890, "abcdefghijklmnopqrstuvwyz1234567", self.private_key,
                   "testdomain.com", "v1")

    def test_authorize(self):
        api = self._create_API()
        RequestReplacer().replacer("get", "ping", ping_get())
        RequestReplacer().replacer("post", "auths", auths_post())
        response = api.authorize("testuser")
        print repr(response)
        assert response == auths_post()['auth_request']

    def test_poll_request(self):
        api = self._create_API()
        RequestReplacer().replacer("get", "poll", poll_get())
        auth_request = "b" * 32
        response = api.poll_request(auth_request)
        assert response['message_code'] == 70402
        assert response['message'] == "There is no pending request"
        RequestReplacer().replacer("get", "ping", ping_get())
        RequestReplacer().replacer("get", "poll", poll_get(1))
        response = api.poll_request(auth_request)
        assert response['auth'] == "c" * 360

    def test_is_authorized(self):
        ''' 
            Give an encrypted package and decrypt it using private key 
            Then test notify
        '''
        pass
        api = self._create_API()
        RequestReplacer().replacer("get", "ping", ping_get())
        RequestReplacer().replacer("put", "logs", None)
        

    def test_logout(self):
        pass
        api = self._create_API()
        RequestReplacer().replacer("get", "ping", ping_get())
        RequestReplacer().replacer("put", "logs", None)


from launchkey import API, generate_RSA
from mock import patch, MagicMock


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
        self._private_key, self._public_key = generate_RSA()
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
            'launchkey_time': '2015-01-01 00:00:00',
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
                'launchkey_time': '2015-01-01 00:00:00',
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

