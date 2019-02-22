"""Service Entity and sub entities"""

# pylint: disable=invalid-name,too-few-public-methods,too-many-arguments
# pylint: disable=redefined-builtin,too-many-instance-attributes
# pylint: disable=too-many-locals

import datetime
from json import loads, dumps
from enum import Enum
from formencode import Invalid
import pytz
from .validation import AuthorizationResponsePackageValidator, \
    JWEAuthorizationResponsePackageValidator
from ..exceptions import UnexpectedDeviceResponse, \
    InvalidGeoFenceName, InvalidTimeFenceEndTime, InvalidTimeFenceName, \
    InvalidTimeFenceStartTime, MismatchedTimeFenceTimezones, \
    DuplicateTimeFenceName, DuplicateGeoFenceName, InvalidPolicyFormat, \
    InvalidParameters


class AuthResponseReason(Enum):
    """Authentication Response Reason Enum"""
    APPROVED = "APPROVED"
    DISAPPROVED = "DISAPPROVED"
    FRAUDULENT = "FRAUDULENT"
    POLICY = "POLICY"
    PERMISSION = "PERMISSION"
    AUTHENTICATION = "AUTHENTICATION"
    CONFIGURATION = "CONFIGURATION"
    BUSY_LOCAL = "BUSY_LOCAL"
    OTHER = "OTHER"


class AuthResponseType(Enum):
    """Authentication Response Type Enum"""
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    FAILED = "FAILED"
    OTHER = "OTHER"


class GeoFence(object):
    """Geo-Fence entity"""
    def __init__(self, latitude, longitude, radius, name):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.radius = float(radius)
        self.name = name

    def __eq__(self, other):
        if isinstance(other, GeoFence):
            success = self.name == other.name and \
                      self.latitude == other.latitude and \
                      self.longitude == other.longitude and \
                      self.radius == other.radius
        else:
            success = False
        return success

    def __repr__(self):
        return "GeoFence <" \
               "name={name}, " \
               "latitude={latitude}, " \
               "longitude={longitude}, " \
               "radius={radius}>". \
            format(
                name=self.name,
                latitude=self.latitude,
                longitude=self.longitude,
                radius=self.radius
            )


class TimeFence(object):
    """Time-Fence entity"""
    def __init__(self, name, start_time, end_time, monday=False, tuesday=False,
                 wednesday=False, thursday=False, friday=False,
                 saturday=False, sunday=False):
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

    def __eq__(self, other):
        if isinstance(other, TimeFence):
            success = self.name == other.name and \
                      self.start_time == other.start_time and \
                      self.end_time == other.end_time and \
                      self.monday == other.monday and \
                      self.tuesday == other.tuesday and \
                      self.wednesday == other.wednesday and \
                      self.thursday == other.thursday and \
                      self.friday == other.friday and \
                      self.saturday == other.saturday and \
                      self.sunday == other.sunday and \
                      self.days == other.days
        else:
            success = False
        return success

    def __repr__(self):
        return "TimeFence <" \
               "name={name}, " \
               "start_time={start_time}, " \
               "end_time={end_time}, " \
               "monday={monday}, " \
               "tuesday={tuesday}, " \
               "wednesday={wednesday}, " \
               "thursday={thursday}, " \
               "friday={friday}, " \
               "saturday={saturday}, " \
               "sunday={sunday}>".\
            format(
                name=self.name,
                start_time=self.start_time,
                end_time=self.end_time,
                monday=self.monday,
                tuesday=self.tuesday,
                wednesday=self.wednesday,
                thursday=self.thursday,
                friday=self.friday,
                saturday=self.saturday,
                sunday=self.sunday
            )


class DenialReason(object):
    """
    Denial reason object to be passed in a list when creating an auth request

    :param denial_id: String. Universally unique identifier for this reason.
    This must be unique in an authorization request and should be unique
    globally for proper tracking of user selections.
    :param reason: String. Textual description of the reason that will be
    presented in a list for the user to select.
    :param fraud: Bool. Is the reason considered fraud.
    """

    def __init__(self, denial_id, reason, fraud):
        self.denial_id = denial_id
        self.reason = reason
        self.fraud = fraud


class AuthPolicy(object):
    """AuthPolicy object for performing dynamic authorizations"""

    def __init__(self, any=0, knowledge=False, inherence=False,
                 possession=False, jailbreak_protection=False):
        """
        Note that if any is used neither knowledge, inherence, nor possession
        can be used alongside it.

        If all values are left at 0, service defaults will be used.

        :param any: Int. Whether to require any x number of factors
        :param knowledge: Boolean. Whether to require knowledge factors
        :param inherence: Boolean. Whether to require inherence factors
        :param possession: Boolean. Whether to require possesion factors
        :param jailbreak_protection: Boolean. Whether to allow jailbroken /
               rooted devices to authenticate
        """

        if knowledge not in (True, False, 0, 1) \
                or inherence not in (True, False, 0, 1) \
                or possession not in (True, False, 0, 1):
            raise InvalidParameters("Inherence, knowledge, or possesion "
                                    "]input must be a boolean.")
        if any != 0 and (knowledge or inherence or possession):
            raise InvalidParameters("Cannot use \"any\" with other specific "
                                    "]factor requirements")

        self.geofences = []
        self.minimum_requirements = []
        self.minimum_amount = 0

        self._policy = {"factors": []}
        self.set_minimum_requirements(knowledge, inherence, possession, any)
        self.jailbreak_protection = jailbreak_protection
        self.require_jailbreak_protection(jailbreak_protection)

    def __eq__(self, other):
        if isinstance(other, AuthPolicy):
            eq = self.get_policy() == other.get_policy()
        else:
            eq = False
        return eq

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
            location = {"radius": float(radius),
                        "latitude": float(latitude),
                        "longitude": float(
                            longitude)}
            if name is not None:
                location['name'] = str(name)
        except TypeError:
            raise InvalidParameters("Latitude, Longitude, and Radius "
                                    "must all be numbers.")
        for i, factor in enumerate(self._policy['factors']):
            if factor.get('factor') == "geofence":
                self._policy['factors'][i]['attributes']['locations'].append(
                    location)
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
        def _remove_from_factors(name_):
            for key, factor in enumerate(self._policy['factors']):
                if 'factor' in factor and factor['factor'] == 'geofence':
                    for loc_key, location in enumerate(
                            factor['attributes']['locations']):
                        if 'name' in location \
                                and location['name'].lower() == name_.lower():
                            del self._policy['factors'][key]['attributes'][
                                'locations'][loc_key]
                            return True
            return False

        def _remove_from_fences(name):
            for geo_key, geo in enumerate(self.geofences):
                if geo.name.lower() == name.lower():
                    del self.geofences[geo_key]
                    return True
            return False

        if _remove_from_factors(name) and _remove_from_fences(name):
            return

        raise InvalidGeoFenceName

    def require_jailbreak_protection(self, status):
        """
        Enables or disables jailbreak and root protection (device integrity)
        for Auths
        :param status: Bool as to whether device integrity should be required
        :return:
        """
        enabled = 1 if status else 0
        self.jailbreak_protection = enabled == 1

        for key, factor in enumerate(self._policy['factors']):
            if 'factor' in factor and factor['factor'] == 'device integrity':
                self._policy['factors'][key]['attributes'] = \
                    {"factor enabled": 1 if status else 0}
                return

        self._policy['factors'].append({
            "factor": "device integrity",
            "requirement": "forced requirement",
            "quickfail": False,
            "priority": 1,
            "attributes": {"factor enabled": enabled}
        })

    def set_minimum_requirements(self, knowledge=False, inherence=False,
                                 possession=False, minimum_amount=0):
        """
        Sets minimum requirements that must be used for each Auth Request
        :param knowledge: Bool. Whether a Knowledge factor should be required.
        :param inherence: Bool. Whether an Inherence factor should be required.
        :param possession: Bool. Whether a Possession factor should be
        required.
        :param minimum_amount: Integer. Whether to require a minimum amount
        any nonspecific requirements.
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
            raise InvalidParameters("Policy input was not JSON serializable. "
                                    "Please verify it is correct.")
        return self._policy

    def set_policy(self, policy):
        """
        Updates a policy based on a given policy
        :param policy: Dict os JSON representation of a LaunchKey policy
        :return: None
        """
        if isinstance(policy, dict):
            self._policy = policy
        else:
            try:
                self._policy = loads(policy)
            except (ValueError, TypeError):
                raise InvalidPolicyFormat()

        if 'minimum_requirements' not in self._policy \
                or 'factors' not in self._policy:
            raise InvalidPolicyFormat()

        self._parse_minimum_requirements(self._policy['minimum_requirements'])
        self._parse_factors(self._policy['factors'])

    def _parse_minimum_requirements(self, minimum_requirements):
        # Although the API returns a list, we only support one
        # returned value as of now
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
            if 'factor' in factor and 'attributes' in factor \
                    and factor['attributes']:
                if factor['factor'] == 'geofence' \
                        and 'locations' in factor['attributes']:
                    for fence in factor['attributes']['locations']:
                        self.geofences.append(
                            GeoFence(fence['latitude'], fence['longitude'],
                                     fence['radius'],
                                     fence.get('name', None)))
                elif factor['factor'] == 'device integrity' \
                        and 'factor enabled' in factor['attributes']:
                    if factor['attributes']['factor enabled']:
                        self.jailbreak_protection = True


class AuthorizationRequest(object):
    """
    Authorization Response object containing decrypted auth response
    and other related information
    """

    def __init__(self, auth_request, push_package):
        self.auth_request = auth_request
        self.push_package = push_package


class AuthorizationResponse(object):
    """
    Authorization Response object containing decrypted auth response and
    other related information
    """

    @staticmethod
    def _get_authorized_bool_from_auth_response_context(response_type,
                                                        response_reason):
        return response_type == AuthResponseType.AUTHORIZED and \
               response_reason == AuthResponseReason.APPROVED

    @staticmethod
    def _retrieve_enum_from_value(enum_class, value):
        try:
            return enum_class(value)
        except ValueError:
            return enum_class.OTHER

    def _parse_device_response_from_jwe(self, jwe_payload, transport):
        """
        Parses a Device auth response using a JWE input.
        :param jwe_payload: JWE payload containing the device response.
        :param transport: Transport that contains the decrypt_response
                          method used to decrypt the Device response.
        :return:
        """
        try:
            data = transport.decrypt_response(jwe_payload)
            unmarshalled_package = loads(data)
            decrypted_jwe = JWEAuthorizationResponsePackageValidator().\
                to_python(unmarshalled_package)
        except (Invalid, TypeError, ValueError) as e:
            raise UnexpectedDeviceResponse("The device response was invalid. "
                                           "Please verify the same key that "
                                           "initiated the auth request is "
                                           "being used to decrypt the current "
                                           "message.", reason=e)

        self.type = self._retrieve_enum_from_value(AuthResponseType,
                                                   decrypted_jwe.get(
                                                       "type"))
        self.reason = self._retrieve_enum_from_value(AuthResponseReason,
                                                     decrypted_jwe.get(
                                                         "reason"))
        self.denial_reason = decrypted_jwe.get("denial_reason")
        self.fraud = self.reason is AuthResponseReason.FRAUDULENT
        self.authorization_request_id = decrypted_jwe.get("auth_request")
        self.authorized = \
            self._get_authorized_bool_from_auth_response_context(
                self.type,
                self.reason
            )
        self.device_id = decrypted_jwe.get("device_id")
        self.service_pins = decrypted_jwe.get("service_pins")

    def _parse_device_response_from_auth_package(self, auth_package, key_id,
                                                 transport):
        """
        Parses a Device auth response using a legacy auth package.
        :param auth_package: RSA Encrypted Device response.
        :param key_id: Key ID designating the key that the response
                       was encrypted to.
        :param transport: Transport that contains the _decrypt_auth_package
                          method used to decrypt the Device response.
        :return:
        """
        try:
            data = transport.decrypt_rsa_response(
                auth_package, key_id)
            unmarshalled_package = loads(data)
            # pylint: disable=no-value-for-parameter
            # noinspection PyArgumentList
            # The statement below should not work but does and will not work
            # when implemented properly. Disabling checks.
            decrypted_package = AuthorizationResponsePackageValidator.\
                to_python(unmarshalled_package)
            # pylint: enable=no-value-for-parameter
        except (Invalid, TypeError, ValueError) as e:
            raise UnexpectedDeviceResponse("The device response was invalid. "
                                           "Please verify the same key that "
                                           "initiated the auth request is "
                                           "being used to decrypt the current "
                                           "message.", reason=e)
        self.authorization_request_id = \
            decrypted_package.get("auth_request")
        self.authorized = decrypted_package.get("response")
        self.device_id = decrypted_package.get("device_id")
        self.service_pins = decrypted_package.get("service_pins")

    def _parse_device_response(self, data, transport):
        """
        Determines if a device has responded using JWE or legacy package format
        and triggers the appropriate parsing steps.
        :param data: Dictionary containing a LaunchKey Device's auth response
        :param transport: Transport that contains the needed steps to decrypt
                          A given Device response.
        :return: None
        """
        if data.get("auth_jwe"):
            self._parse_device_response_from_jwe(
                data.get("auth_jwe"), transport)
        else:
            self._parse_device_response_from_auth_package(
                data['auth'], data['public_key_id'], transport)

        self.service_user_hash = data.get("service_user_hash")
        self.organization_user_hash = data.get("org_user_hash")
        self.user_push_id = data.get("user_push_id")

    def __init__(self, data, transport):
        self.device_id = None
        self.type = None
        self.authorization_request_id = None
        self.service_pins = None
        self.authorized = None
        self.reason = None
        self.denial_reason = None
        self.fraud = None
        self._parse_device_response(data, transport)


class SessionEndRequest(object):
    """
    Session end request containing the logout_requested unix timestamp
    and the service_user_hash
    """

    def __init__(self, service_user_hash, api_time):
        self.logout_requested = api_time
        self.service_user_hash = service_user_hash


class ServiceSecurityPolicy(AuthPolicy):
    """
    Security Policy object containing specifics on policy that will be
    used in Auth Requests
    """

    def __init__(self, any=0, knowledge=False, inherence=False,
                 possession=False, jailbreak_protection=False):
        self.timefences = []

        super(ServiceSecurityPolicy, self).__init__(
            any, knowledge, inherence, possession, jailbreak_protection)

    def add_geofence(self, latitude, longitude, radius, name=None):
        """
        Adds a Geo-Fence requirement
        :param latitude: Float. Geographical Latitude
        :param longitude: Float. Geographical Longitude
        :param radius: Float. Radius of the Geo-Fence in meters
        :param name: String. Name identifier for the Geo-Fence. This
        should be unique.
        """
        if name is None:
            raise ValueError("name expected not to be None!")
        for fence in self.geofences:
            if fence.name.lower() == name.lower():
                # If the name exists, we should raise an
                # error since they should to be unique
                raise DuplicateGeoFenceName
        return super(ServiceSecurityPolicy, self).add_geofence(
            latitude, longitude, radius, name)

    def add_timefence(self, name, start_time, end_time, monday=False,
                      tuesday=False, wednesday=False, thursday=False,
                      friday=False, saturday=False, sunday=False):
        """
        Adds a Time-Fence requirement
        :param name: String. Name identifier for the Time-Fence. This should
        be unique.
        :param start_time: datetime.time object. A tzinfo value must be used if
        you do not want UTC. It must match the end_time tzinfo.
        :param end_time:  datetime.time object. A tzinfo value must be used if
        you do not want UTC. It must match the start_time tzinfo.
        :param monday: Bool. Whether the Time-Fence should be valid on Mondays
        :param tuesday: Bool. Whether the Time-Fence should be valid on
        Tuesdays
        :param wednesday: Bool. Whether the Time-Fence should be valid on
        Wednesdays
        :param thursday: Bool. Whether the Time-Fence should be valid on
        Thursdays
        :param friday: Bool. Whether the Time-Fence should be valid on Fridays
        :param saturday: Bool. Whether the Time-Fence should be valid on
        Saturdays
        :param sunday: Bool. Whether the Time-Fence should be valid on Sundays
        :return:
        """
        fence = TimeFence(name, start_time, end_time, monday=monday,
                          tuesday=tuesday, wednesday=wednesday,
                          thursday=thursday, friday=friday, saturday=saturday,
                          sunday=sunday)
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
                for fence in factor['attributes']['time fences']:
                    if fence['name'].lower() == name.lower():
                        # If the name exists, we should raise an error
                        # since they should to be unique
                        raise DuplicateTimeFenceName
                self._policy['factors'][key]['attributes']['time fences'] \
                    .append(new_time)
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
        def _remove_from_factors(name_):
            for key, factor in enumerate(self._policy['factors']):
                if 'factor' in factor and factor['factor'] == 'timefence':
                    for loc_key, location in \
                            enumerate(factor['attributes']['time fences']):
                        if location['name'].lower() == name_.lower():
                            del self._policy['factors'][key]['attributes'][
                                'time fences'][loc_key]
                            return True
            return False

        def _remove_from_fences(name_):
            for time_key, time in enumerate(self.timefences):
                if time.name.lower() == name_.lower():
                    del self.timefences[time_key]
                    return True
            return False

        if _remove_from_factors(name) and _remove_from_fences(name):
            return

        raise InvalidTimeFenceName

    def _parse_factors(self, factors):
        for factor in factors:
            if 'factor' in factor and 'attributes' in factor \
                    and factor['attributes']:
                if factor['factor'] == 'timefence' \
                        and 'time fences' in factor['attributes']:
                    for fence in factor['attributes']['time fences']:
                        # Dict comp to convert the days list into kwargs
                        kwargs = {day.lower(): True for day in fence['days']}
                        self.timefences.append(
                            TimeFence(
                                fence['name'],
                                datetime.time(
                                    hour=fence['start hour'],
                                    minute=fence['start minute'],
                                    tzinfo=pytz.timezone(fence['timezone'])),
                                datetime.time(
                                    hour=fence['end hour'],
                                    minute=fence['end minute'],
                                    tzinfo=pytz.timezone(fence['timezone'])),
                                **kwargs
                            )
                        )

        return super(ServiceSecurityPolicy, self)._parse_factors(factors)


class Service(object):
    """
    LaunchKey Service. Can be either an Organization or Directory Service.
    """

    def __init__(self, service_data):
        self.id = service_data['id']
        self.icon = service_data['icon']
        self.name = service_data['name']
        self.description = service_data['description']
        self.active = service_data['active']
        self.callback_url = service_data['callback_url']
