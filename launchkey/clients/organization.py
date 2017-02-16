from .base import BaseClient


class OrganizationClient(BaseClient):

    def __init__(self, subject_id, transport):
        super(OrganizationClient, self).__init__('org', subject_id, transport)
