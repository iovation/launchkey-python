"""Entities shared across domains"""

# pylint: disable=invalid-name,too-few-public-methods

from enum import Enum


class KeyType(Enum):
    """
    An enum that represents what a key is to be used for, i.e. signature,
    encryption, or both.
    """
    BOTH = 0
    ENCRYPTION = 1
    SIGNATURE = 2
    OTHER = -1


class PublicKey(object):
    """
    Public key object signifying a public key belonging to an Organization,
    Directory, or Service
    """

    def __init__(self, public_key_data):
        self.id = public_key_data['id']
        self.active = public_key_data['active']
        self.created = public_key_data['date_created']
        self.expires = public_key_data['date_expires']
        self.public_key = public_key_data['public_key']

        try:
            self.key_type = KeyType.BOTH if not \
                public_key_data.get('key_type') else \
                KeyType(public_key_data['key_type'])

        except ValueError:
            self.key_type = KeyType.OTHER
