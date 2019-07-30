import unittest

from Cryptodome.PublicKey.RSA import RsaKey
from ddt import data, ddt
from jwkest import JWKESTException
from jwkest.jws import JWS
from jwkest.jwt import JWT
from mock import MagicMock, ANY, patch, call
from launchkey.transports import JOSETransport, RequestsTransport
from launchkey.transports.base import APIResponse, APIErrorResponse
from launchkey.exceptions import InvalidAlgorithm, UnexpectedAPIResponse, \
    InvalidEntityID, InvalidIssuer, InvalidPrivateKey, NoIssuerKey, \
    InvalidJWTResponse, JWTValidationFailure, LaunchKeyAPIException, \
    UnexpectedKeyID
from launchkey import JOSE_SUPPORTED_JWT_ALGS, JOSE_SUPPORTED_JWE_ALGS, JOSE_SUPPORTED_JWE_ENCS, \
    JOSE_SUPPORTED_CONTENT_HASH_ALGS, API_CACHE_TIME, VALID_JWT_ISSUER_LIST, JOSE_JWT_LEEWAY
from datetime import datetime
from jwkest.jwk import RSAKey
from uuid import uuid4
from time import time
from json import loads

valid_private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAwYKRr9BD26TDyGDDBcBdGQ4FCpIRGig0JCrupTCs4Ov+9V1t
/j+jlqw/7DJdrHoSfQngUmm34vNioU0TrbbjHpmtfCmer87mS+KKkfMDa/DNFfW6
UlONbU2kzVQfV+U8cD7LwtR/NjMUh82UcjmEs55jzwPDpEn2SnrinqwmxpFUswjy
DBxmIk8lJHgkxUiCaslyL3AvroFLcgcqqmvjYEFufpZu+Ye0FMSSqYOKL2csEghm
5DCTqKiED8SRSmc1UERV7k8ByOg4t8s1lX4YRbNYxR1ax3gaXc13o5YhUoys3UW1
ussWuUeo0h0obcI32fJxJoU6UQ8j7cr+GRhH7QIDAQABAoIBAFjRFQ0dCghGF5Zg
0yJQqGpXhPjVEgRvb38qNV6ceLzDlMIJn/KSQwNlC/HdLCF95f5+CffJjh0cmKhw
OBgDWTsyTe4vLCaFUC6ETBWw9GEWpQrvPhWLQ95nRLz5X2l4TcU3DU7fOYQm7cVn
FjtXKxFGIYlisOk3CVQmEt3BJgr83RK9s1q0IuUGWL+9mDlkbno3msHXW7HcHJdz
D4CarZB/JAl2eNb8EX+wZ8fSK8OXyG5IGClcvbQDP0tFshsgk4QYNbnU+5RoyPVu
1ybEVu9tbHAWe9ilckdh4GOry/zEgIHe3jNiZDcxux+qkqTNs+EbxuGjqcIpDIFD
hWjwagECgYEA3nmKJ47611J+vKjSUVKyN9vxU/R1hoGde7GZfLianVxL2IKRPrtZ
aaysgukCejctw7JuXAp9tIwiu0Ptom7y8+ETSIkgEpjA/eGlBa7DB/c9/wguvxeq
rUqIp2dogYPnFdRgmQJA1USorWp8tsT0oHv2jATDPGP6uOUnmPKSFEcCgYEA3qum
gDRaOaCe3HK+IfVWxNmvohlTvLSVzJbmRGGpqd6KYZ8y7AsTQbpTGIh0GH/R0OaK
vIpFDuaXUnoYUSpGGv6dfxR6vC41r6+L73HvX2Op8orL61qMhB1yOmaPQt3B78N0
Fx5j7VthAT+LUWRxVISF51Uj7/y3JyIaFCjKICsCgYAShI1SU51fdNdlvqua50Y8
TgtdUJjDtGA2XocHEZqVBIyvndaXISMFH8FQODLjl1ow0tZKxPjHoW52peXOwmto
j1B6lidcROizeSeyPGSxcgvwAW9aqo6jU/Ph80KInUEL2RydP8nDtq5PmPB+ihBO
l2LjLrZNfYjuAOz11yL/mwKBgEEWodv18a3Issczzzoz8gIms71Jc/3EN8mPDo5M
kgCyqXaxx3vSHPXoliOkt3L14goTadiE/nzFkNQuFm+bUNTROo6MGPhq9Yx+XwRG
JLeYdXQNeGA6nrp7tQk3M4dTNT51vriHTKR0Qp3PylSnbK1M86tUauXa1FrfEAp2
hebzAoGAPyAyxjVqfw7ue/KdX4a25rKM2lslBJOgEfaz1FCo3wvxY+BEsVqYdxQ9
GnLtg1qwslGgm5paVd/pkhavp6B0OR+ZCh8yh/M4tV5ihkJM2GoyeeXGTcTDZI17
v7rN++QitIL05FB/X9yr04bmfekja8/gr2kf1k7Cl9f5b6GQRFg=
-----END RSA PRIVATE KEY-----"""

valid_public_key = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAinATCdbqz0oDfcUtjzrx
vF9JNJOrZzBNCmTUpOz/VptDWpraj040eoywD3VRklmMVFt0e77Hs34BsrhchCav
mzlQmYYjL4zIzRX4B0l+U/PhC6p6RIL8D/TSk11u11sHtBycSOThYDeoPRuBo/Zq
g3rVvsYdjQ56RLEgI9JkXM5xJWEPgRE2NcCMCBjEQu3icWKUsu5boo4vT33ZhOMU
CDrajXshXvCxrp6JSb3jvoWC/lIpcDomtDnj/u9GXivsGv3Vk8YjmFlTEnr5Kb/o
3uSlCFO9bLfEGEhlBULyOeN7m2NKFvFXqfbd4hdtVbEQWBc+te9hLfAF6n13wURk
qF23lpEZCLcvql4mq/38u+MlgHshaOfYuGN5lPLZn4pRLUPPGS+Q1dYEVirLzWJx
1Ztn7Ti8qe3ePbXHF2W/+9T+udhROQNv3pJsGp7dxG3WxZB2l16v2cir0nv+jZti
JaXPf+seoEup2RckvCWhalpnUeXSJE339CkFAN1uTkvXgMWr5XRNuxBsRhz8pnLT
TxrmsAS6Onkyjhl/+ihxJasCTpN69jmwqxSFNmStzXFz6LjqUtiPIeMdiCn9dFrD
Gb2x+XCOpvFR9q+9RPP/bZxnJPmSPbQEcrjwhLerDL9qbwgHnGYXdlM9JaYYkG5y
2ZzlVAZOwr81Y9KxOGFq+w8CAwEAAQ==
-----END PUBLIC KEY-----"""


class TestJOSETransport3rdParty(unittest.TestCase):

    def setUp(self):
        self._transport = JOSETransport()
        self._transport.get = MagicMock(return_value=MagicMock(spec=APIResponse))
        public_key = APIResponse(valid_private_key,
                                 {"X-IOV-KEY-ID": "59:12:e2:f6:3f:79:d5:1e:18:75:c5:25:ff:b3:b7:f2"}, 200)
        self._transport.get.return_value = public_key
        self._transport._server_time_difference = 0, time()

    def test_public_key_parse(self):
        self._transport.get.return_value.data = valid_public_key
        keys = self._transport.api_public_keys
        self.assertEqual(len(keys), 1)
        self.assertIsInstance(keys[0], RSAKey)

    def test_build_jwt_signature_no_key(self):
        with self.assertRaises(NoIssuerKey):
            self._transport._build_jwt_signature(MagicMock(spec=str), ANY, ANY, ANY, ANY)

    def test_build_jwt_signature(self):
        self._transport.set_issuer(ANY, uuid4(), valid_private_key)
        jwt = self._transport._build_jwt_signature("PUT", "/test", str(uuid4()), "test:subject", "ABCDEFG")
        self.assertIn('IOV-JWT', jwt)
        jwt = jwt.strip('IOV-JWT ')
        self.assertEqual(len(jwt.split(".")), 3)

    def test_invalid_jwt_response(self):
        headers = {"X-IOV-JWT": 'invalid'}
        with self.assertRaises(InvalidJWTResponse):
            self._transport.verify_jwt_response(headers, ANY, ANY, ANY)

    def test_jwt_response_error(self):
        headers = {"X-IOV-JWT": 'invalid'}
        with self.assertRaises(InvalidJWTResponse):
            self._transport.verify_jwt_response(headers, ANY, ANY, ANY)

    def test_empty_jwt_response(self):
        headers = {}
        with self.assertRaises(InvalidJWTResponse):
            self._transport.verify_jwt_response(headers, ANY, ANY, ANY)

    @patch.object(JWS, 'verify_compact')
    def test_jwt_error_raises_expected_exception(self, verify_compact_patch):
        verify_compact_patch.side_effect = JWKESTException
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response({}, ANY, ANY, ANY)


class TestDecryptRSAResponse(unittest.TestCase):

    def setUp(self):
        self._transport = JOSETransport()
        patch.object(self._transport, 'loaded_issuer_private_keys',
                     {"key_id": MagicMock()}).start()
        self.addCleanup(patch.stopall)

    def test_decrypt_rsa_response(self):
        self._transport.loaded_issuer_private_keys['key_id'].decrypt.return_value = "response"
        resp = self._transport.decrypt_rsa_response('dGVzdGluZw==', 'key_id')
        self.assertEqual(resp, "response")

    def test_decrypt_rsa_decrypt_input(self):
        self._transport.loaded_issuer_private_keys['key_id'].decrypt.return_value = "response"
        self._transport.decrypt_rsa_response('dGVzdGluZw==', 'key_id')
        self._transport.loaded_issuer_private_keys['key_id'].decrypt.assert_called_with(b"testing")

    def test_decrypt_rsa_response_invalid_key(self):
        with self.assertRaises(UnexpectedKeyID):
            self._transport.decrypt_rsa_response('response', 'wrong_key')


class TestJWKESTSupportedAlgs(unittest.TestCase):

    def setUp(self):
        self._transport = JOSETransport()
        self._transport.get = MagicMock(return_value=MagicMock(spec=APIResponse))
        public_key = APIResponse(valid_private_key,
                                 {"X-IOV-KEY-ID": "59:12:e2:f6:3f:79:d5:1e:18:75:c5:25:ff:b3:b7:f2"}, 200)
        self._transport.get.return_value = public_key
        self._transport._server_time_difference = 0, time()

    def _encrypt_decrypt(self):
        self._transport.add_issuer_key(valid_private_key)
        to_encrypt = {"tobe": "encrypted"}
        encrypted = self._transport._encrypt_request(to_encrypt)
        self.assertEqual(len(encrypted.split('.')), 5)
        decrypted = self._transport.decrypt_response(encrypted)
        self.assertEqual(loads(decrypted), to_encrypt)

    def test_encrypt_decrypt_defaults(self):
        self._encrypt_decrypt()

    def test_supported_jwt_algorithms_success(self):
        for alg in JOSE_SUPPORTED_JWT_ALGS:
            self._transport.jwt_algorithm = alg
            self._encrypt_decrypt()

    def test_supported_jwe_algorithms_success(self):
        for alg in JOSE_SUPPORTED_JWE_ALGS:
            self._transport.jwe_cek_encryption = alg
            self._encrypt_decrypt()

    def test_supported_jwe_encryptions_success(self):
        for enc in JOSE_SUPPORTED_JWE_ENCS:
            self._transport.jwe_claims_encryption = enc
            self._encrypt_decrypt()


class TestHashlibSupportedAlgs(unittest.TestCase):

    def test_supported_content_hash_algorithm_success_in_construct(self):
        for alg in JOSE_SUPPORTED_CONTENT_HASH_ALGS:
            JOSETransport(content_hash_algorithm=alg)

    def test_unsupported_content_hash_algorithm_success_in_construct_raises_invalid_algorithm_error(self):
        with self.assertRaises(InvalidAlgorithm):
            JOSETransport(content_hash_algorithm="bad")

    def test_supported_content_hash_algorithm_success_in_get_content_hash(self):
        for alg in JOSE_SUPPORTED_CONTENT_HASH_ALGS:
            transport = JOSETransport()
            to_hash = str(uuid4())
            result = transport._get_content_hash(to_hash, alg)
            self.assertNotEqual(to_hash, result)

    def test_unsupported_content_hash_algorithm_success_in_get_content_hash_raises_invalid_algorithm_error(self):
            transport = JOSETransport()
            with self.assertRaises(InvalidAlgorithm):
                transport._get_content_hash(None, "invalid")


class TestJOSEProcessJOSERequest(unittest.TestCase):

    def setUp(self):
        self._http_transport = MagicMock(spec=RequestsTransport)
        self._transport = JOSETransport(http_client=self._http_transport)
        self._transport.verify_jwt_response = MagicMock()
        self._transport._build_jwt_signature = MagicMock()
        self._transport.decrypt_response = MagicMock(return_value="Decrypted Response")
        self._transport._encrypt_request = MagicMock(return_value="Encrypted Response")

    @patch('requests.get')
    def test_process_jose_request_success_encrypted_response(self, requests_patch):
        requests_patch.return_value = MagicMock()
        response = self._transport._process_jose_request('GET', '/path', 'subject', 'body')
        self._transport.decrypt_response.assert_called_once()
        self.assertEqual(response.data, self._transport.decrypt_response.return_value)

    def test_process_jose_request_success_unencrypted_response(self):
        self._transport._http_client = MagicMock()
        self._transport._http_client.get.return_value = APIResponse({"a": "response"}, {}, 200)
        response = self._transport._process_jose_request('GET', '/path', ANY)
        self._transport.decrypt_response.assert_not_called()
        self.assertIsInstance(response, APIResponse)
        self.assertEqual(response.data, {"a": "response"})
        self.assertEqual(response.status_code, 200)

    def test_process_jose_request_success_empty_response(self):
        self._transport._http_client = MagicMock()
        self._transport._http_client.get.return_value = APIResponse(None, {}, 201)
        response = self._transport._process_jose_request('GET', '/path', 'subject')
        self._transport.decrypt_response.assert_not_called()
        self.assertIsInstance(response, APIResponse)
        self.assertIsNone(response.data)
        self.assertEqual(response.status_code, 201)

    @patch('launchkey.transports.jose_auth.json')
    def test_process_jose_request_data_json_success(self, json_patch):
        json_patch.return_value = "{\"json\": true}"
        response = self._transport._process_jose_request('POST', '/path', 'subject', 'data')
        json_patch.loads.assert_called_with(self._transport.decrypt_response.return_value)
        self.assertEqual(response.data, json_patch.loads.return_value)

    def test_process_jose_request_error_response(self):
        self._transport._http_client = MagicMock()
        self._transport._http_client.put.return_value = APIErrorResponse(ANY, ANY, ANY)
        with self.assertRaises(LaunchKeyAPIException):
            self._transport._process_jose_request('PUT', '/path', 'subject')


class TestJOSETransportJWTResponse(unittest.TestCase):

    def setUp(self):
        self._transport = JOSETransport()
        self._transport.get = MagicMock(return_value=MagicMock(spec=APIResponse))
        public_key = APIResponse(valid_private_key,
                                 {"X-IOV-KEY-ID": "59:12:e2:f6:3f:79:d5:1e:18:75:c5:25:ff:b3:b7:f2"}, 200)
        self._transport.get.return_value = public_key
        self._transport._server_time_difference = 0, time()
        self.issuer = "svc"
        self.issuer_id = uuid4()
        self._transport.set_issuer(self.issuer, self.issuer_id, valid_private_key)
        self._body = str(uuid4())
        self._content_hash = '16793293daadb5a03b7cbbb9d15a1a705b22e762a1a751bc8625dec666101ff2'

        self.jwt_payload = {
            'aud': '%s:%s' % (self.issuer, self.issuer_id),
            'iss': 'lka',
            'cty': 'application/json',
            'nbf': time(),
            'jti': str(uuid4()),
            'exp': time() + 30,
            'iat': time(),
            'response': {
                'status': 200,
                'hash': self._content_hash,
                'func': 'S256',
                'cache': 'expected cache-control',
                'location': 'expected location'},
            'sub': '%s:%s' % (self.issuer, self.issuer_id)
        }

        self._headers = {'Location': 'expected location', 'Cache-Control': 'expected cache-control'}
        self._transport._get_jwt_payload = MagicMock(return_value=self.jwt_payload)
        self._transport.content_hash_function = MagicMock()
        self._transport.content_hash_function.return_value.hexdigest.return_value = self._content_hash

        patcher = patch('launchkey.transports.jose_auth.sha256')
        patched = patcher.start()
        patched.return_value = MagicMock()
        patched.return_value.hexdigest.return_value = self._content_hash
        self.addCleanup(patcher.stop)

    def _verify_jwt_response(self, headers=None, jti=None, body=False, subject=None, status_code=200):
        headers = self._headers if headers is None else headers
        jti = self.jwt_payload['jti'] if jti is None else jti
        body = MagicMock() if body is False else body
        subject = self.jwt_payload['sub'] if subject is None else subject
        return self._transport.verify_jwt_response(headers, jti, body, subject, status_code)

    def test_verify_jwt_response_success_returns_payload(self):
        actual = self._verify_jwt_response()
        self.assertEqual(actual, self.jwt_payload)

    def test_verify_jwt_response_invalid_audience(self):
        self.jwt_payload['aud'] = MagicMock()
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    @patch("launchkey.transports.jose_auth.time")
    def test_verify_jwt_response_invalid_nbf(self, time_patch):
        time_patch.return_value = self.jwt_payload['nbf'] - JOSE_JWT_LEEWAY - 1
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    @patch("launchkey.transports.jose_auth.time")
    def test_verify_jwt_response_invalid_exp(self, time_patch):
        time_patch.return_value = self.jwt_payload['exp'] + JOSE_JWT_LEEWAY + 1
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    def test_verify_jwt_response_invalid_sub(self):
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], MagicMock(), MagicMock())

    def test_verify_jwt_response_invalid_sub_401(self):
        self.jwt_payload['response']['status'] = 401
        self.jwt_payload['aud'] = "public"
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response(subject="Invalid subject")

    def test_verify_jwt_response_invalid_iat(self):
        self.jwt_payload['iat'] = time() + JOSE_JWT_LEEWAY + 1
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    def test_verify_jwt_response_invalid_content_body(self):
        self.jwt_payload['response']['hash'] = MagicMock()
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    def test_verify_jwt_response_invalid_content_jti(self):
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response(jti='InvalidJTI')

    def test_verify_no_response_raises_validation_failure(self):
        del self.jwt_payload['response']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response(body=None)

    def test_verify_no_body_but_response_body_hash_algorithm_raises_validation_failure(self):
        del self.jwt_payload['response']['hash']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response(body=None)

    def test_verify_no_body_but_response_body_hash_raises_validation_failure(self):
        del self.jwt_payload['response']['func']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response(body=None)

    def test_verify_invalid_status_code_raises_validation_failure(self):
        self.jwt_payload['response']['status'] = 999
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    def test_verify_any_status_with_no_status_code_still_passes(self):
        self.assertIsNotNone(self._verify_jwt_response(status_code=None))

    def test_verify_no_status_in_jwt_response_and_no_status_code_raises_validation_failure(self):
        del self.jwt_payload['response']['status']
        with self.assertRaises(JWTValidationFailure):
            self.assertIsNotNone(self._verify_jwt_response(status_code=None))

    def test_verify_no_cache_control_header_and_jwt_response_cache_raises_validation_failure(self):
        del self._headers['Cache-Control']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    def test_verify_cache_control_header_and_jwt_with_no_response_cache_raises_validation_failure(self):
        del self.jwt_payload['response']['cache']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    def test_verify_invalid_cache_control_header_raises_validation_failure(self):
        self.jwt_payload['response']['cache'] = "Unexpected"
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    def test_verify_no_location_header_and_jwt_response_cache_raises_validation_failure(self):
        del self._headers['Location']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    def test_verify_location_header_and_jwt_with_no_response_cache_raises_validation_failure(self):
        del self.jwt_payload['response']['location']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()

    def test_verify_invalid_location_header_raises_validation_failure(self):
        self.jwt_payload['response']['location'] = "Unexpected"
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_response()


class TestJOSETransportJWTRequest(unittest.TestCase):

    def setUp(self):
        self._transport = JOSETransport()
        self._transport.get = MagicMock(return_value=MagicMock(spec=APIResponse))
        public_key = APIResponse(valid_private_key,
                                 {"X-IOV-KEY-ID": "59:12:e2:f6:3f:79:d5:1e:18:75:c5:25:ff:b3:b7:f2"}, 200)
        self._transport.get.return_value = public_key
        self._transport._server_time_difference = 0, time()
        self.issuer = "svc"
        self.issuer_id = uuid4()
        self._transport.set_issuer(self.issuer, self.issuer_id, valid_private_key)
        self._body = str(uuid4())
        self._content_hash = '16793293daadb5a03b7cbbb9d15a1a705b22e762a1a751bc8625dec666101ff2'

        self.jwt_payload = {
            'aud': '%s:%s' % (self.issuer, self.issuer_id),
            'iss': 'lka',
            'cty': 'application/json',
            'nbf': time(),
            'jti': str(uuid4()),
            'exp': time() + 30,
            'iat': time(),
            'request': {
                'meth': 'POST',
                'path': '/',
                'hash': self._content_hash,
                'func': 'S256'},
            'sub': '%s:%s' % (self.issuer, self.issuer_id)
        }
        self._transport._get_jwt_payload = MagicMock(return_value=self.jwt_payload)
        self._transport.content_hash_function = MagicMock()

        self._transport.content_hash_function().hexdigest.return_value = self._content_hash

        patcher = patch('launchkey.transports.jose_auth.sha256')
        patched = patcher.start()
        patched.return_value = MagicMock()
        patched.return_value.hexdigest.return_value = self._content_hash
        self.addCleanup(patcher.stop)

    def _verify_jwt_request(self, compact_jwt="compact.jtw.value", subscriber=None, method='POST', path='/', body="body"):
        subscriber = self.jwt_payload['sub'] if subscriber is None else subscriber
        return self._transport.verify_jwt_request(compact_jwt, subscriber, method, path, body)

    def test_all_params_returns_payload(self):
        actual = self._verify_jwt_request()
        self.assertEqual(actual, self.jwt_payload)

    def test_none_path_returns_payload(self):
        actual = self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST', None, MagicMock())
        self.assertEqual(actual, self.jwt_payload)

    def test_none_path_still_requires_jwt_request_path(self):
        del self.jwt_payload['request']['path']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request(path=None)

    def test_none_method_returns_payload(self):
        actual = self._verify_jwt_request(method=None)
        self.assertEqual(actual, self.jwt_payload)

    def test_none_method_still_requires_jwt_request_path(self):
        del self.jwt_payload['request']['meth']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request(method=None)

    def test_invalid_audience_raises_validation_failure(self):
        self.jwt_payload['aud'] = MagicMock()
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request()

    def test_invalid_issuer_raises_validation_failure(self):
        self.jwt_payload['iss'] = MagicMock()
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request()

    @patch("launchkey.transports.jose_auth.time")
    def test_invalid_nbf_raises_validation_failure(self, time_patch):
        time_patch.return_value = self.jwt_payload['nbf'] - JOSE_JWT_LEEWAY - 1
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request()

    @patch("launchkey.transports.jose_auth.time")
    def test_invalid_exp_raises_validation_failure(self, time_patch):
        time_patch.return_value = self.jwt_payload['exp'] + JOSE_JWT_LEEWAY + 1
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request()

    def test_invalid_sub_raises_validation_failure(self):
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request(subscriber='other')

    def test_invalid_iat_raises_validation_failure(self):
        self.jwt_payload['iat'] = time() + JOSE_JWT_LEEWAY + 1
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request()

    def test_invalid_content_body_raises_validation_failure(self):
        self.jwt_payload['request']['hash'] = MagicMock()
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request()

    def test_no_body_but_response_body_hash_algorithm_raises_validation_failure(self):
        del self.jwt_payload['request']['func']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request(body=None)

    def test_no_body_but_response_body_hash_raises_validation_failure(self):
        del self.jwt_payload['request']['hash']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request(body=None)

    def test_body_but_no_response_body_hash_algorithm_raises_validation_failure(self):
        del self.jwt_payload['request']['hash']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request()

    def test_body_but_no_response_body_hash_raises_validation_failure(self):
        del self.jwt_payload['request']['func']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request()

    def test_invalid_hash_func_raises_validation_failure(self):
        self.jwt_payload['request']['func'] = 'INVALID'
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request()

    def test_no_request_raises_validation_failure(self):
        del self.jwt_payload['request']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request(method='INV')

    def test_no_method_raises_validation_failure(self):
        del self.jwt_payload['request']['meth']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request(method='INV')

    def test_invalid_method_raises_validation_failure(self):
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request(method='INV')

    def test_no_path_raises_validation_failure(self):
        del self.jwt_payload['request']['path']
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request(path='/invalid')

    def test_invalid_path_raises_validation_failure(self):
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request(path='/invalid')

    def test_invalid_jwt_raises_validation_failure(self):
        self._transport._get_jwt_payload.side_effect = JWKESTException
        with self.assertRaises(JWTValidationFailure):
            self._verify_jwt_request()


class TestJOSETransportJWT(unittest.TestCase):

    def setUp(self):
        self._transport = JOSETransport()
        self._transport.get = MagicMock(return_value=MagicMock(spec=APIResponse))
        self._transport._get_jwt_signature = MagicMock(return_value='x.x.x')
        public_key = APIResponse(valid_public_key,
                                 {"X-IOV-KEY-ID": "59:12:e2:f6:3f:79:d5:1e:18:75:c5:25:ff:b3:b7:f2"}, 200)
        self._transport.get.return_value = public_key
        self._transport._server_time_difference = 0, time()

    def test_build_jwt_signature(self):
        self._transport.set_issuer(ANY, uuid4(), valid_private_key)
        jwt = self._transport._build_jwt_signature("PUT", "/test", str(uuid4()), "test:subject", "ABCDEFG")
        self.assertIn('IOV-JWT', jwt)
        jwt = jwt.strip('IOV-JWT ')
        self.assertEqual(len(jwt.split(".")), 3)


class TestJOSETransportRESTCalls(unittest.TestCase):

    def setUp(self):
        self._http_client = MagicMock(spec=RequestsTransport)
        self._transport = JOSETransport(http_client=self._http_client)
        self._transport.verify_jwt_response = MagicMock()
        self._transport._build_jwt_signature = MagicMock()
        self._transport.content_hash_function = MagicMock()
        self._transport.decrypt_response = MagicMock()
        self._transport._encrypt_request = MagicMock()

    def test_get(self):
        self.assertEqual(self._transport.get('/path'), self._http_client.get.return_value)

    def test_get_with_subject(self):
        self.assertEqual(self._transport.get('/path', ANY), self._http_client.get.return_value)

    def test_post(self):
        self.assertEqual(self._transport.post('/path', ANY), self._http_client.post.return_value)

    def test_put(self):
        self.assertEqual(self._transport.put('/path', ANY), self._http_client.put.return_value)

    def test_delete(self):
        self.assertEqual(self._transport.delete('/path', ANY), self._http_client.delete.return_value)

    def test_patch(self):
        self.assertEqual(self._transport.patch('/path', ANY), self._http_client.patch.return_value)


class TestJOSETransportIssuers(unittest.TestCase):

    def setUp(self):
        self._transport = JOSETransport()

    def test_add_issuer_key(self):
        self.assertEqual(len(self._transport.issuer_private_keys), 0)
        self._transport.add_issuer_key(valid_private_key)
        self.assertEqual(len(self._transport.issuer_private_keys), 1)

    def test_add_duplicate_issuer_key(self):
        self.assertEqual(len(self._transport.issuer_private_keys), 0)
        self._transport.add_issuer_key(valid_private_key)
        self.assertEqual(len(self._transport.issuer_private_keys), 1)
        resp = self._transport.add_issuer_key(valid_private_key)
        self.assertFalse(resp)
        self.assertEqual(len(self._transport.issuer_private_keys), 1)

    def test_generate_key_id(self):
        self._transport.add_issuer_key(valid_private_key)
        self.assertEqual(self._transport.issuer_private_keys[0].kid,
                         '59:12:e2:f6:3f:79:d5:1e:18:75:c5:25:ff:b3:b7:f2')

    def test_set_url(self):
        self._transport._http_client = MagicMock()
        self._transport.set_url(ANY, ANY)
        self._transport._http_client.set_url.assert_called_once()

    def test_set_issuer_invalid_entity_id(self):
        with self.assertRaises(InvalidEntityID):
            self._transport.set_issuer(ANY, ANY, ANY)

    def test_set_issuer_invalid_entity_issuer(self):
        with self.assertRaises(InvalidIssuer):
            self._transport.set_issuer(MagicMock(spec=str), uuid4(), ANY)

    def test_set_issuer_invalid_private_key(self):
        with self.assertRaises(InvalidPrivateKey):
            self._transport.set_issuer(ANY, uuid4(), "InvalidKey")

    @patch("launchkey.transports.jose_auth.RSAKey")
    @patch("launchkey.transports.jose_auth.import_rsa_key")
    def test_issuer_list(self, rsa_key_patch, import_key_patch):
        rsa_key_patch.return_value = MagicMock(spec=RSAKey)
        import_key_patch.return_value = MagicMock()
        self._transport.add_issuer_key = MagicMock()
        for issuer in VALID_JWT_ISSUER_LIST:
            self._transport.set_issuer(issuer, uuid4(), ANY)

class TestJOSETransportAPIPing(unittest.TestCase):

    def setUp(self):
        self._transport = JOSETransport()
        self._transport.get = MagicMock(return_value=MagicMock(spec=APIResponse))

    def test_server_time_difference_invalid_timestamp(self):
        self._transport.get.return_value.data = {"api_time": ANY}
        with self.assertRaises(UnexpectedAPIResponse):
            self._transport.server_time_difference

    def test_server_time_difference_invalid_response(self):
        self._transport.get.return_value.data = ANY
        with self.assertRaises(UnexpectedAPIResponse):
            self._transport.server_time_difference

    def test_server_time_difference_success(self):
        self._transport.get.return_value.data = {"api_time": str(datetime.utcnow())[:19].replace(" ", "T") + "Z"}
        self.assertEqual(0, self._transport.server_time_difference)

    def test_server_time_difference_caching_once(self):
        self._transport.get.return_value.data = {"api_time": str(datetime.utcnow())[:19].replace(" ", "T") + "Z"}
        for i in range(0, 10):
            self._transport.server_time_difference
        self._transport.get.assert_called_once()

    @patch("launchkey.transports.jose_auth.time")
    def test_server_time_difference_cache_expiration(self, time_patch):
        self._transport.get.return_value.data = {"api_time": str(datetime.utcnow())[:19].replace(" ", "T") + "Z"}
        call_count = 10
        time_patch.return_value = 0
        for i in range(0, call_count):
            self._transport.server_time_difference
            time_patch.return_value += API_CACHE_TIME + 1
        self.assertEqual(self._transport.get.call_count, call_count)

    def test_api_public_keys_invalid_response(self):
        self._transport.get.return_value.data = ANY
        with self.assertRaises(UnexpectedAPIResponse):
            self._transport.api_public_keys

    def test_api_public_keys_empty_response(self):
        self._transport.get.return_value.data = ""
        with self.assertRaises(UnexpectedAPIResponse):
            self._transport.api_public_keys

    def test_api_public_keys_invalid_public_key(self):
        self._transport.get.return_value.data = "InvalidPublicKey"
        with self.assertRaises(UnexpectedAPIResponse):
            self._transport.api_public_keys

    @patch("launchkey.transports.jose_auth.RSAKey")
    def test_api_public_keys_success(self, rsa_key_patch):
        rsa_key_patch.return_value = MagicMock(spec=RSAKey)
        self._transport.get.return_value.data = valid_public_key
        keys = self._transport.api_public_keys
        self.assertEqual(len(keys), 1)
        self.assertIsInstance(keys[0], RSAKey)

    @patch("launchkey.transports.jose_auth.RSAKey")
    def test_api_public_keys_caching_once(self, rsa_key_patch):
        rsa_key_patch.return_value = MagicMock(spec=RSAKey)
        self._transport.get.return_value.data = valid_public_key
        for i in range(0, 10):
            self._transport.api_public_keys
        self._transport.get.assert_called_once()

    @patch("launchkey.transports.jose_auth.time")
    @patch("launchkey.transports.jose_auth.RSAKey")
    def test_api_public_keys_cache_expiration(self, rsa_key_patch, time_patch):
        rsa_key_patch.return_value = MagicMock(spec=RSAKey)
        self._transport.get.return_value.data = valid_public_key
        call_count = 10
        time_patch.return_value = 0
        for i in range(0, call_count):
            self._transport.api_public_keys
            time_patch.return_value += API_CACHE_TIME + 1
        self.assertEqual(self._transport.get.call_count, call_count)


@ddt
class TestJOSETransportSupportedAlgorithms(unittest.TestCase):

    @data("RS256", "RS384", "RS512")
    def test_supported_jwt_algorithms_success(self, alg):
        transport = JOSETransport(jwt_algorithm=alg)
        self.assertEqual(transport.jwt_algorithm, alg)

    def test_supported_jwt_algorithms_failure(self):
        with self.assertRaises(InvalidAlgorithm):
            JOSETransport(jwt_algorithm="Invalid")

    @data('RSA-OAEP')
    def test_supported_jwe_algorithms_success(self, alg):
        transport = JOSETransport(jwe_cek_encryption=alg)
        self.assertEqual(transport.jwe_cek_encryption, alg)

    def test_supported_jwe_algorithms_failure(self):
        with self.assertRaises(InvalidAlgorithm):
            JOSETransport(jwe_cek_encryption="Invalie")

    @data('A256CBC-HS512')
    def test_supported_jwe_encryptions_success(self, enc):
        transport = JOSETransport(jwe_claims_encryption=enc)
        self.assertEqual(transport.jwe_claims_encryption, enc)

    def test_supported_jwe_encryptions_failure(self):
        with self.assertRaises(InvalidAlgorithm):
            JOSETransport(jwe_claims_encryption="Invalid")

    @data("S256", "S384", "S512")
    def test_supported_content_hash_algorithm_success(self, alg):
        transport = JOSETransport(content_hash_algorithm=alg)
        self.assertEqual(transport.content_hash_algorithm, alg)

    def test_supported_content_hash_algorithm_failure(self):
        with self.assertRaises(InvalidAlgorithm):
            JOSETransport(content_hash_algorithm="Invalid")


class TestTempKeyID(unittest.TestCase):
    def setUp(self):
        self._requests_transport = MagicMock(spec=RequestsTransport)
        self._requests_transport.get.return_value = MagicMock(spec=APIResponse)

        patch.object(JOSETransport, "_verify_jwt_payload").start()
        patch.object(JOSETransport, "_verify_jwt_response_headers").start()
        patch.object(JOSETransport, "_verify_jwt_content_hash").start()

        self._transport = JOSETransport(http_client=self._requests_transport)
        self._import_rsa_key_patch = patch(
            "launchkey.transports.jose_auth.import_rsa_key",
            return_value=MagicMock(spec=RsaKey)).start()
        self._jwt_patch = patch("launchkey.transports.jose_auth.JWT", return_value=MagicMock(spec=JWT)).start()

        self.jti = str(uuid4())
        self._faux_kid = "59:12:e2:f6:3f:79:d5:1e:18:75:c5:25:ff:b3:b7:f2"

        jwt_headers = {
            "alg": "RS512",
            "typ": "JWT",
            "kid": self._faux_kid
        }

        minified_jwt_payload = {
            "jti": self.jti,
            "response": {"status": 200}
        }

        self._jwt_patch.return_value.unpack.return_value.headers = jwt_headers
        self._jws_patch = patch("launchkey.transports.jose_auth.JWS", return_value=MagicMock(spec=JWS)).start()
        self._jws_patch.return_value.verify_compact.return_value = minified_jwt_payload

        self.addCleanup(patch.stopall)

    def test_key_retrieved_by_id_in_jwt_header(self):
        self._transport.verify_jwt_response(MagicMock(), self.jti, ANY, None)
        self._requests_transport.get.assert_called_once_with(
            "/public/v3/public-key/%s" % self._faux_kid,
            data={})

    def test_key_is_cached_by_id(self):
        self._transport.verify_jwt_response(MagicMock(), self.jti, ANY, None)
        self._transport.verify_jwt_response(MagicMock(), self.jti, ANY, None)
        self._requests_transport.get.assert_called_once()

    def test_key_is_retrieved_by_id_when_key_changed(self):
        jwt1 = MagicMock()
        jwt1.headers = {
            "alg": "RS512",
            "typ": "JWT",
            "kid": "jwt1keyid"
        }

        jwt2 = MagicMock()
        jwt2.headers = {
            "alg": "RS512",
            "typ": "JWT",
            "kid": "jwt2keyid"
        }

        self._jwt_patch.return_value.unpack.side_effect = [jwt1, jwt1, jwt2, jwt2]

        self._transport.verify_jwt_response(MagicMock(), self.jti, ANY, None)
        self._transport.verify_jwt_response(MagicMock(), self.jti, ANY, None)
        self._requests_transport.get.assert_has_calls([
            call('/public/v3/public-key/jwt1keyid', data={}),
            call('/public/v3/public-key/jwt2keyid', data={})
        ], any_order=True)

    @patch("launchkey.transports.jose_auth.RSAKey")
    def test_key_retrieved_is_used_to_verify_payload(self, rsa_key_patch):
        self._transport.verify_jwt_response(MagicMock(), self.jti, ANY, None)

        # Verify that verify_compact is called one time with key created by our jwkest key patch
        self._jws_patch.return_value.verify_compact.assert_called_once_with(ANY, keys=[rsa_key_patch.return_value])

        # Assert that the jwkest key patch is built using the import_rsa_key patch return value and the key id
        # from the header
        rsa_key_patch.assert_called_with(key=self._import_rsa_key_patch.return_value, kid=self._faux_kid)

        # Verify that we used the correct key to retrieve the key id from the header
        self._requests_transport.get.return_value.headers.get.assert_called_with("X-IOV-JWT")