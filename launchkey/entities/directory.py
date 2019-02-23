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

    def __eq__(self, other):
        if isinstance(other, Directory):
            success = self.service_ids == other.service_ids and \
                      self.sdk_keys == other.sdk_keys and \
                      self.premium == other.premium and \
                      self.name == other.name and \
                      self.android_key == other.android_key and \
                      self.ios_certificate_fingerprint == \
                      other.ios_certificate_fingerprint and \
                      self.active == other.active and \
                      self.id == other.id and \
                      self.denial_context_inquiry_enabled == \
                      other.denial_context_inquiry_enabled
        else:
            success = False
        return success

    def __repr__(self):
        return "Directory <id={id}, name={name}, service_ids={service_ids}, sdk_keys={sdk_keys}, premium={premium}, ios_certificate_fingerprint={ios_certificate_fingerprint}, active={active}, denial_context_inquiry_enabled={denial_context_inquiry_enabled}>". \
            format(
                id=self.id,
                name=self.name,
                service_ids=self.service_ids,
                sdk_keys=self.sdk_keys,
                premium=self.premium,
                ios_certificate_fingerprint=self.ios_certificate_fingerprint,
                active=self.active,
                denial_context_inquiry_enabled=self.denial_context_inquiry_enabled
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


class Device(object):
    """Device object belonging to a directory user"""

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.status = DeviceStatus(data['status'])
        self.type = data['type']
