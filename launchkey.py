""" 
    Python SDK for LaunchKey API 
    For use in implementing LaunchKey
    Version 1.0
    @author LaunchKey
    @created 2013-03-20
"""

import requests

def generate_RSA(bits=2048):
    '''
        Generate an RSA keypair
        @bits The key length in bits
        Return private key and public key
    '''
    from Crypto.PublicKey import RSA
    new_key = RSA.generate(bits, e=65537)
    public_key = new_key.publickey().exportKey("PEM")
    private_key = new_key.exportKey("PEM")
    return private_key, public_key

def decrypt_RSA(key, package):
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from base64 import b64decode
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    decrypted = rsakey.decrypt(b64decode(package))
    return decrypted

def encrypt_RSA(key, message):
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from base64 import b64encode
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    encrypted = rsakey.encrypt(message)
    return encrypted.encode('base64')

def sign_data(priv_key, data):
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA256
    from base64 import b64encode, b64decode
    rsakey = RSA.importKey(priv_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(b64decode(data))
    sign = signer.sign(digest)
    return b64encode(sign)

def verify_sign(pub_key, signature, data):
    ''' 
        Verifies with a public key from whom the data came that it was indeed
        signed by their private key.
    '''
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA256
    from base64 import b64decode
    data = data.replace('\r', '')
    rsakey = RSA.importKey(pub_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(data)
    if signer.verify(digest, b64decode(signature)):
        return True
    return False


class API(object):
    """ Needed """

    #self.API_HOST = "https://sandbox-api.launchkey.com"
    API_HOST = "https://api.launchkey.com"
    api_pub_key = None
    ping_time = None
    ping_difference = None

    def __init__(self, app_key, app_secret, private_key, domain, version, api_host="", test=False):
        self.app_key = app_key
        self.app_secret = app_secret
        self.private_key = private_key
        self.domain = domain
        self.verify = not test
        if api_host != "":
            self.API_HOST = api_host
        self.API_HOST += "/" + version + "/"

    def _prepare_auth(self):
        ''' Encrypts app_secret with RSA key and signs '''
        #Ping to get key and time
        self.ping()
        to_encrypt = {"secret": self.app_secret, "stamped": str(self.ping_time)}
        encrypted_app_secret = encrypt_RSA(self.api_pub_key, str(to_encrypt))
        signature = sign_data(self.private_key, encrypted_app_secret)
        return {'app_key': self.app_key, 'secret_key': encrypted_app_secret,
                'signature': signature}

    def ping(self):
        import datetime
        if self.api_pub_key is None or self.ping_time is None:
            response = requests.get(self.API_HOST + "ping", verify=self.verify).json()
            self.api_pub_key = response['key']
            self.ping_time = datetime.datetime.strptime(response['launchkey_time'], "%Y-%m-%d %H:%M:%S")
            self.ping_difference = datetime.datetime.now()
        else:
            self.ping_time = datetime.datetime.now() - self.ping_difference + self.ping_time

    def authorize(self, username):
        ''' Used to send an authorization request for a specific username '''
        params = self._prepare_auth()
        params['username'] = username
        response = requests.post(self.API_HOST + "auths", params=params, verify=self.verify)
        if 'status_code' in response.json() and response.json()['status_code'] >= 300:
            #Error response.json()['message_code']
            '''30421 - POST; Incorrect data for API call
            30422 - POST; Credentials incorrect for app and app secret
            30423 - POST; Error verifying app
            30424 - POST; No paired devices'''
            return "Error"
        return response.json()['auth_request']

    def poll_request(self, auth_request):
        ''' Poll the API to find the status of an authorization request '''
        params = self._prepare_auth()
        params['auth_request'] = auth_request
        response = requests.get(self.API_HOST + "poll", params=params, verify=self.verify)
        return response.json()

    def is_authorized(self, auth_request, package):
        ''' 
            Returns boolean value based on whether user has denied or 
            accepted the authorization request
        '''
        import json
        auth_response = json.loads(decrypt_RSA(self.private_key, package))
        if not auth_response['response'] or str(auth_response['response']).lower() == "false" or \
                not auth_response['auth_request'] or auth_request != auth_response['auth_request']:
            return self._notify("Authenticate", False)
        if self.pins_valid(auth_response['app_pins'], auth_response['device_id']) and str(auth_response['response']).lower() == "true":
            return self._notify("Authenticate", True, auth_response['auth_request'])
        return False

    def _notify(self, action, status, auth_request=""):
        '''
            Notifies LaunchKey as to whether the user was logged in/out or not
            This allows for the user to have a confirmed status regarding their
            session
        '''
        params = self._prepare_auth()
        params['action'] = action
        params['status'] = status
        params['auth_request'] = auth_request
        response = requests.put(self.API_HOST + "logs", params=params, verify=self.verify)
        if "message" in response.json() and response.json()['message'] == "Successfully updated":
            return status
        return False

    def deorbit(self, orbit, signature):
        ''' 
            Verify the deorbit request by signature and timestamp 
            Return the user_hash needed to identify the user and log them out
        '''
        import json
        import datetime
        self.ping()
        if verify_sign(self.api_pub_key, signature, orbit):
            decoded = json.loads(orbit)
            date_request = datetime.datetime.strptime(decoded['launchkey_time'], "%Y-%m-%d %H:%M:%S")
            if not self.ping_time - date_request > datetime.timedelta(minutes=5):
                return decoded['user_hash']
        return None

    def logout(self, auth_request):
        ''' 
            Notifies API that the session end has been confirmed
        '''
        return self._notify("Revoke", True, auth_request)

    def pins_valid(self, app_pins, device):
        ''' 
            Return boolean for whether the tokens pass or not 
            Not fully implemented
            Should take into consideration device_id and whether the existing
            pins match up to the previous pins on prior requests
        '''
        tokens = app_pins.split(",")
        return True