import unittest
from mock import MagicMock, ANY
from launchkey.factories.base import BaseFactory
from launchkey.factories import DirectoryFactory, OrganizationFactory, ServiceFactory
from launchkey.clients import DirectoryClient, OrganizationClient, ServiceClient
from launchkey.transports import JOSETransport
from uuid import uuid1


class TestBaseFactory(unittest.TestCase):

    def setUp(self):
        self._factory = BaseFactory(ANY, uuid1(), ANY, ANY, ANY, MagicMock(spec=JOSETransport))

    def test_add_additional_private_key(self):
        self._factory.add_additional_private_key(ANY)


class TestDirectoryFactory(unittest.TestCase):

    def setUp(self):
        self._factory = DirectoryFactory(uuid1(), ANY, transport=MagicMock())

    def test_make_directory_client(self):
        self.assertIsInstance(self._factory.make_directory_client(), DirectoryClient)

    def test_make_service_client(self):
        self.assertIsInstance(self._factory.make_service_client(uuid1()), ServiceClient)


class TestServiceFactory(unittest.TestCase):

    def setUp(self):
        self._factory = ServiceFactory(uuid1(), ANY, transport=MagicMock())

    def test_make_service_client(self):
        self.assertIsInstance(self._factory.make_service_client(), ServiceClient)


class TestOrganizationFactory(unittest.TestCase):

    def setUp(self):
        self._factory = OrganizationFactory(uuid1(), ANY, transport=MagicMock())

    def test_make_directory_client(self):
        self.assertIsInstance(self._factory.make_directory_client(uuid1()), DirectoryClient)

    def test_make_organization_client(self):
        self.assertIsInstance(self._factory.make_organization_client(), OrganizationClient)

    def test_make_service_client(self):
        self.assertIsInstance(self._factory.make_service_client(uuid1()), ServiceClient)
