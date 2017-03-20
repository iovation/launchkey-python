class APIResponse(object):
    data = None
    headers = None
    status_code = None

    def __init__(self, data, headers, status_code):
        self.data = data
        self.headers = headers
        self.status_code = status_code

    def __str__(self):
        return super(APIResponse, self).__str__() + ": %s %s" % (self.status_code, self.data)


class APIErrorResponse(APIResponse):
    """Response that should be raised when an OK status is not found"""
