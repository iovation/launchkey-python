from launchkey.exceptions import InvalidEntityID, LaunchKeyAPIException, InvalidParameters, EntityNotFound, \
    PolicyFailure, InvalidPolicyInput, RequestTimedOut, RateLimited, InvalidDirectoryIdentifier, \
    UnexpectedAPIResponse, Forbidden, Unauthorized
from launchkey.transports.base import APIResponse
from uuid import UUID
from formencode import Invalid

error_code_map = {
    "ARG-001": InvalidParameters,
    "SVC-002": InvalidPolicyInput,
    "SVC-003": PolicyFailure,
    "DIR-001": InvalidDirectoryIdentifier
}

status_code_map = {
    401: Unauthorized,
    403: Forbidden,
    404: EntityNotFound,
    408: RequestTimedOut,
    429: RateLimited
}


def api_call(function):
    """
    Decorator for handling LaunchKey API Exceptions
    :param function:
    :return:
    """
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except LaunchKeyAPIException as e:
            if not isinstance(e.message, dict) or 'error_code' not in e.message or 'error_detail' not in e.message:
                error_code = ""
                error_detail = ""
            else:
                error_code = e.message.get('error_code')
                error_detail = e.message.get('error_detail')
            status_code = e.status_code
            if error_code in error_code_map:
                raise error_code_map[error_code](error_detail, status_code)
            elif status_code in status_code_map:
                raise status_code_map[status_code](error_detail, status_code)
            else:
                raise
    return wrapper


class BaseClient(object):
    """
    Base Client for performing API queries against the LaunchKey API. Clients are the interfaces that will be used
    by implementers to query against specific entity based endpoints (service, directory, organization, etc).
    """

    def __init__(self, subject_type, subject_id, transport):
        """
        :param subject_type: Entity type that the service will represent
        :param subject_id: Entity id of which the service will represent
        :param transport: Transport class that will perform API queries
        """
        try:
            UUID(str(subject_id))
        except ValueError:
            raise InvalidEntityID("The given id was invalid. Please ensure it is a UUID.")
        self._subject = "%s:%s" % (subject_type, subject_id)
        self._transport = transport

    @staticmethod
    def _validate_response(api_response, validator):
        if isinstance(api_response, APIResponse):
            try:
                return validator.to_python(api_response.data)
            except Invalid:
                raise UnexpectedAPIResponse(api_response.data, api_response.status_code)
        else:
            try:
                return validator.to_python(api_response)
            except Invalid:
                raise UnexpectedAPIResponse(api_response)
