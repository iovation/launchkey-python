"""Directory Factory"""

# pylint: disable=too-many-arguments

from .. import LAUNCHKEY_PRODUCTION
from ..clients import DirectoryClient, ServiceClient
from .base import BaseFactory


class DirectoryFactory(BaseFactory):
    """Factory for creating clients when representing a LaunchKey Directory"""

    def __init__(self, directory_id, private_key, url=LAUNCHKEY_PRODUCTION,
                 testing=False, transport=None):
        """
        :param directory_id: UUID for the requesting directory
        :param private_key: PEM formatted private key string
        :param url: URL for the LaunchKey API
        :param testing: Boolean stating whether testing mode is being used.
        This will determine whether SSL validation occurs.
        :param: transport: Instantiated transport object. The default and
        currently only supported transport is
        launchkey.transports.JOSETransport. If you wish to set encryption or
        hashing algorithms, this is where you would do it. IE:
        JOSETransport(jwt_algorithm="RS512", jwe_cek_encryption="RSA-OAEP",
        jwe_claims_encryption="A256CBC-HS512", content_hash_algorithm="S256")
        """
        super(DirectoryFactory, self).__init__('dir', directory_id,
                                               private_key, url, testing,
                                               transport)

    def make_directory_client(self):
        """
        Retrieves a client to make directory calls.
        :return: launchkey.clients.DirectoryClient
        """
        return DirectoryClient(self._issuer_id, self._transport)

    def make_service_client(self, service_id):
        """
        Retrieves a client to make service calls.
        :param service_id: Service id
        :return: launchkey.clients.ServiceClient
        """
        return ServiceClient(service_id, self._transport)
