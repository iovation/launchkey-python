from launchkey.exceptions import InvalidIssuerFormat, InvalidIssuerVersion
from uuid import UUID


class UUIDHelper(object):
    """
    Validate the provided uuid string and return a UUID if string is a valid UUID with the correct
    version or throw InvalidIssuerFormat or InvalidIssuerVersion when that criteria is not met.
    """

    def from_string(self, uuid_value, version=None):
        if type(uuid_value) is not UUID:
            try:
                uuid_value = UUID(uuid_value)
            except (ValueError, TypeError, AttributeError):
                raise InvalidIssuerFormat()

        self.validate_version(uuid_value, version)
        return uuid_value

    @staticmethod
    def validate_version(uuid_value, version):
        if type(uuid_value) is not UUID:
            raise InvalidIssuerFormat()

        if version is not None and int(version) != uuid_value.version:
            raise InvalidIssuerVersion()


def iso_format(datetime):
    """
    Generates an ISO formatted datetime based on what the LaunchKey API expects.
    This is a standard ISO datetime without microseconds.
    :param datetime: datetime.datetime object
    :return: ISO formatted string IE: 2017-10-03T22:50:15Z
    """
    return datetime.strftime("%Y-%m-%dT%H:%M:%SZ") if datetime is not None else None
