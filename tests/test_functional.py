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
