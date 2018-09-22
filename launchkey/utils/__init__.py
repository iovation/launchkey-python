""" Utilities """

from uuid import UUID
from ..exceptions import InvalidIssuerFormat, InvalidIssuerVersion


class UUIDHelper(object):
    """
    Validate the provided uuid string and return a UUID if string is a valid
    UUID with the correct version or throw InvalidIssuerFormat or
    InvalidIssuerVersion when that criteria is not met.
    """

    def from_string(self, uuid_value, version=None):
        """
        Create a UUID from its string representation
        :param uuid_value: The string representation of a UUID
        :param version: The version of the UUID
        :return: UUID
        :raises launchkey.exceptions.InvalidIssuerFormat: when uuid_value
        is not a valid UUID format
        :raises launchkey.exceptions.InvalidIssuerVersion: when uuid_value
        is not the same version as version.
        """
        if not isinstance(uuid_value, UUID):
            try:
                uuid_value = UUID(uuid_value)
            except (ValueError, TypeError, AttributeError):
                raise InvalidIssuerFormat()

        self.validate_version(uuid_value, version)
        return uuid_value

    @staticmethod
    def validate_version(uuid_value, version):
        """

        :param uuid_value: The string representation of a UUID
        :param version: The version of the UUID
        :return: None
        :raises launchkey.exceptions.InvalidIssuerVersion: when uuid_value
        is not the same version as version.
        """
        if not isinstance(uuid_value, UUID):
            raise InvalidIssuerFormat()

        if version is not None and int(version) != uuid_value.version:
            raise InvalidIssuerVersion()


def iso_format(datetime):
    """
    Generates an ISO formatted datetime based on what the LaunchKey API
    expects. This is a standard ISO datetime without microseconds.
    :param datetime: datetime.datetime object
    :return: ISO formatted string IE: 2017-10-03T22:50:15Z
    """
    return datetime.strftime("%Y-%m-%dT%H:%M:%SZ") \
        if datetime is not None else None
