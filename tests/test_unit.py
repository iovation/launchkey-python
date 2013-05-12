import unittest
from launchkey import generate_RSA

def verify_sign(pub_key, signature, data):
    ''' 
        Verifies with a public key from whom the data came that it was indeed
        signed by their private key.
    '''
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA256
    from base64 import b64decode
    rsakey = RSA.importKey(pub_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(b64decode(data))
    if signer.verify(digest, b64decode(signature)):
        return True
    return False

class UnitTestAPI(unittest.TestCase):

    def test_generate_RSA(self):
        private_key, public_key = generate_RSA()
        self.assertEquals("-----BEGIN RSA PRIVATE KEY-----", private_key[:31])
        self.assertEquals("-----END RSA PRIVATE KEY-----", private_key[-29:])
        self.assertEquals("-----BEGIN PUBLIC KEY-----", public_key[:26])
        self.assertEquals("-----END PUBLIC KEY-----", public_key[-24:])
        assert len(private_key) > len(public_key) * 3
        private_key, public_key = generate_RSA(1024)
        self.assertEquals("-----BEGIN RSA PRIVATE KEY-----", private_key[:31])
        self.assertEquals("-----END RSA PRIVATE KEY-----", private_key[-29:])
        self.assertEquals("-----BEGIN PUBLIC KEY-----", public_key[:26])
        self.assertEquals("-----END PUBLIC KEY-----", public_key[-24:])
        assert len(private_key) > len(public_key) * 3

    def test_encrypt_RSA(self):
        from launchkey import encrypt_RSA
        private_key, public_key = generate_RSA()
        encrypted = encrypt_RSA(public_key, "#" * 214)
        assert len(encrypted) > 300
        assert "#" * 214 not in encrypted
        self.assertRaises(ValueError, encrypt_RSA, public_key, "#" * 215)

    def test_decrypt_RSA(self):
        from launchkey import encrypt_RSA, decrypt_RSA
        private_key, public_key = generate_RSA()
        encrypted = encrypt_RSA(public_key, "test message " * 5)
        decrypted = decrypt_RSA(private_key, encrypted)
        self.assertEquals(decrypted, "test message " * 5)

    def test_sign_data(self):
        from launchkey import encrypt_RSA, decrypt_RSA, sign_data
        from Crypto.PublicKey import RSA
        private_key, public_key = generate_RSA()
        encrypted = encrypt_RSA(public_key, "test message")
        private_key2, public_key2 = generate_RSA()
        signature = sign_data(private_key2, encrypted)
        self.assertTrue(verify_sign(public_key2, signature, encrypted))
        self.assertFalse(verify_sign(public_key, signature, encrypted))
        o_signature = sign_data(private_key, encrypted)
        self.assertFalse(verify_sign(public_key2, o_signature, encrypted))
        self.assertTrue(verify_sign(public_key, o_signature, encrypted))
