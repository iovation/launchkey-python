class BaseManager(object):

    def __init__(self, organization_factory):
        self._organization_factory = organization_factory
        self._organization_client = self._organization_factory. \
            make_organization_client()

    def _get_directory_client(self, directory_id):
        return self._organization_factory.make_directory_client(directory_id)

    def _get_service_client(self, service_id):
        return self._organization_factory.make_service_client(service_id)

    def cleanup(self):
        pass
