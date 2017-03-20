from launchkey.transports import JOSETransport


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
        self._issuer_id = issuer_id
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
