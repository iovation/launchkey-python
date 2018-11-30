"""Shared Validators"""


from formencode import FancyValidator, Invalid
from dateutil.parser import parse


class ValidateISODate(FancyValidator):
    """Validator for LaunchKey ISO dates"""

    @staticmethod
    def _to_python(value, state):
        try:
            val = parse(value)
        except ValueError:
            raise Invalid("Date/time format is invalid, it must be ISO 8601 "
                          "formatted  for UTZ with no offset (i.e. "
                          "2010-01-01T01:01:01Z)", value, state)
        return val
