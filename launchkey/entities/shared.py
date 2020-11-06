"""Entities shared across domains"""

# pylint: disable=invalid-name,too-few-public-methods


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
        self.key_type = 0 if not public_key_data.get('key_type') \
            else public_key_data['key_type']
