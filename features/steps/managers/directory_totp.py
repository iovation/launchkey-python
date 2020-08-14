import hashlib
from logging import getLogger
from pyotp import TOTP
from .base import BaseManager
from launchkey.entities.directory import DirectoryUserTOTP


class TOTPNotGenerated(Exception):
    """TOTP has not been generated yet"""


class DirectoryTOTPManager(BaseManager):
    def __init__(self, organization_factory):
        self.current_totp_response = None
        self.current_totp_configuration = None
        self._current_user_identifier = None
        self.current_user_identifier = None
        self._current_user_identifier = None
        self.directory_user_identifiers = dict()
        self._logger = getLogger(
            "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        )
        super(DirectoryTOTPManager, self, ).__init__(
            organization_factory)

    def cleanup(self):
        for directory_id, user_identifier_set in \
                self.directory_user_identifiers.items():
            self._logger.debug("Cleaning up directory: %s TOTP" %
                               directory_id)
            for user_identifier in user_identifier_set:
                self.remove_user_totp(user_identifier, directory_id)

    @property
    def current_totp_configuration(self):
        if self._current_totp_configuration is None:
            raise TOTPNotGenerated
        return self._current_totp_configuration

    @current_totp_configuration.setter
    def current_totp_configuration(self, value):
        self.previous_totp_configuration = getattr(
            self, "_current_totp_configuration", None)
        self._current_totp_configuration = value

    @property
    def current_totp_response(self):
        if self._current_totp_response is None:
            raise TOTPNotGenerated
        return self._current_totp_response

    @current_totp_response.setter
    def current_totp_response(self, value):
        self.previous_totp_response = getattr(
            self, "_current_totp_response", None)
        self._current_totp_response = value

        if isinstance(value, DirectoryUserTOTP):
            otp_data = {
                "digits": value.digits,
                "interval": value.period
            }
            algorithm = value.algorithm
            if algorithm == 'SHA1':
                otp_data['digest'] = hashlib.sha1
            elif algorithm == 'SHA256':
                otp_data['digest'] = hashlib.sha256
            elif algorithm == 'SHA512':
                otp_data['digest'] = hashlib.sha512

            self.current_totp_configuration = TOTP(
                value.secret,
                **otp_data
            )

    @property
    def current_user_identifier(self):
        return self._current_user_identifier

    @current_user_identifier.setter
    def current_user_identifier(self, value):
        self.previous_user_identifier = getattr(
            self, "_current_user_identifier", None)
        self._current_user_identifier = value

    def generate_user_totp(self, user_identifier, directory_id):
        self.current_user_identifier = user_identifier
        directory_client = self._get_directory_client(directory_id)
        self.current_totp_response = directory_client.generate_user_totp(
            user_identifier
        )

        if self.directory_user_identifiers.get(directory_id):
            self.directory_user_identifiers[directory_id].add(user_identifier)
        else:
            self.directory_user_identifiers[directory_id] = {user_identifier}

        return self.current_totp_response

    def remove_user_totp(self, user_identifier, directory_id):
        directory_client = self._get_directory_client(directory_id)
        directory_client.remove_user_totp(
            user_identifier
        )

    def verify_totp(self, user_identifier, otp, service_id):
        service_client = self._get_service_client(service_id)
        service_client.verify_totp(
            user_identifier,
            otp
        )