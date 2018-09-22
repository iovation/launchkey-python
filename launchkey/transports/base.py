""" Module for shared code amongst transports """

# pylint: disable=too-few-public-methods, too-many-arguments


class APIResponse(object):
    """ Response from API """
    data = None
    headers = None
    status_code = None
    reason = None

    def __init__(self, data, headers, status_code, reason=None, raw_data=None):
        self.data = data
        self.headers = headers
        self.status_code = status_code
        self.reason = reason
        self.raw_data = raw_data

    def __str__(self):
        return super(APIResponse, self).__str__() + ": %s %s %s" % (
            self.status_code, self.reason, self.data)


class APIErrorResponse(APIResponse):
    """Response that should be raised when an OK status is not found"""
