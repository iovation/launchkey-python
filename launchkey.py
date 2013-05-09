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


class API(object):
    """ Needed """

    #self.API_HOST = "https://sandbox-api.launchkey.com"
    API_HOST = "https://api.launchkey.com"
    api_pub_key = None

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
        if self.api_pub_key is None:
            #Ping to get key
            response = requests.get(self.API_HOST + "ping", verify=self.verify)
            self.api_pub_key = response.json()['key']
        encrypted_app_secret = encrypt_RSA(self.api_pub_key, self.app_secret)
        signature = sign_data(self.private_key, encrypted_app_secret)
        return {'app_key': self.app_key, 'secret_key': encrypted_app_secret,
                'signature': signature}

    def authorize(self, username):
        ''' Used to send an authorization request for a specific username '''
        params = self._prepare_auth()
        params['username'] = username
        response = requests.post(self.API_HOST + "auths", params=params, verify=self.verify)
        print "\n\nresponse is \n" + repr(response.text)
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
        params = {'app_key': self.app_key, 'app_secret': self.app_secret,
                  'auth_request': auth_request}
        response = requests.get(self.API_HOST + "poll", params=params, verify=self.verify)
        return response.json()

    def is_authorized(self, package):
        ''' 
            Returns boolean value based on whether user has denied or 
            accepted the authorization request
        '''
        import json
        auth_response = json.loads(decrypt_RSA(self.private_key, package))
        if not auth_response['response'] or str(auth_response['response']).lower() == "false":
            return self._notify("Authenticate", False)
        if str(auth_response['response']).lower() == "true":
            return self._notify("Authenticate", True, auth_response['auth_request'])
        return False

    def _notify(self, action, status, auth_request=""):
        '''
            Notifies LaunchKey as to whether the user was logged in/out or not
            This allows for the user to have a confirmed status regarding their
            session
        '''
        params = self._prepare_auth()
        params['username'] = username
        params['action'] = action
        params['status'] = status
        params['auth_request'] = auth_request
        response = requests.put(self.API_HOST + "logs", params=params, verify=self.verify)
        print "\n\nlogs response\n" + repr(response.text)
        pass

    def logout(self, username):
        ''' 
            Forces an end of session for user
            Then notifies API that the session end has been confirmed
        '''
        return self._notify("Revoke", False)
