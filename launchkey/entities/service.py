from formencode import Invalid
from launchkey.exceptions import UnexpectedKeyID, UnexpectedDeviceResponse, InvalidGeoFenceName, \
    InvalidTimeFenceEndTime, InvalidTimeFenceName, InvalidTimeFenceStartTime, MismatchedTimeFenceTimezones, \
    DuplicateTimeFenceName, DuplicateGeoFenceName
from base64 import b64decode
from json import loads, dumps
from launchkey.exceptions import InvalidPolicyFormat, InvalidParameters
from .validation import AuthorizationResponsePackageValidator
import datetime
import pytz


class GeoFence(object):

    def __init__(self, latitude, longitude, radius, name):
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
        self.name = name


class TimeFence(object):

    def __init__(self, name, start_time, end_time, monday=False, tuesday=False, wednesday=False, thursday=False,
                 friday=False, saturday=False, sunday=False):
        if not isinstance(start_time, datetime.time):
            raise InvalidTimeFenceStartTime
        elif not isinstance(end_time, datetime.time):
            raise InvalidTimeFenceEndTime
        elif start_time.tzname() != end_time.tzname():
            raise MismatchedTimeFenceTimezones

        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday
        self.days = []
        if self.monday:
            self.days.append("Monday")
        if self.tuesday:
            self.days.append("Tuesday")
        if self.wednesday:
            self.days.append("Wednesday")
        if self.thursday:
            self.days.append("Thursday")
        if self.friday:
            self.days.append("Friday")
        if self.saturday:
            self.days.append("Saturday")
        if self.sunday:
            self.days.append("Sunday")
        self.timezone = start_time.tzname() if start_time.tzname() else "UTC"


class AuthPolicy(object):
    """AuthPolicy object for performing dynamic authorizations"""

    def __init__(self, any=0, knowledge=False, inherence=False, possession=False, jailbreak_protection=False):
        """
        Note that if any is used neither knowledge, inherence, nor possession can be used alongside it.

        If all values are left at 0, service defaults will be used.

        :param any: Int. Whether to require any x number of factors
        :param knowledge: Boolean. Whether to require knowledge factors
        :param inherence: Boolean. Whether to require inherence factors
        :param possession: Boolean. Whether to require possesion factors
        :param jailbreak_protection: Boolean. Whether to allow jailbroken / rooted devices to authenticate
        """

        if knowledge not in (True, False, 0, 1) or inherence not in (True, False, 0, 1) \
                or possession not in (True, False, 0, 1):
            raise InvalidParameters("Inherence, knowledge, or possesion input must be a boolean.")
        if any != 0 and (knowledge or inherence or possession):
            raise InvalidParameters("Cannot use \"any\" with other specific factor requirements")

        self.geofences = []
        self.minimum_requirements = []
        self.minimum_amount = 0

        self._policy = {"factors": []}
        self.set_minimum_requirements(knowledge, inherence, possession, any)
        self.require_jailbreak_protection(jailbreak_protection)

    def __eq__(self, other):
        return self._policy == other._policy if hasattr(other, '_policy') else False

    def add_geofence(self, latitude, longitude, radius, name=None):
        """
        Adds a Geo-Fence requirement
        :param latitude: Float. Geographical Latitude
        :param longitude: Float. Geographical Longitude
        :param radius: Float. Radius of the Geo-Fence in meters
        :param name: String. Optional identifier for the Geo-Fence.
        """
        self.geofences.append(GeoFence(latitude, longitude, radius, name))
        try:
            location = {"radius": float(radius), "latitude": float(latitude), "longitude": float(longitude)}
            if name is not None:
                location['name'] = str(name)
        except TypeError:
            raise InvalidParameters("Latitude, Longitude, and Radius must all be numbers.")
        for i, factor in enumerate(self._policy['factors']):
            if factor.get('factor') == "geofence":
                self._policy['factors'][i]['attributes']['locations'].append(location)
                return
        self._policy['factors'].append(
            {
                "factor": "geofence",
                "requirement": "forced requirement",
                "quickfail": False,
                "priority": 1,
                "attributes": {"locations": [location]}
            }
        )

    def remove_geofence(self, name):
        """
        Removes a Geo-Fence based on an input name
        :param name: String name of the Geo-Fence
        :return:
        """
        for key, factor in enumerate(self._policy['factors']):
            if 'factor' in factor and factor['factor'] == 'geofence':
                for loc_key, location in enumerate(factor['attributes']['locations']):
                    if 'name' in location and location['name'].lower() == name.lower():
                        del self._policy['factors'][key]['attributes']['locations'][loc_key]
                        for geo_key, geo in enumerate(self.geofences):
                            if geo.name.lower() == name.lower():
                                del self.geofences[geo_key]
                                return
        raise InvalidGeoFenceName

    def require_jailbreak_protection(self, status):
        """
        Enables or disables jailbreak and root protection (device integrity) for Auths
        :param status: Bool as to whether device integrity should be required
        :return:
        """
        enabled = 1 if status else 0
        self.jailbreak_protection = True if enabled else False

        for key, factor in enumerate(self._policy['factors']):
            if 'factor' in factor and factor['factor'] == 'device integrity':
                self._policy['factors'][key]['attributes'] = {"factor enabled": 1 if status else 0}
                return

        self._policy['factors'].append({
            "factor": "device integrity",
            "requirement": "forced requirement",
            "quickfail": False,
            "priority": 1,
            "attributes": {"factor enabled": enabled}
        })

    def set_minimum_requirements(self, knowledge=False, inherence=False, possession=False, minimum_amount=0):
        """
        Sets minimum requirements that must be used for each Auth Request
        :param knowledge: Bool. Whether a Knowledge factor should be required.
        :param inherence: Bool. Whether an Inherence factor should be required.
        :param possession: Bool. Whether a Possession factor should be required.
        :param minimum_amount: Integer. Whether to require a minimum amount any nonspecific requirements.
        :return:
        """

        minimum_requirements = []
        if knowledge:
            minimum_requirements.append("knowledge")
        if inherence:
            minimum_requirements.append("inherence")
        if possession:
            minimum_requirements.append("possession")

        self.minimum_requirements = minimum_requirements
        self.minimum_amount = minimum_amount
        if not minimum_requirements and not minimum_amount:
            self._policy['minimum_requirements'] = []
        else:
            self._policy['minimum_requirements'] = [{
                "requirement": "authenticated",
                "any": self.minimum_amount,
                "knowledge": 1 if 'knowledge' in minimum_requirements else 0,
                "inherence": 1 if 'inherence' in minimum_requirements else 0,
                "possession": 1 if 'possession' in minimum_requirements else 0,
            }]

    def get_policy(self):
        """
        Retrieves json representation of the policy
        :return: Valid policy dict
        """
        try:
            dumps(self._policy)
        except TypeError:
            raise InvalidParameters("Policy input was not JSON serializable. Please verify it is correct.")
        return self._policy

    def set_policy(self, policy):
        """
        Updates a policy based on a given policy
        :param policy: Dict os JSON representation of a LaunchKey policy
        :return:
        """
        if type(policy) is not dict:
            try:
                self._policy = loads(policy)
            except (ValueError, TypeError):
                raise InvalidPolicyFormat()
        else:
            self._policy = policy

        if 'minimum_requirements' not in self._policy or 'factors' not in self._policy:
            raise InvalidPolicyFormat()

        self._parse_minimum_requirements(self._policy['minimum_requirements'])
        self._parse_factors(self._policy['factors'])

    def _parse_minimum_requirements(self, minimum_requirements):
        # Although the API returns a list, we only support one returned value as of now
        if minimum_requirements:
            requirement = minimum_requirements[0]
            if 'knowledge' in requirement and requirement['knowledge']:
                self.minimum_requirements.append('knowledge')
            if 'inherence' in requirement and requirement['inherence']:
                self.minimum_requirements.append('inherence')
            if 'possession' in requirement and requirement['possession']:
                self.minimum_requirements.append('possession')
            if 'all' in requirement and requirement['all']:
                self.minimum_amount = requirement['all']
            if 'any' in requirement and requirement['any']:
                self.minimum_amount = requirement['any']

    def _parse_factors(self, factors):
        for factor in factors:
            if 'factor' in factor and 'attributes' in factor and factor['attributes']:
                if factor['factor'] == 'geofence' and 'locations' in factor['attributes']:
                    for fence in factor['attributes']['locations']:
                        self.geofences.append(GeoFence(fence['latitude'], fence['longitude'], fence['radius'],
                                                       fence['name']))
                elif factor['factor'] == 'device integrity' and 'factor enabled' in factor['attributes']:
                    if factor['attributes']['factor enabled']:
                        self.jailbreak_protection = True


class AuthorizationResponse(object):
    """Authorization Response object containing decrypted auth response and other related information"""

    @staticmethod
    def _decrypt_auth_package(package, issuer_private_key):
        try:
            return AuthorizationResponsePackageValidator.to_python(
                loads(issuer_private_key.decrypt(b64decode(package)))
            )
        except (Invalid, ValueError, TypeError):
            raise UnexpectedDeviceResponse("The device response was invalid. Please verify the same key that initiated"
                                           " the auth request is being used to decrypt the current message.")

    def __init__(self, data, issuer_private_keys):
        if data.get('public_key_id') not in issuer_private_keys:
            raise UnexpectedKeyID("The auth response was for a key id %s which is not recognized" %
                                  data.get('public_key_id'))
        decrypted_package = self._decrypt_auth_package(data['auth'], issuer_private_keys[data.get('public_key_id')])
        self.authorization_request_id = decrypted_package.get('auth_request')
        self.authorized = decrypted_package.get('response')
        self.device_id = decrypted_package.get('device_id')
        self.service_pins = decrypted_package.get('service_pins')
        self.service_user_hash = data.get('service_user_hash')
        self.organization_user_hash = data.get('org_user_hash')
        self.user_push_id = data.get('user_push_id')


class SessionEndRequest(object):
    """Session end request containing the logout_requested unix timestamp and the service_user_hash"""

    def __init__(self, service_user_hash, api_time):
        self.logout_requested = api_time
        self.service_user_hash = service_user_hash


class ServiceSecurityPolicy(AuthPolicy):
    """Security Policy object containing specifics on policy that will be used in Auth Requests"""

    def __init__(self, any=0, knowledge=False, inherence=False, possession=False, jailbreak_protection=False):
        self.timefences = []
        super(ServiceSecurityPolicy, self).__init__(any, knowledge, inherence, possession, jailbreak_protection)

    def add_geofence(self, latitude, longitude, radius, name):
        """
        Adds a Geo-Fence requirement
        :param latitude: Float. Geographical Latitude
        :param longitude: Float. Geographical Longitude
        :param radius: Float. Radius of the Geo-Fence in meters
        :param name: String. Name identifier for the Geo-Fence. This should be unique.
        """
        for fence in self.geofences:
            if fence.name.lower() == name.lower():
                # If the name exists, we should raise an error since they should to be unique
                raise DuplicateGeoFenceName
        return super(ServiceSecurityPolicy, self).add_geofence(latitude, longitude, radius, name)

    def add_timefence(self, name, start_time, end_time, monday=False, tuesday=False, wednesday=False, thursday=False,
                      friday=False, saturday=False, sunday=False):
        """
        Adds a Time-Fence requirement
        :param name: String. Name identifier for the Time-Fence. This should be unique.
        :param start_time: datetime.time object. A tzinfo value must be used if you do not want UTC.
                            It must match the end_time tzinfo.
        :param end_time:  datetime.time object. A tzinfo value must be used if you do not want UTC.
                            It must match the start_time tzinfo.
        :param monday: Bool. Whether the Time-Fence should be valid on Mondays
        :param tuesday: Bool. Whether the Time-Fence should be valid on Tuesdays
        :param wednesday: Bool. Whether the Time-Fence should be valid on Wednesdays
        :param thursday: Bool. Whether the Time-Fence should be valid on Thursdays
        :param friday: Bool. Whether the Time-Fence should be valid on Fridays
        :param saturday: Bool. Whether the Time-Fence should be valid on Saturdays
        :param sunday: Bool. Whether the Time-Fence should be valid on Sundays
        :return:
        """
        fence = TimeFence(name, start_time, end_time, monday=monday, tuesday=tuesday, wednesday=wednesday,
                          thursday=thursday, friday=friday, saturday=saturday, sunday=sunday)
        self.timefences.append(fence)
        new_time = {
            "days": fence.days,
            "start hour": fence.start_time.hour,
            "end hour": fence.end_time.hour,
            "name": fence.name,
            "start minute": fence.start_time.minute,
            "end minute": fence.end_time.minute,
            "timezone": fence.timezone
        }

        for key, factor in enumerate(self._policy['factors']):
            if 'factor' in factor and factor['factor'] == 'timefence':
                for fence_key, fence in enumerate(factor['attributes']['time fences']):
                    if fence['name'].lower() == name.lower():
                        # If the name exists, we should raise an error since they should to be unique
                        raise DuplicateTimeFenceName
                self._policy['factors'][key]['attributes']['time fences'].append(new_time)
                return

        # If the timefence factor does not exist at all, we need to create it
        self._policy['factors'].append({
            "factor": "timefence",
            "requirement": "forced requirement",
            "quickfail": False,
            "priority": 1,
            "attributes": {
                "time fences": [
                    new_time
                ]
            }
        })

    def remove_timefence(self, name):
        """
        Removes a Time-Fence based on an input name
        :param name: String name of the Time-Fence
        :return:
        """
        for key, factor in enumerate(self._policy['factors']):
            if 'factor' in factor and factor['factor'] == 'timefence':
                for loc_key, location in enumerate(factor['attributes']['time fences']):
                    if location['name'].lower() == name.lower():
                        del self._policy['factors'][key]['attributes']['time fences'][loc_key]
                        for time_key, time in enumerate(self.timefences):
                            if time.name.lower() == name.lower():
                                del self.timefences[time_key]
                                return
        raise InvalidTimeFenceName

    def _parse_factors(self, factors):
        for factor in factors:
            if 'factor' in factor and 'attributes' in factor and factor['attributes']:
                if factor['factor'] == 'timefence' and 'time fences' in factor['attributes']:
                    for fence in factor['attributes']['time fences']:
                        # Dict comp to convert the days list into kwargs
                        kwargs = {day.lower(): True for day in fence['days']}
                        self.timefences.append(
                            TimeFence(
                                fence['name'],
                                datetime.time(hour=fence['start hour'], minute=fence['start minute'],
                                              tzinfo=pytz.timezone(fence['timezone'])),
                                datetime.time(hour=fence['end hour'], minute=fence['end minute'],
                                              tzinfo=pytz.timezone(fence['timezone'])),
                                **kwargs
                            )
                        )

        return super(ServiceSecurityPolicy, self)._parse_factors(factors)


class Service(object):
    """LaunchKey Service. Can be either an Organization or Directory Service."""

    def __init__(self, service_data):
        self.id = service_data['id']
        self.icon = service_data['icon']
        self.name = service_data['name']
        self.description = service_data['description']
        self.active = service_data['active']
        self.callback_url = service_data['callback_url']
