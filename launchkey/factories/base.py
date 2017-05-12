from launchkey.transports import JOSETransport
from launchkey.exceptions import InvalidIssuerFormat, InvalidIssuerVersion
from uuid import UUID


class BaseFactory(object):
    """
    LaunchKey Base client

    The primary purpose of the client is to validate entity input and translate needed values that will be utilized in
    the JOSE flow.
    """

    def __init__(self, issuer, issuer_id, private_key, url, testing, transport):
        """
        :param issuer: Issuer type that will be translated directly to the JOSE transport layer as an issuer.
                       IE: svc, dir, org
        :param issuer_id: UUID of the issuer
        :param private_key: PEM formatted private key string
        :param url: URL for the LaunchKey API
        :param testing: Boolean stating whether testing mode is being used. This will determine whether SSL validation
        occurs.
        """
        self._issuer_id = UUIDHelper().from_string(issuer_id, 1)
        self._transport = transport if transport is not None else JOSETransport()
        self._transport.set_url(url, testing)
        self._transport.set_issuer(issuer, issuer_id, private_key)

    def add_additional_private_key(self, private_key):
        """
        Adds an additional private key. This is to allow for key rotation. The default key to be used is the one set in
        the instantiation of the factory.
        :param private_key:
        :return:
        """
        self._transport.add_issuer_key(private_key)
    
        
class UUIDHelper(object):
    """
    Validate the provided uuid string and return a UUID if string is a valid UUID with the correct
    version or throw InvalidIssuerFormat or InvalidIssuerVersion when that criteria is not met.
    """

    def from_string(self, uuid_value, version):
        if type(uuid_value) is not UUID:
            try:
                uuid_value = UUID(uuid_value)
            except (ValueError, TypeError, AttributeError):
                raise InvalidIssuerFormat()
        
        self.validate_version(uuid_value, version)
        return uuid_value
        
    def validate_version(self, uuid_value, version):
        if type(uuid_value) is not UUID:
            raise InvalidIssuerFormat()
            
        if int(version) != uuid_value.version:
            raise InvalidIssuerVersion()
            
        
