import unittest

from jwkest import JWKESTException
from jwkest.jws import JWS
from mock import MagicMock, ANY, patch
from launchkey.transports import JOSETransport, RequestsTransport
from launchkey.transports.base import APIResponse, APIErrorResponse
from launchkey.exceptions import InvalidAlgorithm, UnexpectedAPIResponse, InvalidEntityID, InvalidIssuer, \
    InvalidPrivateKey, NoIssuerKey, InvalidJWTResponse, JWTValidationFailure, LaunchKeyAPIException
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

    def test_supported_content_hash_algorithm_success(self):
        for alg in JOSE_SUPPORTED_CONTENT_HASH_ALGS:
            transport = JOSETransport(content_hash_algorithm=alg)
            to_hash = str(uuid4())
            result = transport._get_content_hash(to_hash)
            self.assertNotEqual(to_hash, result)


class TestJOSEProcessJOSERequest(unittest.TestCase):

    def setUp(self):
        self._http_transport = MagicMock(spec=RequestsTransport)
        self._transport = JOSETransport(http_client=self._http_transport)
        self._transport.verify_jwt_response = MagicMock()
        self._transport._build_jwt_signature = MagicMock()
        self._transport.content_hash_function = MagicMock()
        self._transport.decrypt_response = MagicMock()
        self._transport._encrypt_request = MagicMock()

    @patch('requests.get')
    def test_process_jose_request_success_encrypted_response(self, requests_patch):
        requests_patch.return_value = MagicMock()
        response = self._transport._process_jose_request('GET', '/path', ANY)
        self._transport.decrypt_response.assert_called_once()
        self.assertEqual(response.data, self._transport.decrypt_response.return_value)

    def test_process_jose_request_success_unencrypted_response(self):
        self._transport._http_client = MagicMock()
        self._transport._http_client.get.return_value = APIResponse({"a": "response"}, ANY, 200)
        response = self._transport._process_jose_request('GET', '/path', ANY)
        self._transport.decrypt_response.assert_not_called()
        self.assertIsInstance(response, APIResponse)
        self.assertEqual(response.data, {"a": "response"})
        self.assertEqual(response.status_code, 200)

    def test_process_jose_request_success_empty_response(self):
        self._transport._http_client = MagicMock()
        self._transport._http_client.get.return_value = APIResponse(None, ANY, 201)
        response = self._transport._process_jose_request('GET', '/path', ANY)
        self._transport.decrypt_response.assert_not_called()
        self.assertIsInstance(response, APIResponse)
        self.assertIsNone(response.data)
        self.assertEqual(response.status_code, 201)

    @patch('launchkey.transports.jose_auth.json')
    def test_process_jose_request_data_json_success(self, json_patch):
        json_patch.return_value = MagicMock()
        response = self._transport._process_jose_request('POST', '/path', ANY, ANY)
        json_patch.loads.assert_called_with(self._transport.decrypt_response.return_value)
        self.assertEqual(response.data, json_patch.loads.return_value)

    def test_process_jose_request_error_response(self):
        self._transport._http_client = MagicMock()
        self._transport._http_client.put.return_value = APIErrorResponse(ANY, ANY, ANY)
        with self.assertRaises(LaunchKeyAPIException):
            self._transport._process_jose_request('PUT', '/path', ANY)


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
                'func': 'S256'},
            'sub': '%s:%s' % (self.issuer, self.issuer_id)
        }
        self._transport._get_jwt_payload = MagicMock(return_value=self.jwt_payload)
        self._transport.content_hash_function = MagicMock()
        self._transport.content_hash_function.return_value.hexdigest.return_value = self._content_hash

        patcher = patch('launchkey.transports.jose_auth.sha256')
        patched = patcher.start()
        patched.return_value = MagicMock()
        patched.return_value.hexdigest.return_value = self._content_hash
        self.addCleanup(patcher.stop)

    def test_verify_jwt_response_success_returns_payload(self):
        actual = self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], MagicMock(),
                                                     self.jwt_payload['sub'])
        self.assertEqual(actual, self.jwt_payload)

    def test_verify_jwt_response_invalid_audience(self):
        self.jwt_payload['aud'] = MagicMock()
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], MagicMock(),
                                                self.jwt_payload['sub'])

    @patch("launchkey.transports.jose_auth.time")
    def test_verify_jwt_response_invalid_nbf(self, time_patch):
        time_patch.return_value = self.jwt_payload['nbf'] - JOSE_JWT_LEEWAY - 1
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], MagicMock(),
                                                self.jwt_payload['sub'])

    @patch("launchkey.transports.jose_auth.time")
    def test_verify_jwt_response_invalid_exp(self, time_patch):
        time_patch.return_value = self.jwt_payload['exp'] + JOSE_JWT_LEEWAY + 1
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], MagicMock(),
                                                self.jwt_payload['sub'])

    def test_verify_jwt_response_invalid_sub(self):
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], MagicMock(), MagicMock())

    def test_verify_jwt_response_invalid_sub_401(self):
        self.jwt_payload['response']['status'] = 401
        self.jwt_payload['aud'] = "public"
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], MagicMock(), MagicMock())

    def test_verify_jwt_response_invalid_iat(self):
        self.jwt_payload['iat'] = time() + JOSE_JWT_LEEWAY + 1
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], MagicMock(),
                                                self.jwt_payload['sub'])

    def test_verify_jwt_response_invalid_content_body(self):
        self.jwt_payload['response']['hash'] = MagicMock()
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], MagicMock(),
                                                self.jwt_payload['sub'])

    def test_verify_jwt_response_invalid_content_jti(self):
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), 'InvalidJTI', MagicMock(), self.jwt_payload['sub'])

    def test_verify_no_body_but_response_body_hash_algorithm_raises_validation_failure(self):
        del self.jwt_payload['response']['hash']
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], None, self.jwt_payload['sub'])

    def test_verify_no_body_but_response_body_hash_raises_validation_failure(self):
        del self.jwt_payload['response']['func']
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_response(MagicMock(), self.jwt_payload['jti'], None, self.jwt_payload['sub'])


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
                'method': 'POST',
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

    def test_all_params_returns_payload(self):
        actual = self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST', '/', MagicMock())
        self.assertEqual(actual, self.jwt_payload)

    def test_none_path_returns_payload(self):
        actual = self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST', None, MagicMock())
        self.assertEqual(actual, self.jwt_payload)

    def test_none_path_still_requires_jwt_request_path(self):
        del self.jwt_payload['request']['path']
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST', None, MagicMock())

    def test_none_method_returns_payload(self):
        actual = self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], None, '/', MagicMock())
        self.assertEqual(actual, self.jwt_payload)

    def test_none_method_still_requires_jwt_request_path(self):
        del self.jwt_payload['request']['method']
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], None, '/', MagicMock())

    def test_invalid_audience_raises_validation_failure(self):
        self.jwt_payload['aud'] = MagicMock()
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST', '/', MagicMock())

    def test_no_authoprization_raises_validation_failure(self):
        self.jwt_payload['aud'] = MagicMock()
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST',
                                               '/', MagicMock())

    @patch("launchkey.transports.jose_auth.time")
    def test_invalid_nbf_raises_validation_failure(self, time_patch):
        time_patch.return_value = self.jwt_payload['nbf'] - JOSE_JWT_LEEWAY - 1
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST',
                                               '/', MagicMock())

    @patch("launchkey.transports.jose_auth.time")
    def test_invalid_exp_raises_validation_failure(self, time_patch):
        time_patch.return_value = self.jwt_payload['exp'] + JOSE_JWT_LEEWAY + 1
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST',
                                               '/', MagicMock())

    def test_invalid_sub_raises_validation_failure(self):
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), 'other', 'POST', '/', MagicMock())

    def test_invalid_iat_raises_validation_failure(self):
        self.jwt_payload['iat'] = time() + JOSE_JWT_LEEWAY + 1
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST',
                                               '/', MagicMock())

    def test_invalid_content_body_raises_validation_failure(self):
        self.jwt_payload['request']['hash'] = MagicMock()
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST',
                                               '/', MagicMock())

    def test_no_body_but_response_body_hash_algorithm_raises_validation_failure(self):
        del self.jwt_payload['request']['hash']
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST',
                                               '/', None)

    def test_no_body_but_response_body_hash_raises_validation_failure(self):
        del self.jwt_payload['request']['func']
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST',
                                               '/', None)

    def test_no_request_raises_validation_failure(self):
        del self.jwt_payload['request']
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'INV', '/', None)

    def test_no_method_raises_validation_failure(self):
        del self.jwt_payload['request']['method']
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'INV',
                                               '/', MagicMock())

    def test_invalid_method_raises_validation_failure(self):
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'INV',
                                               '/', MagicMock())

    def test_no_path_raises_validation_failure(self):
        del self.jwt_payload['request']['path']
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'INV', '/', None)

    def test_invalid_path_raises_validation_failure(self):
        with self.assertRaises(JWTValidationFailure):
            self._transport.verify_jwt_request(MagicMock(), self.jwt_payload['sub'], 'POST',
                                               '/invalid', MagicMock())


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

class TestJOSETransportSupportedAlgorithms(unittest.TestCase):

    def test_supported_jwt_algorithms_success(self):
        for alg in JOSE_SUPPORTED_JWT_ALGS:
            transport = JOSETransport(jwt_algorithm=alg)
            self.assertEqual(transport.jwt_algorithm, alg)

    def test_supported_jwt_algorithms_failure(self):
        with self.assertRaises(InvalidAlgorithm):
            JOSETransport(jwt_algorithm=MagicMock(spec=str))

    def test_supported_jwe_algorithms_success(self):
        for alg in JOSE_SUPPORTED_JWE_ALGS:
            transport = JOSETransport(jwe_cek_encryption=alg)
            self.assertEqual(transport.jwe_cek_encryption, alg)

    def test_supported_jwe_algorithms_failure(self):
        with self.assertRaises(InvalidAlgorithm):
            JOSETransport(jwe_cek_encryption=MagicMock(spec=str))

    def test_supported_jwe_encryptions_success(self):
        for enc in JOSE_SUPPORTED_JWE_ENCS:
            transport = JOSETransport(jwe_claims_encryption=enc)
            self.assertEqual(transport.jwe_claims_encryption, enc)

    def test_supported_jwe_encryptions_failure(self):
        with self.assertRaises(InvalidAlgorithm):
            JOSETransport(jwe_claims_encryption=MagicMock(spec=str))

    def test_supported_content_hash_algorithm_success(self):
        for alg in JOSE_SUPPORTED_CONTENT_HASH_ALGS:
            transport = JOSETransport(content_hash_algorithm=alg)
            self.assertEqual(transport.content_hash_algorithm, alg)

    def test_supported_content_hash_algorithm_failure(self):
        with self.assertRaises(InvalidAlgorithm):
            JOSETransport(content_hash_algorithm=MagicMock(spec=str))
