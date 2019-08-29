""" Service Policy objects """

# pylint: disable=too-few-public-methods, too-many-arguments

from enum import Enum
from json import dumps

from launchkey.exceptions import InvalidFenceType, InvalidPolicyAttributes, \
    InvalidPolicyType


class Factor(Enum):
    """ Factors Enum"""
    KNOWLEDGE = "KNOWLEDGE"
    INHERENCE = "INHERENCE"
    POSSESSION = "POSSESSION"


class Fence(object):
    """ Base class of all Fences """


class Policy(object):
    """
    Base class for new policy objects
    """
    @classmethod
    def verify_fence_type(cls, fences):
        """
        Verifies the fence is of a valid type for the Policy
        """
        for fence in fences:
            if not isinstance(fence, Fence):
                raise InvalidFenceType("Invalid Fence object. Fence must be "
                                       "one of the following: "
                                       "[\"GeoCircleFence\", \"Territory"
                                       "Fence\", \"GeoFence\"]")


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

    def __init__(self, inside, outside, deny_rooted_jailbroken=False,
                 deny_emulator_simulator=False, fences=None):
        if not fences:
            fences = []

        super(ConditionalGeoFencePolicy, self)

        self.deny_rooted_jailbroken = deny_rooted_jailbroken
        self.deny_emulator_simulator = deny_emulator_simulator

        self.verify_fence_type(fences)

        self.fences = fences

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
        self.type = "COND_GEO"

    def to_json(self):
        """
        returns the JSON representation of the policy object
        """
        return dumps(dict(self))

    def __repr__(self):
        return repr(dict(self))

    def __iter__(self):
        yield "type", self.type
        yield "fences", [dict(fence) for fence in self.fences]
        yield "inside", dict(self.inside)
        yield "outside", dict(self.outside)
        yield "deny_rooted_jailbroken", self.deny_rooted_jailbroken
        yield "deny_emulator_simulator", self.deny_emulator_simulator

    # noinspection PyTypeChecker
    @staticmethod
    def __create_inner_policies(policy):
        if policy.type == "METHOD_AMOUNT":
            policy = MethodAmountPolicy(
                amount=policy.amount, fences=None,
                deny_emulator_simulator=None, deny_rooted_jailbroken=None
            )
        elif policy.type == "FACTORS":
            policy = FactorsPolicy(
                factors=policy.factors, fences=None,
                deny_rooted_jailbroken=None, deny_emulator_simulator=None
            )
        else:
            raise InvalidPolicyType(
                "Inside and Outside policies must be one of the following: ["
                "\"FACTORS\", \"METHOD_AMOUNT\"]")

        return policy


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
        if not fences:
            fences = []

        super(MethodAmountPolicy, self)
        self.amount = amount
        self.deny_rooted_jailbroken = deny_rooted_jailbroken
        self.deny_emulator_simulator = deny_emulator_simulator

        self.verify_fence_type(fences)
        self.fences = fences

        self.type = "METHOD_AMOUNT"

    def to_json(self):
        """
        returns the JSON representation of the policy object
        """
        return dumps(dict(self))

    def __repr__(self):
        return repr(dict(self))

    def __iter__(self):
        yield "type", self.type
        yield "fences", [dict(fence) for fence in self.fences]
        yield "amount", self.amount
        if self.deny_rooted_jailbroken is not None:
            yield "deny_rooted_jailbroken", self.deny_rooted_jailbroken
        if self.deny_emulator_simulator is not None:
            yield "deny_emulator_simulator", self.deny_emulator_simulator


class FactorsPolicy(Policy):
    """
    Auth policy object that handles authentication based on type of factors

    :param factors: List of factors that the device should use for the
    Auth request
    :param deny_rooted_jailbroken: Deny request if device reports that it is
    rooted/jailbroken
    :param deny_emulator_simulator: Deny request if device reports it is a
    simulator or an emulator
    :param fences: List of fences that the device should check
    """
    def __init__(self, factors=None, deny_rooted_jailbroken=False,
                 deny_emulator_simulator=False, fences=None):
        if not fences:
            fences = []
        if not factors:
            factors = []

        super(FactorsPolicy, self)
        self.deny_rooted_jailbroken = deny_rooted_jailbroken
        self.deny_emulator_simulator = deny_emulator_simulator

        self.verify_fence_type(fences)
        self.fences = fences
        self.factors = [
            Factor(factor) for factor in factors
        ]
        self.type = "FACTORS"

    def to_json(self):
        """
        returns the JSON representation of the policy object
        """
        return dumps(dict(self))

    def __repr__(self):
        return repr(dict(self))

    def __iter__(self):
        yield "type", self.type
        yield "fences", [dict(fence) for fence in self.fences]
        yield "factors", [factor.name for factor in self.factors]
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
        super(GeoCircleFence, self)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.radius = float(radius)
        self.name = name
        self.type = "GEO_CIRCLE"

    def __repr__(self):
        return repr(dict(self))

    def __iter__(self):
        yield "type", self.type
        yield "name", self.name
        yield "latitude", self.latitude
        yield "longitude", self.longitude
        yield "radius", self.radius


class TerritoryFence(Fence):
    """
    Represents a fence based on the territory

    :param country: two character representation of the country
    :param administrative_area:  ISO 3166-2 subdivision code ex: "US-CA"
    :param postal_code: representation of area mail is delivered too
    :param name: name of the Fence
    """
    def __init__(self, country, administrative_area, postal_code, name=None):
        super(TerritoryFence, self)
        self.country = country
        self.administrative_area = administrative_area
        self.postal_code = str(postal_code)
        self.name = name
        self.type = "TERRITORY"

    def __repr__(self):
        return repr(dict(self))

    def __iter__(self):
        yield "type", self.type
        yield "name", self.name
        yield "administrative_area", self.administrative_area
        yield "country", self.country
        yield "postal_code", self.postal_code
