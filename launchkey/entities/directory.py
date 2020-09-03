"""Directory level entities"""

# pylint: disable=invalid-name,too-few-public-methods,
# pylint: disable=too-many-instance-attributes


from launchkey.exceptions import InvalidDeviceStatus


class Directory(object):
    """Directory entity"""
    def __init__(self, data):
        self.service_ids = data['service_ids']
        self.sdk_keys = data['sdk_keys']
        self.premium = data['premium']
        self.name = data['name']
        self.android_key = data['android_key']
        self.ios_certificate_fingerprint = data['ios_certificate_fingerprint']
        self.active = data['active']
        self.id = data['id']
        self.denial_context_inquiry_enabled = \
            data['denial_context_inquiry_enabled']
        self.webhook_url = data['webhook_url']

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, Directory):
            eq = self.service_ids == other.service_ids and \
                      self.sdk_keys == other.sdk_keys and \
                      self.premium == other.premium and \
                      self.name == other.name and \
                      self.android_key == other.android_key and \
                      self.ios_certificate_fingerprint == \
                      other.ios_certificate_fingerprint and \
                      self.active == other.active and \
                      self.id == other.id and \
                      self.denial_context_inquiry_enabled == \
                      other.denial_context_inquiry_enabled and \
                      self.webhook_url == other.webhook_url
        else:
            eq = False
        return eq

    def __repr__(self):
        return "Directory <id=\"{id}\", name=\"{name}\", " \
               "service_ids={service_ids}, sdk_keys={sdk_keys}, " \
               "premium={premium}, " \
               "ios_certificate_fingerprint=" \
               "\"{ios_certificate_fingerprint}\", " \
               "active={active}, " \
               "denial_context_inquiry_enabled=" \
               "{denial_context_inquiry}, webhook_url=\"{webhook_url}\">". \
            format(
                id=self.id,
                name=self.name,
                service_ids=self.service_ids,
                sdk_keys=self.sdk_keys,
                premium=self.premium,
                ios_certificate_fingerprint=self.ios_certificate_fingerprint,
                active=self.active,
                denial_context_inquiry=self.denial_context_inquiry_enabled,
                webhook_url=self.webhook_url
            )


class Session(object):
    """User Service Session"""

    def __init__(self, session):
        self.auth_request = session['auth_request']
        self.created = session['date_created']
        self.service_icon = session['service_icon']
        self.service_id = session['service_id']
        self.service_name = session['service_name']


class DirectoryUserDeviceLinkData(object):
    """Directory user device data used to finish the linking process"""

    def __init__(self, data):
        self.qrcode = data['qrcode']
        self.code = data['code']
        self.device_id = data['device_id']


class DirectoryUserTOTP(object):
    """Directory user TOTP data that is returned after an add request"""

    def __init__(self, data):
        self.secret = data['secret']
        self.algorithm = data['algorithm']
        self.period = data['period']
        self.digits = data['digits']

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, DirectoryUserTOTP):
            eq = self.secret == other.secret and \
                 self.algorithm == other.algorithm and \
                 self.period == other.period and \
                 self.digits == other.digits
        else:
            eq = False
        return eq

    def __repr__(self):
        return "DirectoryUserTOTP <secret=\"{secret}\", " \
               "algorithm=\"{algorithm}\", period={period}, " \
               "digits={digits}>". \
            format(
                secret=self.secret,
                algorithm=self.algorithm,
                period=self.period,
                digits=self.digits
            )


class DeviceLinkCompletionResponse(object):
    """Package returned on the event that a device finishes linking"""

    def __init__(self, data):
        self.device_id = data['device_id']
        self.device_public_key = data['device_public_key']
        self.device_public_key_id = data['device_public_key_id']


class DeviceStatus(object):
    """Activation status of a directory user's device"""

    _status_map = {
        0: ("LINK_PENDING", False),
        1: ("LINKED", True),
        2: ("UNLINK_PENDING", True)
    }

    def __init__(self, status_code):
        if status_code not in self._status_map:
            raise InvalidDeviceStatus(
                "Status code %s was not recognized" % status_code)
        self._status_code = status_code

    @property
    def is_active(self):
        """
        Is the device active?
        :return: active status
        """
        return self._status_map[self._status_code][1]

    @property
    def status_code(self):
        """
        What's the status iof the device
        :return: Status code
        """
        return self._status_map[self._status_code][0]

    def __repr__(self):
        return \
            "DeviceStatus <status_code=\"{status_code}\", " \
            "is_active={is_active}>".format(
                status_code=self.status_code,
                is_active=self.is_active
            )


class Device(object):
    """Device object belonging to a directory user"""

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.status = DeviceStatus(data['status'])
        self.type = data['type']

    def __repr__(self):
        return "Device <id=\"{id}\", name=\"{name}\", " \
               "status={status}, type=\"{type}\">". \
            format(
                id=self.id,
                name=self.name,
                status=self.status,
                type=self.type
            )
