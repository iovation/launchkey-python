"""LaunchKey Service SDK module"""
from six import add_move, MovedAttribute
from .utils import *

add_move(MovedAttribute('encodebytes',
                        'base64', 'base64',
                        'encodestring', 'encodebytes'))

SDK_VERSION = '3.3.0'
LAUNCHKEY_PRODUCTION = "https://api.launchkey.com"
VALID_JWT_ISSUER_LIST = ["svc", "dir", "org"]
JOSE_SUPPORTED_JWE_ALGS = ['RSA-OAEP']
JOSE_SUPPORTED_JWE_ENCS = ['A256CBC-HS512']
JOSE_SUPPORTED_JWT_ALGS = ["RS256", "RS384", "RS512"]
JOSE_SUPPORTED_CONTENT_HASH_ALGS = ["S256", "S384", "S512"]
JOSE_AUDIENCE = "lka"
JOSE_JWT_LEEWAY = 30
API_CACHE_TIME = 300
