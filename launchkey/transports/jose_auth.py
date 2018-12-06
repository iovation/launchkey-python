""" JOSE based transport"""

# pylint: disable=too-many-instance-attributes, too-many-arguments

import warnings
import json

from base64 import b64decode
from uuid import UUID, uuid4
from hashlib import sha256, sha384, sha512, md5
from time import time
from calendar import timegm
from dateutil.parser import parse
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from jwkest import JWKESTException
from jwkest.jwk import RSAKey, import_rsa_key
from jwkest.jws import JWS, NoSuitableSigningKeys
from jwkest.jwe import JWE, JWEnc
from jwkest.jwt import BadSyntax

import six

from ..exceptions import InvalidEntityID, InvalidPrivateKey, \
    InvalidIssuer, InvalidAlgorithm, LaunchKeyAPIException, \
    JWTValidationFailure, UnexpectedAPIResponse, NoIssuerKey, \
    InvalidJWTResponse, UnexpectedKeyID
from .. import VALID_JWT_ISSUER_LIST, API_CACHE_TIME, \
    JOSE_SUPPORTED_CONTENT_HASH_ALGS, JOSE_SUPPORTED_JWE_ALGS, \
    JOSE_SUPPORTED_JWE_ENCS, JOSE_SUPPORTED_JWT_ALGS, \
    JOSE_AUDIENCE, JOSE_JWT_LEEWAY
from .http import RequestsTransport
from .base import APIErrorResponse


class JOSETransport(object):
    """
    Transport to wrap HTTP transport for providing request/response validation,
    encryption, and decryption.
    """
    audience = JOSE_AUDIENCE

    def __init__(self, jwt_algorithm="RS512", jwe_cek_encryption="RSA-OAEP",
                 jwe_claims_encryption="A256CBC-HS512",
                 content_hash_algorithm="S256", http_client=None):
        """
        :param jwt_algorithm: JWT Signing algorithm
                              Currently supported: RS256, RS384, RS512
        :param jwe_cek_encryption: JWE algorithm to use with CEK encryption
        Currently supported: RSA-OAEP
        To be supported: RSA-OAEP-256 (pending pyjwkest release to > 1.3.2)
        :param jwe_claims_encryption: JWE algorithm to use for claims
        encryption.
        Currently supported: A256CBC-HS512
        :param content_hash_algorithm: Hashing algorithm for signing
        content body.
        Currently supported: S256, S384, S512 (shortened forms of SHAxxx)
        :param http_client: HTTP transport to contact the LaunchKey api after
        JOSE processing is complete
        """
        self.issuer = None
        self.issuer_id = None
        self.loaded_issuer_private_keys = {}
        self.issuer_private_keys = []
        self._server_time_difference = None, None
        self._api_public_keys = [], None

        self.jwt_algorithm = self.__verify_supported_algorithm(
            jwt_algorithm, JOSE_SUPPORTED_JWT_ALGS)
        self.jwe_cek_encryption = self.__verify_supported_algorithm(
            jwe_cek_encryption, JOSE_SUPPORTED_JWE_ALGS)
        self.jwe_claims_encryption = self.__verify_supported_algorithm(
            jwe_claims_encryption, JOSE_SUPPORTED_JWE_ENCS)
        self.content_hash_algorithm = self.__verify_supported_algorithm(
            content_hash_algorithm,
            JOSE_SUPPORTED_CONTENT_HASH_ALGS)
        self._http_client = http_client \
            if http_client is not None else RequestsTransport()

    @staticmethod
    def __verify_supported_algorithm(algorithm, supported_list):
        """
        Verifies an input string algorithm is in an input list, and raises
        the appropriate exception if it is not
        """
        if algorithm not in supported_list:
            raise InvalidAlgorithm(
                "Input algorithm {0} is not in "
                "the supported list of {1}".format(algorithm, supported_list))
        return algorithm

    @staticmethod
    def __get_jti():
        """Retrieves a unique JWT ID"""
        return str(uuid4())

    @staticmethod
    def __generate_key_id(rsa_key):
        """
        Generates a key id to be used in JWE + JWT. It is based on the digest
        of the key.
        :param rsa_key: RSA private key in string format
        :return:
        """
        key = RSA.importKey(rsa_key)
        md5digest = md5(key.publickey().exportKey('DER')).hexdigest()
        return ":".join(
            md5digest[i:i + 2] for i in range(0, len(md5digest), 2))

    @staticmethod
    def parse_api_time(api_time):
        """
        Parses LaunchKey api_time to a unix timestamp
        :return: int representation of the timestamp
        """
        return timegm(parse(api_time).timetuple())

    @property
    def server_time_difference(self):
        """
        The time drag between the sdk and the Launchkey API. The result is
        cached for API_CACHE_TIME
        """
        now = int(time())
        if self._server_time_difference[1] is None or now - \
                self._server_time_difference[1] > API_CACHE_TIME:
            response = self.get("/public/v3/ping", None)
            try:
                self._server_time_difference = now - self.parse_api_time(
                    response.data['api_time']), now
            except (KeyError, ValueError, TypeError):
                raise UnexpectedAPIResponse(
                    "Unexpected api time received: %s" % response.data)
        return self._server_time_difference[0]

    @property
    def api_public_keys(self):
        """
        The public key retrieved from the LaunchKey API. The result is
        cached for API_CACHE_TIME
        """
        now = int(time())
        if self._api_public_keys[1] is None \
                or now - self._api_public_keys[1] > API_CACHE_TIME:
            response = self.get("/public/v3/public-key", None)
            try:
                key = RSAKey(key=import_rsa_key(response.data),
                             kid=response.headers.get('X-IOV-KEY-ID'))
            except (IndexError, TypeError):
                raise UnexpectedAPIResponse(
                    "Unexpected api public key received: %s" % response.data)
            except ValueError:
                raise UnexpectedAPIResponse("Unexpected api public key "
                                            "received, RSA parsing error"
                                            ": %s" % response.data)
            if key not in self._api_public_keys[0]:
                self._api_public_keys[0].append(key)
            self._api_public_keys = self._api_public_keys[0], now
        return self._api_public_keys[0]

    def add_issuer_key(self, private_key):
        """
        Adds a private key to the list of keys available for decryption
        and signatures
        :return: Boolean - Whether the key is already in the list
        """
        new_key = RSAKey(key=import_rsa_key(private_key),
                         kid=self.__generate_key_id(private_key))
        for key in self.issuer_private_keys:
            if new_key.kid == key.kid:
                return False
        self.issuer_private_keys.append(new_key)
        self.loaded_issuer_private_keys[new_key.kid] = PKCS1_OAEP.new(
            RSA.importKey(private_key))
        return True

    def set_url(self, url, testing):
        """
        Creates a new http_client using the input url and testing flag
        :param url: Base url for the querying LaunchKey API
        :param testing: Boolean stating whether testing mode is being
        performed. This will determine whether SSL should be verified.
        :return:
        """
        self._http_client.set_url(url, testing)

    def set_issuer(self, issuer, issuer_id, private_key):
        """
        Set the issuer credentials
        :param issuer: Issuer entity type (svc, dir, or org)
        :param issuer_id: Identifier for the issuer entity
        :param private_key: PEM formatted private key for issuer entity
        :return: None
        :raises launchkey.exceptions.InvalidEntityID: when issuer_id is not
        valid
        :raises launchkey.exceptions.InvalidIssuer: when issuer is not valid
        :raises launchkey.exceptions.InvalidPrivateKey when private_key is
        not valid
        """
        if issuer not in VALID_JWT_ISSUER_LIST:
            raise InvalidIssuer("Invalid issuer it must be one of: {0}".format(
                VALID_JWT_ISSUER_LIST))
        try:
            UUID(str(issuer_id))
        except ValueError:
            raise InvalidEntityID(
                "The given id was invalid. Please ensure it is a UUID.")
        self.issuer = "%s:%s" % (issuer, issuer_id)
        try:
            self.add_issuer_key(private_key)
        except ValueError:
            raise InvalidPrivateKey(
                "Invalid private key. Please ensure you are submitting "
                "a string representation of a PEM private key.")

    def _get_jwt_signature(self, params):
        try:
            jws = JWS(params, alg=self.jwt_algorithm)
            return jws.sign_compact(keys=self.issuer_private_keys)
        except NoSuitableSigningKeys:
            raise NoIssuerKey(
                "An issuer key wasn't loaded. Please run set_issuer() first.")

    def _build_jwt_signature(self, method, resource, jti, subject,
                             content_hash=None):
        """
        Compiles a JWT signature for the given data
        :param method: HTTP Method
        :param content_hash: SHA 256 hash of the content body if it exists
        :param resource: The path (api endpoint)
        :param jti: JWT ID. This is a unique identifier for the request
        :param subject: The subject entity of the request
        :return:
        """
        current = int(time()) - self.server_time_difference
        expires = current + 5

        params = {
            "alg": self.jwt_algorithm,
            "nbf": current,
            "exp": expires,
            "iss": self.issuer,
            "sub": subject,
            "aud": self.audience,
            "iat": current,
            "jti": jti,
            "request": {
                "meth": method.upper(),
                "path": resource
            }
        }

        if content_hash is not None:
            params["request"]["hash"] = content_hash
            params["request"]["func"] = self.content_hash_algorithm

        return "IOV-JWT %s" % self._get_jwt_signature(params)

    def _get_jwt_payload(self, compact_jwt):
        try:
            return JWS().verify_compact(compact_jwt, keys=self.api_public_keys)
        except (AttributeError, BadSyntax):
            raise InvalidJWTResponse(
                "Received JWT is not valid: %s" % compact_jwt)

    @staticmethod
    def _get_content_hash(body, hash_function):
        """
        Retrieves a hash using the stored content_hash_function
        :param body: string body
        :param hash_function: function identifier hash the body
        :return: hash based on the content_hash_function
        """
        if hash_function == "S256":
            hasher = sha256
        elif hash_function == "S384":
            hasher = sha384
        elif hash_function == "S512":
            hasher = sha512
        else:
            raise InvalidAlgorithm(
                "Invalid hash algorithm {}!".format(hash_function))

        return hasher(six.b(body)).hexdigest()

    def _encrypt_request(self, data):
        """
        Encrypts the input data for the stored api_public_keys
        :param data: Information to be encrypted
        :return: JWE formatted string
        """
        jwe = JWE(json.dumps(data), alg=self.jwe_cek_encryption,
                  enc=self.jwe_claims_encryption)
        return jwe.encrypt(keys=self.api_public_keys)

    def _process_jose_request(self, method, path, subject, data=None):
        """
        Performs a JOSE request
        :param method: Request method IE get, put, post, delete
        :param path: Path or endpoint that will be hit
        :param subject: Subject for which the request is issued for
        :param data: The data that will be submitted in the body of the request
        :return:
        """
        jti = self.__get_jti()
        body = None
        if data:
            body = self._encrypt_request(data)
            content_hash = self._get_content_hash(body,
                                                  self.content_hash_algorithm)
            signature = self._build_jwt_signature(method, path, jti, subject,
                                                  content_hash=content_hash)
            headers = {"content-type": "application/jwe",
                       "Authorization": signature}
        else:
            signature = self._build_jwt_signature(method, path, jti, subject)
            headers = {"content-type": "application/jwt",
                       "Authorization": signature}
        response = getattr(self._http_client, method.lower())(path, data=body,
                                                              headers=headers)

        if response.status_code != 401:
            self.verify_jwt_response(response.headers, jti, response.data,
                                     subject)

        if response.data and not isinstance(response.data, dict):
            jwe = self.decrypt_response(response.data)
            try:
                result = json.loads(jwe)
            except (ValueError, TypeError):
                result = jwe
            response.data = result

        if isinstance(response, APIErrorResponse):
            raise LaunchKeyAPIException(response.data, response.status_code,
                                        response.reason)

        return response

    def decrypt_response(self, response):
        """
        Decrypts a response using the stored issuer private keys
        :param response: JWE encrypted string
        :return: Decrypted string
        """
        package = JWEnc().unpack(response)
        keys = list(self.issuer_private_keys)
        if 'kid' in package.headers:
            for key in self.issuer_private_keys:
                if key.kid == package.headers['kid']:
                    keys = [key]
        return JWE().decrypt(response, keys=keys).decode('utf-8')

    def decrypt_rsa_response(self, response, key_id):
        """
        Decrypts a RSA response using the stored issuer private keys
        :param response: RSA encrypted string
        :param key_id: Key ID designating who the response was encrypted for.
        :return: Decrypted string
        """
        if key_id not in self.loaded_issuer_private_keys:
            raise UnexpectedKeyID("The response was for a key id "
                                  "%s which is not recognized" %
                                  key_id)
        binary_package = b64decode(response)
        return self.loaded_issuer_private_keys[key_id].decrypt(binary_package)

    def verify_jwt_response(self, headers, jti, content_body, subject,
                            status_code=None):
        """
        Verifies a response's JWT header to be valid
        :param headers: Full headers of the response
        :param jti: The input JTI value in the initial request that returned
        the response
        :param content_body: The body of the response
        :param subject: Expected subject of the JWT
        :param status_code: Status code of the response
        :return: The JWT claims
        """
        if status_code is None:
            warnings.warn(
                "Not passing a status_code value has been deprecated and "
                "will not be allowed in the next major version",
                DeprecationWarning)

        ci_headers = {k.lower(): v for k, v in headers.items()}
        auth = headers.get('X-IOV-JWT')
        try:
            payload = self._get_jwt_payload(auth)
        except JWKESTException as reason:
            raise JWTValidationFailure("Unable to parse JWT", reason=reason)

        self._verify_jwt_payload(payload, self.audience, self.issuer, subject)

        if payload.get("jti") != jti:
            raise JWTValidationFailure(
                "JTI does not match: expected {0} but got {1}".format(
                    jti, payload.get("jti")))
        elif not payload.get('response'):
            raise JWTValidationFailure("Expected JWT to contain a response "
                                       "segment but there was none!")

        response = payload['response']
        if 'status' not in response:
            raise JWTValidationFailure("Expected JWT to contain status "
                                       "in the response segment but there "
                                       "was none!")
        elif status_code and status_code != response['status']:
            raise JWTValidationFailure("Unexpected response status value")

        self._verify_jwt_response_headers(ci_headers, response)
        self._verify_jwt_content_hash(content_body, response)
        return payload

    @staticmethod
    def _verify_jwt_response_headers(ci_headers, response):
        if 'location' in response and 'location' not in ci_headers:
            raise JWTValidationFailure(
                "Expected headers to location but there was none!")
        elif 'location' not in response and 'location' in ci_headers:
            raise JWTValidationFailure("Expected JWT to contain location "
                                       "in the response segment but there "
                                       "was none!")
        elif 'location' in response and 'location' in ci_headers \
                and response['location'] != ci_headers['location']:
            raise JWTValidationFailure("Invalid location header!")
        elif 'cache' in response and 'cache-control' not in ci_headers:
            raise JWTValidationFailure("Expected headers to contain "
                                       "cache-control but there was none!")
        elif 'cache' not in response and 'cache-control' in ci_headers:
            raise JWTValidationFailure("Expected JWT to contain cache in the "
                                       "response segment but there was none!")
        elif 'cache' in response and 'cache-control' in ci_headers and \
                response['cache'] != ci_headers['cache-control']:
            raise JWTValidationFailure("Invalid cache-control header!")

    def verify_jwt_request(self, compact_jwt, subject, method, path, body):
        """
        Verify a request's JWT
        :param compact_jwt:  The compact JWT to verify
        :param subject: The expected subject of the JWT
        :param method: The method of the request
        :param path: The path of the request
        :param body: The body of the request
        :return: The claims of the JWT
        """
        try:
            payload = self._get_jwt_payload(compact_jwt)
        except JWKESTException as reason:
            raise JWTValidationFailure("Unable to parse JWT", reason=reason)

        self._verify_jwt_payload(payload, self.audience, self.issuer, subject)

        if 'request' not in payload:
            raise JWTValidationFailure("Expected JWT to contain a request "
                                       "segment but there was none!")
        elif 'meth' not in payload['request']:
            raise JWTValidationFailure("Expected method attribute but "
                                       "there was none!")
        elif method is not None and payload['request']['meth'] != method:
            raise JWTValidationFailure(
                "Method does not match: expected {} but got {}".format(
                    payload['request']['meth'], method))
        elif 'path' not in payload['request']:
            raise JWTValidationFailure(
                "Expected path attribute but there was none!")
        elif path is not None and payload['request']['path'] != path:
            raise JWTValidationFailure(
                "Path does not match: expected {} but got {}".format(
                    payload['request']['path'], path))

        self._verify_jwt_content_hash(body, payload['request'])
        return payload

    @staticmethod
    def _verify_jwt_payload(payload, issuer, audience, subject):
        """
        Verifies a JWT's payload to be valid
        :param payload: JTW payload to verify
        :param issuer: Expected issuer of the JWT payload
        :param audience: Expected audience of the JWT payload
        :param subject: Expected subject of the JWT payload
        :return: The JWT claims
        """
        now = time()

        if payload.get('iss') != issuer:
            raise JWTValidationFailure(
                "Issuer does not match: expected %s but got %s" % (
                    issuer, payload.get('iss')))
        if payload.get('aud') != audience:
            raise JWTValidationFailure(
                "Audience does not match: expected %s but got %s" % (
                    audience, payload.get('aud')))
        elif payload.get('nbf') > now + JOSE_JWT_LEEWAY:
            seconds = payload.get('nbf') - (now + JOSE_JWT_LEEWAY)
            raise JWTValidationFailure("NBF failed by %s seconds" % seconds)
        elif payload.get('exp') < now - JOSE_JWT_LEEWAY:
            seconds = (now - JOSE_JWT_LEEWAY) - payload.get('exp')
            raise JWTValidationFailure("EXP failed by %s seconds" % seconds)
        elif payload.get('sub') != subject:
            raise JWTValidationFailure(
                "Subject does not match: expected %s but got %s" % (
                    subject, payload.get('sub')))
        elif payload.get('iat') > now + JOSE_JWT_LEEWAY:
            seconds = (payload.get('iat') - (now + JOSE_JWT_LEEWAY))
            raise JWTValidationFailure(
                "IAT failed as its %s seconds in the future" % seconds)

        return payload

    def _verify_jwt_content_hash(self, content, custom_segment):
        if not content and (
                custom_segment.get('hash') or custom_segment.get('func')):
            raise JWTValidationFailure(
                "JWT expected response body but was none!")
        elif content and not custom_segment.get('hash'):
            raise JWTValidationFailure(
                "Expected JWT to contain a hash attribute but there was none!")
        elif content and not custom_segment.get('func'):
            raise JWTValidationFailure(
                "Expected JWT to contain a func attribute but there was none!")
        elif content:
            try:
                expected_hash = self._get_content_hash(content,
                                                       custom_segment.get(
                                                           'func'))
            except InvalidAlgorithm as reason:
                raise JWTValidationFailure("Invalid algorithm in JWT",
                                           reason=reason)
            received_hash = custom_segment.get('hash')
            if received_hash != expected_hash:
                raise JWTValidationFailure(
                    "Content hash does not match: expected %s but got %s" %
                    (expected_hash, received_hash))

    def get(self, path, subject=None, **kwargs):
        """
        Performs an HTTP GET request against the LaunchKey API
        :param path: Path or endpoint that will be hit
        :param subject: Subject for which the request is issued for
        :param kwargs: Any additional KWARGs will be parameters that are
        tacked onto the url
        :return:
        """
        if subject:
            return self._process_jose_request('get', path, subject)
        return self._http_client.get(path, data=kwargs)

    def post(self, path, subject=None, **kwargs):
        """
        Performs an HTTP POST request against the LaunchKey API
        :param path: Path or endpoint that will be hit
        :param subject: Subject for which the request is issued for
        :param kwargs: Any additional KWARGs will be converted to data
        parameters
        :return:
        """
        return self._process_jose_request('post', path, subject, kwargs)

    def put(self, path, subject=None, **kwargs):
        """
        Performs an HTTP PUT request against the LaunchKey API
        :param path: Path or endpoint that will be hit
        :param subject: Subject for which the request is issued for
        :param kwargs: Any additional KWARGs will be converted to data
        parameters
        :return:
        """
        return self._process_jose_request('put', path, subject, kwargs)

    def delete(self, path, subject=None, **kwargs):
        """
        Performs an HTTP DELETE request against the LaunchKey API
        :param path: Path or endpoint that will be hit
        :param subject: Subject for which the request is issued for
        :param kwargs: Any additional KWARGs will be converted to data
        parameters
        :return:
        """
        return self._process_jose_request('delete', path, subject, kwargs)

    def patch(self, path, subject=None, **kwargs):
        """
        Performs an HTTP PATCH request against the LaunchKey API
        :param path: Path or endpoint that will be hit
        :param subject: Subject for which the request is issued for
        :param kwargs: Any additional KWARGs will be converted to data
        parameters
        :return:
        """
        return self._process_jose_request('patch', path, subject, kwargs)
