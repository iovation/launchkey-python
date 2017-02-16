from .base import BaseFactory
from launchkey import LAUNCHKEY_PRODUCTION
from launchkey.clients import ServiceClient


class ServiceFactory(BaseFactory):
    """Factory for creating clients when representing a LaunchKey Service Profile"""

    def __init__(self, service_id, private_key, url=LAUNCHKEY_PRODUCTION, testing=False, transport=None):
        """
        :param service_id: UUID for the requesting service
        :param private_key: PEM formatted private key string
        :param url: URL for the LaunchKey API
        :param testing: Boolean stating whether testing mode is being used. This will determine whether SSL validation
        occurs.
        :param: transport: Instantiated transport object. The default and currently only supported transport is
        launchkey.transports.JOSETransport. If you wish to set encryption or hashing algorithms, this is where you would
        do it. IE: JOSETransport(jwt_algorithm="RS512", jwe_cek_encryption="RSA-OAEP",
                                jwe_claims_encryption="A256CBC-HS512", content_hash_algorithm="S256")
        """
        super(ServiceFactory, self).__init__('svc', service_id, private_key, url, testing, transport)

    def make_service_client(self):
        """
        Retrieves a client to make service calls.
        :return: launchkey.clients.ServiceClient
        """
        return ServiceClient(self._issuer_id, self._transport)
