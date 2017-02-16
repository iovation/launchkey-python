import unittest
from mock import MagicMock, ANY
from launchkey.factories.base import BaseFactory
from launchkey.factories import DirectoryFactory, OrganizationFactory, ServiceFactory
from launchkey.clients import DirectoryClient, OrganizationClient, ServiceClient
from launchkey.transports import JOSETransport
from uuid import uuid4


class TestBaseFactory(unittest.TestCase):

    def setUp(self):
        self._factory = BaseFactory(ANY, ANY, ANY, ANY, ANY, MagicMock(spec=JOSETransport))

    def test_add_additional_private_key(self):
        self._factory.add_additional_private_key(ANY)


class TestDirectoryFactory(unittest.TestCase):

    def setUp(self):
        self._factory = DirectoryFactory(uuid4(), ANY, transport=MagicMock())

    def test_make_directory_client(self):
        self.assertIsInstance(self._factory.make_directory_client(), DirectoryClient)

    def test_make_service_client(self):
        self.assertIsInstance(self._factory.make_service_client(uuid4()), ServiceClient)


class TestServiceFactory(unittest.TestCase):

    def setUp(self):
        self._factory = ServiceFactory(uuid4(), ANY, transport=MagicMock())

    def test_make_service_client(self):
        self.assertIsInstance(self._factory.make_service_client(), ServiceClient)


class TestOrganizationFactory(unittest.TestCase):

    def setUp(self):
        self._factory = OrganizationFactory(uuid4(), ANY, transport=MagicMock())

    def test_make_directory_client(self):
        self.assertIsInstance(self._factory.make_directory_client(uuid4()), DirectoryClient)

    def test_make_organization_client(self):
        self.assertIsInstance(self._factory.make_organization_client(), OrganizationClient)

    def test_make_service_client(self):
        self.assertIsInstance(self._factory.make_service_client(uuid4()), ServiceClient)
