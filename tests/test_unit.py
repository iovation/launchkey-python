import unittest
from launchkey import generate_rsa
from mock import patch


def verify_sign(pub_key, signature, data):
    """
        Verifies with a public key from whom the data came that it was indeed
        signed by their private key.
    """
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA256
    from base64 import b64decode
    rsakey = RSA.importKey(pub_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(b64decode(data))
    try:
        if signer.verify(digest, b64decode(signature)):
            return True
    except ValueError:
        pass
    return False


class UnitTestAPI(unittest.TestCase):
    def test_generate_rsa(self):
        private_key, public_key = generate_rsa()
        self.assertEqual("-----BEGIN RSA PRIVATE KEY-----", private_key[:31])
        self.assertEqual("-----END RSA PRIVATE KEY-----", private_key[-29:])
        self.assertEqual("-----BEGIN PUBLIC KEY-----", public_key[:26])
        self.assertEqual("-----END PUBLIC KEY-----", public_key[-24:])
        assert len(private_key) > len(public_key) * 3
        private_key, public_key = generate_rsa(1024)
        self.assertEqual("-----BEGIN RSA PRIVATE KEY-----", private_key[:31])
        self.assertEqual("-----END RSA PRIVATE KEY-----", private_key[-29:])
        self.assertEqual("-----BEGIN PUBLIC KEY-----", public_key[:26])
        self.assertEqual("-----END PUBLIC KEY-----", public_key[-24:])
        assert len(private_key) > len(public_key) * 3

    def test_encrypt_rsa(self):
        from launchkey import encrypt_rsa
        private_key, public_key = generate_rsa()
        encrypted = encrypt_rsa(public_key, "#" * 214)
        assert len(encrypted) > 300
        assert "#" * 214 not in encrypted
        self.assertRaises(ValueError, encrypt_rsa, public_key, "#" * 215)

    def test_decrypt_rsa(self):
        from launchkey import encrypt_rsa, decrypt_rsa
        private_key, public_key = generate_rsa()
        encrypted = encrypt_rsa(public_key, "test message " * 5)
        decrypted = decrypt_rsa(private_key, encrypted)
        self.assertEqual(decrypted, "test message " * 5)

    def test_sign_data(self):
        from launchkey import encrypt_rsa, sign_data
        private_key, public_key = generate_rsa()
        encrypted = encrypt_rsa(public_key, "test message")
        private_key2, public_key2 = generate_rsa()
        signature = sign_data(private_key2, encrypted)
        self.assertTrue(verify_sign(public_key2, signature, encrypted))
        self.assertFalse(verify_sign(public_key, signature, encrypted))
        o_signature = sign_data(private_key, encrypted)
        self.assertFalse(verify_sign(public_key2, o_signature, encrypted))
        self.assertTrue(verify_sign(public_key, o_signature, encrypted))

    def test_policy_all_factors_properly_json_encodes(self):
        from launchkey import Policy
        import json
        expected = json.loads('{' +
                              '"minimum_requirements":[' +
                              '{"requirement":"authenticated","all":3,"knowledge":0,"inherence":0,"possession":0}' +
                              '],' +
                              '"factors":[]' +
                              '}')
        policy = Policy(all=3)
        actual = json.loads(json.dumps(policy))
        self.assertEqual(expected, actual)

    def test_policy_required_knowledge_factor_properly_json_encodes(self):
        from launchkey import Policy
        import json
        expected = json.loads('{' +
                              '"minimum_requirements":[' +
                              '{"requirement":"authenticated","all":0,"knowledge":1,"inherence":0,"possession":0}' +
                              '],' +
                              '"factors":[]' +
                              '}')
        policy = Policy(knowledge=True)
        actual = json.loads(json.dumps(policy))
        self.assertEqual(expected, actual)

    def test_policy_required_inherence_factor_properly_json_encodes(self):
        from launchkey import Policy
        import json
        expected = json.loads('{' +
                              '"minimum_requirements":[' +
                              '{"requirement":"authenticated","all":0,"knowledge":0,"inherence":1,"possession":0}' +
                              '],' +
                              '"factors":[]' +
                              '}')
        policy = Policy(inherence=True)
        actual = json.loads(json.dumps(policy))
        self.assertEqual(expected, actual)

    def test_policy_required_possession_factor_properly_json_encodes(self):
        from launchkey import Policy
        import json
        expected = json.loads('{' +
                              '"minimum_requirements":[' +
                              '{"requirement":"authenticated","all":0,"knowledge":0,"inherence":0,"possession":1}' +
                              '],' +
                              '"factors":[]' +
                              '}')
        policy = Policy(possession=True)
        actual = json.loads(json.dumps(policy))
        self.assertEqual(expected, actual)

    def test_policy_required_all_factors_properly_json_encodes(self):
        from launchkey import Policy
        import json
        expected = json.loads('{' +
                              '"minimum_requirements": [' +
                              '{"requirement":"authenticated","all":0,"knowledge":1,"inherence":1,"possession":1}' +
                              '],' +
                              '"factors":[]' +
                              '}')
        policy = Policy(knowledge=True, inherence=True, possession=True)
        actual = json.loads(json.dumps(policy))
        self.assertEqual(expected, actual)

    def test_policy_raises_error_when_all_factors_and_required_factors_together(self):
        from launchkey import Policy
        with self.assertRaises(AttributeError):
            Policy(all=1, knowledge=True, inherence=True, possession=True)

    def test_locations_properly_json_encodes(self):
        from launchkey import Policy
        import json
        expected = json.loads('{' +
                              '"minimum_requirements": [' +
                              '{"requirement": "authenticated","all":0,"knowledge":0,"inherence":0,"possession":0}' +
                              '],' +
                              '"factors":[' +
                              '{"factor":"geofence","requirement":"forced requirement",' +
                              '"quickfail":true,"priority":1,"attributes":{"locations":[' +
                              '{"radius":11.1,"latitude":12.2,"longitude":13.3},' +
                              '{"radius":21.1,"latitude":22.2,"longitude":23.3}' +
                              ']}}' +
                              ']' +
                              '}')
        policy = Policy()
        policy.add_location(radius=11.1, latitude=12.2, longitude=13.3)
        policy.add_location(radius=21.1, latitude=22.2, longitude=23.3)
        actual = json.loads(json.dumps(policy))

        self.assertEqual(expected, actual)

    @patch('requests.get')
    @patch('requests.post')
    def test_authorize_passes_correct_policy(self, post_patch, get_patch):
        from mock import MagicMock
        import json
        from requests.models import Response
        from launchkey import API, Policy

        ping_response = Response()
        ping_response.json = MagicMock(return_value={
            "date_stamp": "2013-04-20 21:40:02",
            "api_time": "2015-04-23 05:25:24",
            "key": "-----BEGIN PUBLIC KEY-----\n\n" +
                   "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8zQos4iDSjmUVrFUAg5G\n" +
                   "uhU6GehNKb8MCXFadRWiyLGjtbGZAk8fusQU0Uj9E3o0mne0SYESACkhyK+3M1Er\n" +
                   "bHlwYJHN0PZHtpaPWqsRmNzui8PvPmhm9QduF4KBFsWu1sBw0ibBYsLrua67F/wK\n" +
                   "PaagZRnUgrbRUhQuYt+53kQNH9nLkwG2aMVPxhxcLJYPzQCat6VjhHOX0bgiNt1i\n" +
                   "HRHU2phxBcquOW2HpGSWcpzlYgFEhPPQFAxoDUBYZI3lfRj49gBhGQi32qQ1YiWp\n" +
                   "aFxOB8GA0Ny5SfI67u6w9Nz9Z9cBhcZBfJKdq5uRWjZWslHjBN3emTAKBpAUPNET\n" +
                   "nwIDAQAB\n\n-----END PUBLIC KEY-----\n"
        })

        post_response = Response()
        post_response.json = MagicMock(return_value={"auth_request": "auth request"})

        get_patch.return_value = ping_response
        post_patch.return_value = post_response
        private_key, public_key = generate_rsa()
        policy = Policy()
        expected = json.dumps(policy)

        api = API("app key", "secret key", private_key)
        api.authorize("username", policy=policy)

        self.assertTrue(post_patch.called, 'Expected requests.post to be called but was not')
        args, kwargs = post_patch.call_args
        self.assertIn('policy', kwargs['params'])
        self.assertEqual(expected, kwargs['params']['policy'])
