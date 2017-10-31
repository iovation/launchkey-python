from launchkey.exceptions import InvalidDeviceStatus


class Directory(object):
    def __init__(self, data):
        self.service_ids = data['service_ids']
        self.sdk_keys = data['sdk_keys']
        self.premium = data['premium']
        self.name = data['name']
        self.android_key = data['android_key']
        self.ios_certificate_fingerprint = data['ios_certificate_fingerprint']
        self.active = data['active']
        self.id = data['id']


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
            raise InvalidDeviceStatus("Status code %s was not recognized" % status_code)
        self._status_code = status_code

    @property
    def is_active(self):
        return self._status_map[self._status_code][1]

    @property
    def status_code(self):
        return self._status_map[self._status_code][0]


class Device(object):
    """Device object belonging to a directory user"""

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.status = DeviceStatus(data['status'])
        self.type = data['type']
