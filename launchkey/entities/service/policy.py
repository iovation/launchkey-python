""" Service Policy objects """
from enum import Enum

from launchkey.exceptions import InvalidFenceType, InvalidPolicyAttributes


# pylint: disable=too-few-public-methods
class Fence(object):
    """ Base class of all Fences """

    def __init__(self, name):
        self.name = name


# pylint: disable=too-few-public-methods
class Policy(object):
    """
    Base class for new policy objects
    """
    def __init__(self, fences):
        if not fences:
            fences = []

        for fence in fences:
            if not isinstance(fence, Fence):
                raise InvalidFenceType("Invalid Fence object. Fence must be "
                                       "one of the following: "
                                       "[\"GeoCircleFence\", \"Territory"
                                       "Fence\"]")
        self.fences = fences


class Requirement(Enum):
    """ Requirement Enum """
    AMOUNT = "AMOUNT"
    TYPES = "TYPES"
    COND_GEO = "COND_GEO"
    OTHER = "OTHER"


class AuthorizationResponsePolicy(Policy):
    """
    Represents the AMI Authorization Policy

    :param requirement: Requirement Enum representing the policy requirement
    :param amount: Integer representing amount of factors to enforce
    :param fences: List of fence objects
    :param inherence_required: Boolean. Whether to require inherence factor
    :param knowledge_required: Boolean. Whether to require knowledge factor
    :param possession_required: Boolean. Whether to require possession factor
    """

    # pylint: disable=too-many-arguments
    def __init__(self, requirement=None, amount=0, fences=None,
                 inherence_required=False, knowledge_required=False,
                 possession_required=False):
        super(AuthorizationResponsePolicy, self).__init__(fences)

        if requirement and not isinstance(requirement, Requirement):
            raise InvalidPolicyAttributes("Requirement must be an enumeration "
                                          "of \"Requirement\"")

        if requirement and isinstance(requirement, Requirement):
            self.requirement = requirement

        else:
            self.requirement = Requirement.OTHER

        self.amount = amount
        self.inherence_required = inherence_required
        self.knowledge_required = knowledge_required
        self.possession_required = possession_required

    def to_dict(self):
        """
        returns the JSON representation of the auth response policy
        """
        return dict(self)

    def __repr__(self):
        return "AuthorizationResponsePolicy <" \
               "requirement={requirement}, " \
               "fences={fences}, " \
               "amount={amount}, " \
               "inherence_required={inherence_required}, " \
               "knowledge_required={knowledge_required}, " \
               "possession_required={possession_required}>". \
            format(
                requirement=repr(self.requirement),
                fences=repr(self.fences),
                amount=self.amount,
                inherence_required=self.inherence_required,
                knowledge_required=self.knowledge_required,
                possession_required=self.possession_required
            )

    def __iter__(self):
        yield "requirement", self.requirement.name
        yield "fences", [dict(fence) for fence in self.fences]
        yield "amount", self.amount
        yield "inherence_required", self.inherence_required
        yield "knowledge_required", self.knowledge_required
        yield "possession_required", self.possession_required


class ConditionalGeoFencePolicy(Policy):
    """
    Provides an Auth Request the ability to have the device based on user
    location implement differing Auth Policies

    :param inside: Auth Policy to execute if the device is inside
    the fence(s)
    :param outside: Auth Policy to execute if the device is outside
    :param deny_rooted_jailbroken: Deny request if device reports that it is
    rooted/jailbroken
    :param deny_emulator_simulator: Deny request if device reports it is a
    simulator or an emulator
    :param fences: list.  List of fences that the device should check
    the fence(s)
    """

    #  pylint: disable=too-many-arguments
    def __init__(self, inside, outside, deny_rooted_jailbroken=False,
                 deny_emulator_simulator=False, fences=None):
        super(ConditionalGeoFencePolicy, self).__init__(fences)

        self.deny_rooted_jailbroken = deny_rooted_jailbroken
        self.deny_emulator_simulator = deny_emulator_simulator

        if inside.fences or outside.fences:
            raise InvalidPolicyAttributes("Fences are not allowed on Inside or"
                                          " Outside Policy objects")

        if inside.deny_rooted_jailbroken not in [False, None] or \
                outside.deny_rooted_jailbroken not in [False, None]:
            raise InvalidPolicyAttributes(
                "Setting deny_rooted_jailbroken is not allowed on Inside or "
                "Outside Policy objects"
            )

        if inside.deny_emulator_simulator not in [False, None] or \
                outside.deny_emulator_simulator not in [False, None]:
            raise InvalidPolicyAttributes(
                "Setting deny_emulator_simulator is not allowed on Inside or "
                "Outside Policy objects"
            )

        self.inside = self.__create_inner_policies(inside)
        self.outside = self.__create_inner_policies(outside)

    def to_dict(self):
        """
        returns the JSON representation of the policy object
        """
        return dict(self)

    def __repr__(self):
        return "ConditionalGeoFencePolicy <" \
               "inside={inside}, " \
               "outside={outside}, " \
               "deny_rooted_jailbroken={deny_rooted_jailbroken}, " \
               "deny_emulator_simulator={deny_emulator_simulator}, " \
               "fences={fences}>". \
            format(
                inside=repr(self.inside),
                outside=repr(self.outside),
                deny_rooted_jailbroken=self.deny_rooted_jailbroken,
                deny_emulator_simulator=self.deny_emulator_simulator,
                fences=repr(self.fences)
            )

    def __iter__(self):
        yield "type", "COND_GEO"
        yield "fences", [dict(fence) for fence in self.fences]
        yield "inside", dict(self.inside)
        yield "outside", dict(self.outside)
        yield "deny_rooted_jailbroken", self.deny_rooted_jailbroken
        yield "deny_emulator_simulator", self.deny_emulator_simulator

    # noinspection PyTypeChecker
    @staticmethod
    def __create_inner_policies(policy):
        if isinstance(policy, MethodAmountPolicy):
            new_policy = MethodAmountPolicy(
                amount=policy.amount, fences=None,
                deny_emulator_simulator=None, deny_rooted_jailbroken=None
            )
        elif isinstance(policy, FactorsPolicy):
            new_policy = FactorsPolicy(
                deny_rooted_jailbroken=None,
                deny_emulator_simulator=None,
                inherence_required=policy.inherence_required,
                knowledge_required=policy.knowledge_required,
                possession_required=policy.possession_required,
                fences=None
            )
        else:
            raise InvalidPolicyAttributes(
                "Inside and Outside policies must be one of the following: ["
                "\"FACTORS\", \"METHOD_AMOUNT\"]"
            )

        return new_policy


class LegacyPolicy(Policy):
    """
    Auth policy that loosely models the soon-to-be-deprecated
    `ServiceSecurityPolicy`

    :param amount: Integer amount of auth methods to require
    :param inherence_required: Boolean. Whether to require inherence factor
    :param knowledge_required: Boolean. Whether to require knowledge factor
    :param possession_required: Boolean. Whether to require possession factor
    :param deny_rooted_jailbroken: Boolean, deny request if device reports
    that it is rooted/jailbroken
    :param fences: List of GeoCircleFences
    :param time_restrictions: List of TimeFences
    """

    # pylint: disable=too-many-arguments
    def __init__(self, amount=0, inherence_required=False,
                 knowledge_required=False, possession_required=False,
                 deny_rooted_jailbroken=False, fences=None,
                 time_restrictions=None):

        sanitized_fences = []
        for fence in fences:
            if not isinstance(fence, GeoCircleFence):
                raise InvalidFenceType("A LegacyPolicy may only contain a "
                                       "GeoCircleFence.")

            sanitized_fences.append(fence)

        super(LegacyPolicy, self).__init__(sanitized_fences)
        self.amount = amount
        self.inherence_required = inherence_required
        self.knowledge_required = knowledge_required
        self.possession_required = possession_required
        self.deny_rooted_jailbroken = deny_rooted_jailbroken
        self.fences = [] if not fences else fences
        self.time_restrictions = [] if not time_restrictions else \
            time_restrictions

    def to_dict(self):
        """
        returns the JSON representation of the legacy policy object
        """
        return dict(self)

    def __repr__(self):
        return "LegacyPolicy <" \
               "amount={amount}, " \
               "inherence_required={inherence_required}, " \
               "knowledge_required={knowledge_required}, " \
               "possession_required={possession_required}, " \
               "deny_rooted_jailbroken={deny_rooted_jailbroken}, " \
               "fences={fences}, " \
               "time_restrictions={time_restrictions}>". \
            format(
                amount=self.amount,
                inherence_required=self.inherence_required,
                knowledge_required=self.knowledge_required,
                possession_required=self.possession_required,
                deny_rooted_jailbroken=self.deny_rooted_jailbroken,
                fences=repr(self.fences),
                time_restrictions=repr(self.time_restrictions)
            )

    def __iter__(self):
        yield "type", "LEGACY"
        yield "amount", self.amount
        yield "inherence_required", self.inherence_required
        yield "knowledge_required", self.knowledge_required
        yield "possession_required", self.possession_required
        yield "deny_rooted_jailbroken", self.deny_rooted_jailbroken
        yield "fences", [dict(f) for f in self.fences]
        yield "time_restrictions", [dict(f) for f in self.time_restrictions]


class MethodAmountPolicy(Policy):
    """
    Auth policy object that handles authentication by the amount of factors

    :param amount: amount of methods to be used in this AuthRequest
    :param deny_rooted_jailbroken: Deny request if device reports that it is
    rooted/jailbroken
    :param deny_emulator_simulator: Deny request if device reports it is a
    simulator or an emulator
    :param fences: list.  List of fences that the device should check
    """
    def __init__(self, amount=0, deny_rooted_jailbroken=False,
                 deny_emulator_simulator=False, fences=None):
        super(MethodAmountPolicy, self).__init__(fences)
        self.amount = amount
        self.deny_rooted_jailbroken = deny_rooted_jailbroken
        self.deny_emulator_simulator = deny_emulator_simulator

    def to_dict(self):
        """
        returns the JSON representation of the policy object
        """
        return dict(self)

    def __repr__(self):
        return "MethodAmountPolicy <" \
               "amount={amount}, " \
               "deny_rooted_jailbroken={deny_rooted_jailbroken}, " \
               "deny_emulator_simulator={deny_emulator_simulator}, " \
               "fences={fences}>". \
            format(
                amount=self.amount,
                deny_rooted_jailbroken=self.deny_rooted_jailbroken,
                deny_emulator_simulator=self.deny_emulator_simulator,
                fences=repr(self.fences)
            )

    def __iter__(self):
        yield "type", "METHOD_AMOUNT"
        yield "fences", [dict(fence) for fence in self.fences]
        yield "amount", self.amount
        if self.deny_rooted_jailbroken is not None:
            yield "deny_rooted_jailbroken", self.deny_rooted_jailbroken
        if self.deny_emulator_simulator is not None:
            yield "deny_emulator_simulator", self.deny_emulator_simulator


class FactorsPolicy(Policy):
    """
    Auth policy object that handles authentication based on type of factors

    Cannot be a mixed list of strings and Factor objects
    :param deny_rooted_jailbroken: Deny request if device reports that it is
    rooted/jailbroken
    :param deny_emulator_simulator: Deny request if device reports it is a
    simulator or an emulator
    :param inherence_required: Boolean. Whether to require inherence factor
    :param knowledge_required: Boolean. Whether to require knowledge factor
    :param possession_required: Boolean. Whether to require possession factor
    :param fences: List of fences to apply to the policy
    """

    # pylint: disable=too-many-arguments
    def __init__(self, deny_rooted_jailbroken=False,
                 deny_emulator_simulator=False, inherence_required=False,
                 knowledge_required=False, possession_required=False,
                 fences=None):
        super(FactorsPolicy, self).__init__(fences)
        self.deny_rooted_jailbroken = deny_rooted_jailbroken
        self.deny_emulator_simulator = deny_emulator_simulator
        self.inherence_required = inherence_required
        self.knowledge_required = knowledge_required
        self.possession_required = possession_required

    def __factors_list(self):
        factors = []
        if self.inherence_required:
            factors.append("INHERENCE")

        if self.knowledge_required:
            factors.append("KNOWLEDGE")

        if self.possession_required:
            factors.append("POSSESSION")

        return factors

    def to_dict(self):
        """
        returns the JSON representation of the policy object
        """
        return dict(self)

    def __repr__(self):
        return "FactorsPolicy <" \
               "deny_rooted_jailbroken={deny_rooted_jailbroken}, " \
               "deny_emulator_simulator={deny_emulator_simulator}, " \
               "inherence_required={inherence_required}, " \
               "knowledge_required={knowledge_required}, " \
               "possession_required={possession_required}, " \
               "fences={fences}>". \
            format(
                deny_rooted_jailbroken=self.deny_rooted_jailbroken,
                deny_emulator_simulator=self.deny_emulator_simulator,
                inherence_required=self.inherence_required,
                knowledge_required=self.knowledge_required,
                possession_required=self.possession_required,
                fences=repr(self.fences)
            )

    def __iter__(self):
        yield "type", "FACTORS"
        yield "fences", [dict(fence) for fence in self.fences]
        yield "factors", self.__factors_list()
        if self.deny_rooted_jailbroken is not None:
            yield "deny_rooted_jailbroken", self.deny_rooted_jailbroken
        if self.deny_emulator_simulator is not None:
            yield "deny_emulator_simulator", self.deny_emulator_simulator


class GeoCircleFence(Fence):
    """
    Represents a fence based on latitude, longitude, and radius

    :param latitude: represents the distance north or south of the equator
    :param longitude: represents the distance east or west of the meridian
    :param radius: radius of circle from the point
    :param name: name of the Fence
    """
    def __init__(self, latitude, longitude, radius, name=None):
        super(GeoCircleFence, self).__init__(name)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.radius = float(radius)

    def __repr__(self):
        return "GeoCircleFence <" \
               "latitude={latitude}, " \
               "longitude={longitude}, " \
               "radius={radius}, " \
               "name=\"{name}\">". \
            format(
                latitude=self.latitude,
                longitude=self.longitude,
                radius=self.radius,
                name=self.name
            )

    def __iter__(self):
        yield "type", "GEO_CIRCLE"
        yield "name", self.name
        yield "latitude", self.latitude
        yield "longitude", self.longitude
        yield "radius", self.radius

    def __eq__(self, other):
        if isinstance(other, GeoCircleFence):
            return self.latitude == other.latitude \
                and self.longitude == other.longitude \
                and self.radius == other.radius \
                and self.name == other.name

        return False


class TerritoryFence(Fence):
    """
    Represents a fence based on the territory

    :param country: two character representation of the country
    :param administrative_area:  ISO 3166-2 subdivision code ex: "US-CA"
    :param postal_code: string representation of area mail is delivered too
    :param name: name of the Fence
    """
    def __init__(self, country, administrative_area=None, postal_code=None,
                 name=None):
        super(TerritoryFence, self).__init__(name)
        self.country = country
        self.administrative_area = administrative_area
        self.postal_code = str(postal_code) if postal_code else None

    def __repr__(self):
        return "TerritoryFence <" \
               "country=\"{country}\", " \
               "administrative_area=\"{administrative_area}\", " \
               "postal_code=\"{postal_code}\", " \
               "name=\"{name}\">". \
            format(
                country=self.country,
                administrative_area=self.administrative_area,
                postal_code=self.postal_code,
                name=self.name
            )

    def __iter__(self):
        yield "type", "TERRITORY"
        yield "name", self.name
        yield "administrative_area", self.administrative_area
        yield "country", self.country
        yield "postal_code", self.postal_code

    def __eq__(self, other):
        if isinstance(other, TerritoryFence):
            return self.country == other.country \
                and self.administrative_area == other.administrative_area \
                and self.postal_code == other.postal_code \
                and self.name == other.name

        return False
