import unittest
from mock import MagicMock
from uuid import uuid4
from launchkey.clients import OrganizationClient
from launchkey.transports.base import APIResponse


class TestOrganizationClient(unittest.TestCase):

    def setUp(self):
        self._transport = MagicMock()
        self._response = APIResponse({}, {}, 200)
        self._transport.post.return_value = self._response
        self._organization_service = OrganizationClient(uuid4(), self._transport)

    def test_instantiation(self):
        pass
