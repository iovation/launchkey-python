class APIResponse(object):
    data = None
    headers = None
    status_code = None
    reason = None

    def __init__(self, data, headers, status_code, reason=None):
        self.data = data
        self.headers = headers
        self.status_code = status_code
        self.reason = reason

    def __str__(self):
        return super(APIResponse, self).__str__() + ": %s %s %s" % (self.status_code, self.reason, self.data)


class APIErrorResponse(APIResponse):
    """Response that should be raised when an OK status is not found"""
