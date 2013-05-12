import unittest
from tests.mock import RequestReplacer

def get_api_key():
    return "-----BEGIN PUBLIC KEY-----\n\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8zQos4iDSjmUVrFUAg5G\nuhU6GehNKb8MCXFadRWiyLGjtbGZAk8fusQU0Uj9E3o0mne0SYESACkhyK+3M1Er\nbHlwYJHN0PZHtpaPWqsRmNzui8PvPmhm9QduF4KBFsWu1sBw0ibBYsLrua67F/wK\nPaagZRnUgrbRUhQuYt+53kQNH9nLkwG2aMVPxhxcLJYPzQCat6VjhHOX0bgiNt1i\nHRHU2phxBcquOW2HpGSWcpzlYgFEhPPQFAxoDUBYZI3lfRj49gBhGQi32qQ1YiWp\naFxOB8GA0Ny5SfI67u6w9Nz9Z9cBhcZBfJKdq5uRWjZWslHjBN3emTAKBpAUPNET\nnwIDAQAB\n\n-----END PUBLIC KEY-----\n"

def ping_get(launchkey_time=None):
    import datetime
    response = {"date_stamp": "2013-04-20 21:40:02", "key": get_api_key()}
    if launchkey_time is None:
        response['launchkey_time'] = datetime.datetime.now()
    else:
        response['launchkey_time'] = launchkey_time
    return response

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

