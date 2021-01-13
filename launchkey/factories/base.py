"""Base classes for factories"""

# pylint: disable=too-many-arguments,too-few-public-methods

import warnings
from ..transports import JOSETransport
from ..utils.shared import UUIDHelper


class BaseFactory(object):
    """
    LaunchKey Base client

    The primary purpose of the client is to validate entity input and
    translate needed values that will be utilized in
    the JOSE flow.
    """

    def __init__(self, issuer, issuer_id, private_key, url, testing,
                 transport):
        """
        :param issuer: Issuer type that will be translated directly to the
        JOSE transport layer as an issuer. IE: svc, dir, org
        :param issuer_id: UUID of the issuer
        :param private_key: PEM formatted private key string. This key will be
                            used for signing requests. It will also be used for
                            decrypting requests when a dual purpose key is
                            given. If a separate encryption key is desired it
                            can be added via the add_encryption_private_key
                            method.
        :param url: URL for the LaunchKey API
        :param testing: Boolean stating whether testing mode is being used.
        This will determine whether SSL validation
        occurs.
        """
        self._issuer_id = UUIDHelper().from_string(issuer_id)
        self._transport = transport if transport is not None \
            else JOSETransport()
        self._transport.set_url(url, testing)
        # Set the issue which will set the given key as the signature key
        self._transport.set_issuer(issuer, issuer_id, private_key)
        # Add the given key as an encryption key as well
        self._transport.add_encryption_private_key(private_key)

    def add_additional_private_key(self, private_key):
        """
        Adds an additional private key. This is to allow for key rotation.
        The default key to be used is the one set in
        the instantiation of the factory.

        This method is being deprecated in favor of add_encryption_private_key.

        :param private_key:
        :return:
        """
        warnings.warn(
            "This method will be removed in the future. Please use "
            "add_encryption_key instead.",
            DeprecationWarning)
        self.add_encryption_private_key(private_key)

    def add_encryption_private_key(self, private_key):
        """
        Adds an additional encryption private key. This is to allow for
        separating signature and encryption keys. Multiple encryption keys are
        supported to allow for key rotation.

        When defining a signature key it should be done in the instantiation of
        the factory.

        :param private_key:
        :return:
        """
        self._transport.add_encryption_private_key(private_key)
