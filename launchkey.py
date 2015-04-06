""" 
Python SDK for LaunchKey API 
For use in implementing LaunchKey
Version 1.2.0
@author LaunchKey
@updated 2014-06-16
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

def sign_data(priv_key, data, encoded=True):
    '''
    Create a signature for a set of data using private key
    :param priv_key: Private key
    :param data: String data that the signature is being created for
    :param encoded: Boolean. True for base64 encoded data input
    False for raw data input
    :return: Base64 encoded signature
    '''
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA256
    from base64 import b64encode, b64decode
    rsakey = RSA.importKey(priv_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    if encoded:
        digest.update(b64decode(data))
    else:
        digest.update(data)
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

def decrypt_AES(cipher, package, iv):
    '''
    Decrypts an AES package using a specific cipher and iv
    :param cipher: String. Key for decryption.
    :param package: String. The base64 encoded data to be decrypted.
    :param iv: String. 16 characters. Used to randomize the data for repeated
        cipher usage by changing this value. Can be sent plaintext.
    '''
    from Crypto.Cipher import AES
    from base64 import b64decode
    cipher_obj = AES.new(cipher, AES.MODE_CBC, iv)
    return cipher_obj.decrypt(b64decode(package))


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

    def _prepare_auth(self, cipher=None, signature=False):
        '''
        Encrypts secret with RSA key and signs
        :param cipher: The AES cipher that was used to encrypt other parameters or body
        :return: Dict with RSA encrypted secret_key and signature of that value
        '''
        #Ping to get key and time
        self.ping()
        to_encrypt = {"secret": self.app_secret, "stamped": str(self.ping_time)}
        if cipher is not None:
            to_encrypt['cipher'] = cipher
        encrypted_secret = encrypt_RSA(self.api_pub_key, str(to_encrypt))
        to_return = {'secret_key': encrypted_secret}
        if signature:
            signature = sign_data(self.private_key, encrypted_secret)
            to_return['signature'] = signature
        
        to_return['app_key'] = self.app_key
        return to_return

    def _signature(self, body):
        return sign_data(self.private_key, body, encoded=False)

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

    def authorize(self, username, session=True, user_push_id=False):
        '''
        Used to send an authorization request for a specific username
        :param username: String. The LaunchKey username of the one authorizing
        :param session: Boolean. If keeping a session mark True; transactional mark False
        :param user_push_id: Boolean. If your app would like to be returned an ID for the user
        that can be used to initiate notifications in the future without user input mark True.
        :return: String. The auth_request value for future reference.
        '''
        params = self._prepare_auth(signature=True)
        params['username'] = username
        params['session'] = session
        params['user_push_id'] = user_push_id
        response = requests.post(self.API_HOST + "auths", params=params, verify=self.verify)
        try:
            if 'status_code' in response.json() and response.json()['status_code'] >= 300:
                error = str(response.json()['message_code']) + " " + str(response.json()['message'])
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
        params = self._prepare_auth(signature=True)
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
        response = str(auth_response['response']).lower() == 'true'
        return self._notify("Authenticate", response, auth_response['auth_request'])


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
        params = self._prepare_auth(signature=True)
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

    def get_user_hash(self):
        '''
        Get the user hash for this request
        :return: user_hash
        '''
        raise NotImplementedError('Subclass must implement.')
    
    def create_whitelabel_user(self, identifier):
        '''
        WhiteLabel Only
        Create a new user for your White Label application
        If the user for the specified identifier already exists, then set up a new device
        for that user
        :param identifier: How the user is identified to your application
            This should be a static value such as a user's ID or UUID value rather than an
            email address which may be subject to change.  This identifier will be used authenticate the user as well as
            pair devices additional devices to the user's account within your white label group.
        :return: JSON response
            qrcode - The URL to a QR Code for the device to scan
            code - Manual code for the user to type into their device if they are unable to
                scan the QR Code
        '''
        import json
        body = self._prepare_auth()
        body['identifier'] = identifier
        json_string = json.dumps(body)
        headers = {"content-type": "application/json"}
        response = requests.post(self.API_HOST + "users", data=json_string,
                                 params={"signature": self._signature(json_string)},
                                 headers=headers, verify=self.verify)
        cipher = decrypt_RSA(self.private_key, response.json()['response']['cipher'])
        data = decrypt_AES(cipher[:-16], response.json()['response']['data'], cipher[-16:])
        import json
        return json.loads(data)
