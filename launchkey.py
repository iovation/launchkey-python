""" 
Python SDK for LaunchKey API 
For use in implementing LaunchKey
Version 1.1.0
@author LaunchKey
@updated 2013-09-16
"""

import requests

def generate_RSA(bits=2048):
    '''
    Generate an RSA keypair
    :param bits: Int. The key length in bits
    :return: String. private key
    :return: String. public key
    '''
    from Crypto.PublicKey import RSA
    new_key = RSA.generate(bits, e=65537)
    public_key = new_key.publickey().exportKey("PEM")
    private_key = new_key.exportKey("PEM")
    return private_key, public_key

def decrypt_RSA(key, package):
    '''
    Decrypt RSA encrypted package with private key
    :param key: Private key
    :param package: Base64 encoded string to decrypt
    :return: String decrypted
    '''
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from base64 import b64decode
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    decrypted = rsakey.decrypt(b64decode(package))
    return decrypted

def encrypt_RSA(key, message):
    '''
    RSA encrypts the message using the public key
    :param key: Public key to encrypt with
    :param message: String to be encrypted
    :return: Base64 encoded encrypted string
    '''
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from base64 import b64encode
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    encrypted = rsakey.encrypt(message)
    return encrypted.encode('base64')

def sign_data(priv_key, data):
    '''
    Create a signature for a set of data using private key
    :param priv_key: Private key
    :param data: String data that the signature is being created for
    :return: Base64 encoded signature
    '''
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
    :param pub_key: Public key
    :param signature: String signature to be verified
    :param data: The data the signature was created with
    :return: Boolean. True for verified. False for not verified.
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
    try:
        if signer.verify(digest, b64decode(signature)):
            return True
    except ValueError:
        pass
    return False


class API(object):
    """ 
    Launchkey API Object that can be used to authorize users,
    check existing authorization requests, and notify LaunchKey
    of the authorization response so it can appropriately be 
    logged and placed in orbit.
    """

    API_HOST = "https://api.launchkey.com"
    api_pub_key = None
    ping_time = None
    ping_difference = None

    def __init__(self, app_key, app_secret, private_key, version="v1", api_host="", test=False):
        self.app_key = app_key
        self.app_secret = app_secret
        self.private_key = private_key
        self.verify = not test
        if api_host != "":
            self.API_HOST = api_host
            if self.API_HOST[-1:] == "/":
                self.API_HOST = self.API_HOST[:-1]
        self.API_HOST += "/" + version + "/"

    def _prepare_auth(self):
        '''
        Encrypts app_secret with RSA key and signs
        '''
        #Ping to get key and time
        self.ping()
        to_encrypt = {"secret": self.app_secret, "stamped": str(self.ping_time)}
        encrypted_app_secret = encrypt_RSA(self.api_pub_key, str(to_encrypt))
        signature = sign_data(self.private_key, encrypted_app_secret)
        return {'app_key': self.app_key, 'secret_key': encrypted_app_secret,
                'signature': signature}

    def ping(self, force=False):
        '''
        Used to retrieve the API's public key and server time
        The key is used to encrypt data being sent to the API and the server time is used
        to ensure the data being sent is recent and relevant.
        Instead of doing a ping each time to the server, it keeps the key and server_time
        stored and does a comparison from the local time to appropriately adjust the value
        :param force: Boolean. True will override the cached variables and ping LaunchKey
        :return: JSON response with the launchkey_time and API's public key
        '''
        import datetime
        if force or self.api_pub_key is None or self.ping_time is None:
            response = requests.get(self.API_HOST + "ping", verify=self.verify).json()
            self.api_pub_key = response['key']
            self.ping_time = datetime.datetime.strptime(response['launchkey_time'], "%Y-%m-%d %H:%M:%S")
            self.ping_difference = datetime.datetime.now()
            return response
        else:
            self.ping_time = datetime.datetime.now() - self.ping_difference + self.ping_time
        return {"launchkey_time": str(self.ping_time)[:-7], "key": self.api_pub_key}

    def authorize(self, username, session=True):
        '''
        Used to send an authorization request for a specific username
        :param username: String. The LaunchKey username of the one authorizing
        :param session: Boolean. If keeping a session mark True; transactional mark False
        :return: String. The auth_request value for future reference.
        '''
        params = self._prepare_auth()
        params['username'] = username
        params['session'] = session
        response = requests.post(self.API_HOST + "auths", params=params, verify=self.verify)
        try:
            if 'status_code' in response.json() and response.json()['status_code'] >= 300:
                error = str(response.json()['message_code']) + " " + response.json()['message']
                return "Error: " + error
        except ValueError:
            return "Error"
        return response.json()['auth_request']

    def poll_request(self, auth_request):
        '''
        Poll the API to find the status of an authorization request
        :param auth_request: String. The reference value provided from authorize.
        :return: JSON. The response will have an error or the encrypted response from the user.
        '''
        params = self._prepare_auth()
        params['auth_request'] = auth_request
        response = requests.get(self.API_HOST + "poll", params=params, verify=self.verify)
        return response.json()

    def is_authorized(self, auth_request, package):
        ''' 
        Returns boolean value based on whether user has denied or accepted the authorization
        request and it has passed all security checks
        :param auth_request. String. Same reference value used in poll_request and authorize
        :param package. String. "auth" value returned from a successful poll_request
        :return: Boolean. True if successfully authorizes. False if denied or something goes wrong.
        '''
        import json
        auth_response = json.loads(decrypt_RSA(self.private_key, package))
        if "response" not in auth_response or "auth_request" not in auth_response or \
                auth_request != auth_response['auth_request']:
            return self._notify("Authenticate", False, auth_request)
        pins_valid = False
        try:
            pins_valid = self.pins_valid(auth_response['app_pins'], auth_response['device_id'])
        except NotImplementedError:
            pins_valid = True
        if pins_valid:
            response = str(auth_response['response']).lower() == 'true'
            return self._notify("Authenticate", response, auth_response['auth_request'])
        return False

    def _notify(self, action, status, auth_request):
        '''
        Notifies LaunchKey as to whether the user was logged in/out or not
        This allows for the user to have a confirmed status regarding their
        session
        :param action: String. Authenticate or Revoke depending on action being taken.
        :param status: Boolean. True for authorization, False for deny or failure.
        :param auth_request: String. The value originally provided by authorize for reference.
        :return: Boolean. Will match the status going in unless there's a failure in which case
            the return will default to False.
        '''
        params = self._prepare_auth()
        params['action'] = action
        params['status'] = status
        params['auth_request'] = auth_request
        response = requests.put(self.API_HOST + "logs", params=params, verify=self.verify)
        if "message" in response.json() and response.json()['message'] == "Successfully updated":
            return status
        return False

    def deorbit(self, deorbit, signature):
        ''' 
        Verify the deorbit request by signature and timestamp 
        Return the user_hash needed to identify the user and log them out
        :param deorbit: JSON string from LaunchKey with the user_hash and
        launchkey_time.
        :param signature: String. Signature signed by API to verify the authenticity of the
        data found in the deorbit JSON.
        :return: String when successful of the user_hash and None on failure.
        '''
        import json
        import datetime
        self.ping()
        if verify_sign(self.api_pub_key, signature, deorbit):
            decoded = json.loads(deorbit)
            date_request = datetime.datetime.strptime(decoded['launchkey_time'], "%Y-%m-%d %H:%M:%S")
            if self.ping_time - date_request < datetime.timedelta(minutes=5):
                #Only want to honor a request that's been made recently
                return decoded['user_hash']
        return None

    def logout(self, auth_request):
        ''' 
        Notifies API that the session end has been confirmed
        :param auth_request: String. The value originally provided by authorize for reference.
        :return: Boolean. True on success, False on failure.
        '''
        return self._notify("Revoke", True, auth_request)

    def pins_valid(self, app_pins, device):
        ''' 
        Return boolean for whether the tokens pass or not 
        May optionally be implemented in a subclass
        Should take into consideration device_id and whether the existing
        PINs match up to the previous pins on prior requests
        Can one-way hash the PINs newest 4 PINs for storage and compare on authorization
        :param app_pins: The PINs that were sent with the device's authorization response
        :param device: The device_id to identify which of the user's devices was used and
        by which to check the PINs
        '''
        raise NotImplementedError
        user = get_user_hash()
        pins = get_existing_pins(user, device)
        update = False
        if app_pins.count(",") == 0 and pins.strip() == "":
            update = True
        elif app_pins.count(",") > 0:
            if app_pins[:app_pins.rfind(",")] == pins.strip():
                update = True
                if app_pins.count(",") == 4:
                    app_pins = app_pins[app_pins.find(",") + 1:]
            elif app_pins[app_pins.find(",") + 1:] == pins.strip():
                update = True
                if app_pins.count(",") == 4:
                    app_pins = app_pins[:app_pins.rfind(",")]
        if update:
            update_pins(user, device, app_pins)
            return True
    
    def get_user_hash(self):
        '''
        Get the user hash for this request
        :return: user_hash
        '''
        raise NotImplementedError('Subclass must implement.')
    
    def get_existing_pins(self, user, device):
        '''
        Get string of all PINs comma delimited that exist for the user already from
        persistent store
        :param user: the user_hash for this request
        :param device: the device id that was decrypted in the response for this authorization
        :return: pins as a string going from oldest to newest
        '''
        raise NotImplementedError('Subclass must implement.')
    
    def update_pins(self, user, device, pins):
        '''
        Update the persistent store with the latest PINs
        :param user: user_hash
        :param device: the device_id to identify which of the user's devices
        :param pins: the latest PINs with which to update
        '''
        raise NotImplementedError('Subclass must implement.')
    
    
