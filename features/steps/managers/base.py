from logging import getLogger


class Loggable(object):

    def __init__(self):
        self._logger = getLogger(
            "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        )

    def log_info(self, message, *args, **kwargs):
        self._logger.info(message, *args, **kwargs)

    def log_debug(self, message, *args, **kwargs):
        self._logger.debug(message, *args, **kwargs)

    def log_error(self, message, *args, **kwargs):
        self._logger.error(message, *args, **kwargs)


class BaseManager(Loggable):

    def __init__(self, organization_factory):
        self._organization_factory = organization_factory
        self._organization_client = self._organization_factory. \
            make_organization_client()
        Loggable.__init__(self)

    def _get_directory_client(self, directory_id):
        return self._organization_factory.make_directory_client(directory_id)

    def _get_service_client(self, service_id):
        return self._organization_factory.make_service_client(service_id)

    def cleanup(self):
        pass
