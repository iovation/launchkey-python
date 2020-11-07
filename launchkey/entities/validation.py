"""Validators"""

# pylint: disable=too-few-public-methods

from formencode import Schema, validators, ForEach
from ..utils.validation import ValidateISODate


class PublicKeyValidator(Schema):
    """Public Key entity Validator"""
    id = validators.String()
    active = validators.Bool()
    date_created = ValidateISODate()
    date_expires = ValidateISODate()
    public_key = validators.String()
    key_type = validators.Int(if_missing=0, if_empty=0)
    allow_extra_fields = True


class DirectoryUserDeviceLinkResponseValidator(Schema):
    """Directory User Device link response validator"""
    qrcode = validators.String()  # URL
    code = validators.String(min=7)
    device_id = validators.String()
    allow_extra_fields = True


class DirectoryGetDeviceResponseValidator(Schema):
    """Directory get Device response validator"""
    id = validators.String()
    name = validators.String()
    status = validators.Int()
    type = validators.String()
    allow_extra_fields = True


class DirectoryGetSessionsValidator(Schema):
    """Directory get Sessions validator"""
    auth_request = validators.String()
    date_created = ValidateISODate()
    service_icon = validators.String()
    service_id = validators.String()
    service_name = validators.String()
    allow_extra_fields = True


class DirectoryValidator(Schema):
    """Directory entity validator"""
    id = validators.String()
    service_ids = ForEach(validators.String())
    sdk_keys = ForEach(validators.String())
    premium = validators.Bool()
    name = validators.String()
    android_key = validators.String()
    ios_certificate_fingerprint = validators.String()
    active = validators.Bool()
    denial_context_inquiry_enabled = validators.Bool(if_empty=False,
                                                     if_missing=False)
    webhook_url = validators.String()
    allow_extra_fields = True


class DirectoryDeviceLinkCompletionValidator(Schema):
    """Directory User Device link completion validator"""
    type = validators.OneOf(['DEVICE_LINK_COMPLETION'])
    device_id = validators.String()
    device_public_key = validators.String()
    device_public_key_id = validators.String()
    allow_extra_fields = True


class AuthorizationResponseValidator(Schema):
    """Authorization Response entity validator"""
    auth = validators.String()
    auth_jwe = validators.String(if_missing=None, if_empty=None)
    service_user_hash = validators.String()
    org_user_hash = validators.String()
    user_push_id = validators.String()
    public_key_id = validators.String()
    allow_extra_fields = True


class AuthorizationResponsePackageValidator(Schema):
    """Authorization Response Package entity validator"""
    service_pins = ForEach()
    auth_request = validators.String()  # UUID
    response = validators.Bool()
    device_id = validators.String()
    allow_extra_fields = True


class AuthMethodsValidator(Schema):
    """Auth methods validator"""
    method = validators.String()
    set = validators.Bool(if_empty=None)
    active = validators.Bool(if_empty=None)
    allowed = validators.Bool(if_empty=None)
    supported = validators.Bool(if_empty=None)
    user_required = validators.Bool(if_empty=None)
    passed = validators.Bool(if_empty=None)
    error = validators.Bool(if_empty=None)


class GeoFenceValidator(Schema):
    """ GeoFence Validator, can represent both GeoFence and GeoCircleFence """
    name = validators.String(if_missing=None)
    latitude = validators.Number()
    longitude = validators.Number()
    radius = validators.Number()


class GeoCircleFenceValidator(GeoFenceValidator):
    """ GeoFence Validator, can represent ONLY GeoCircleFence """
    type = validators.OneOf(["GEO_CIRCLE"])


class TerritoryFenceValidator(Schema):
    """ TerritoryFence Validator"""
    name = validators.String(if_missing=None)
    type = validators.OneOf(["TERRITORY"], if_missing=None)
    country = validators.Regex(r"^[A-Z]{2}$", not_empty=True)
    administrative_area = validators.Regex(r"^[A-Z]{2}-[A-Z]{2}[A-Z]?$",
                                           if_missing=None)
    postal_code = validators.String(if_missing=None, if_empty=None)

    @staticmethod
    def _validate_python(value, _state):
        if not value["administrative_area"]:
            del value["administrative_area"]

        if not value["postal_code"]:
            del value["postal_code"]


class FenceValidator(Schema):
    """Fence validator"""
    allow_extra_fields = True
    type = validators.OneOf(["GEO_CIRCLE", "TERRITORY"], if_missing=None)
    name = validators.String(if_missing=None)

    @staticmethod
    def _validate_python(value, _state):
        if not value["type"]:
            del value["type"]
            GeoFenceValidator().to_python(value)

        elif value["type"] == "GEO_CIRCLE":
            GeoCircleFenceValidator().to_python(value)

        elif value["type"] == "TERRITORY":
            TerritoryFenceValidator().to_python(value)


class AuthPolicyValidator(Schema):
    """Auth policy validate for auth method insights"""
    requirement = validators.String(if_missing=None, if_empty=None)
    amount = validators.Number(if_missing=None)
    types = ForEach(validators.String(), if_missing=None)
    geofences = ForEach(FenceValidator(), if_missing=[], if_empty=[])


class PolicyTerritoryValidator(Schema):
    """Validates Territory fences inside policies"""
    allow_extra_fields = True
    country = validators.String(not_empty=True)
    administrative_area = validators.String(if_missing=None)
    postal_code = validators.String(if_missing=None, if_empty=None)


class PolicyGeoCircleValidator(Schema):
    """Validates GeoCircle fences inside policies"""
    allow_extra_fields = True
    latitude = validators.Number(not_empty=True)
    longitude = validators.Number(not_empty=True)
    radius = validators.Number(not_empty=True)


class PolicyFenceValidator(Schema):
    """Validates fence objects in policies"""
    allow_extra_fields = True
    type = validators.String(not_empty=True)
    name = validators.String(if_missing=None, not_empty=True)

    @staticmethod
    def _validate_other(value, state):
        if "type" in value:
            if value["type"] == "TERRITORY":
                value.update(PolicyTerritoryValidator().to_python(
                    value, state))
            elif value["type"] == "GEO_CIRCLE":
                value.update(PolicyGeoCircleValidator().to_python(
                    value, state))
        return value


class ConditionalGeoFenceValidator(Schema):
    """Validates conditional geofence policies"""
    allow_extra_fields = True
    inside = validators.NotEmpty(accept_iterator=True)
    outside = validators.NotEmpty(accept_iterator=True)
    fences = ForEach(not_empty=True)

    @staticmethod
    def _validate_python(value, state):
        if 'inside' in value and 'outside' in value:
            value['inside'] = PolicyBaseValidator().to_python(
                value['inside'], state)
            value['outside'] = PolicyBaseValidator().to_python(
                value['outside'], state)
        return value


class MethodAmountPolicyValidator(Schema):
    """Validates method amount policies"""
    allow_extra_fields = True
    amount = validators.Int(not_empty=True)


class FactorsPolicyValidator(Schema):
    """Validates factors for policies"""
    allow_extra_fields = True
    factors = ForEach(validators.OneOf(
        ["KNOWLEDGE", "INHERENCE", "POSSESSION"]), not_empty=True)


class PolicyBaseValidator(Schema):
    """Base policy validator for legacy and new policies"""
    allow_extra_fields = True
    type = validators.String(if_missing="LEGACY")
    fences = ForEach(PolicyFenceValidator())

    @staticmethod
    def _validate_python(value, state):
        if value["type"] == "COND_GEO":
            value.update(ConditionalGeoFenceValidator().to_python(
                value, state))
        elif value["type"] == "METHOD_AMOUNT":
            value.update(MethodAmountPolicyValidator().to_python(value, state))
        elif value["type"] == "FACTORS":
            value.update(FactorsPolicyValidator().to_python(value, state))
        elif value["type"] == "LEGACY":
            if "deny_rooted_jailbroken" in value:
                del value["deny_rooted_jailbroken"]
            if "deny_emulator_simulator" in value:
                del value["deny_emulator_simulator"]
            del value["fences"]
        return value


class ServiceSecurityPolicyValidator(PolicyBaseValidator):
    """Service Policy validator"""
    allow_extra_fields = True
    deny_rooted_jailbroken = validators.Bool(if_missing=None)
    deny_emulator_simulator = validators.Bool(if_missing=None)


class JWEAuthorizationResponsePackageValidator(Schema):
    """Authorization Response JWE payload entity validator"""
    service_pins = ForEach()
    auth_request = validators.String()  # UUID
    type = validators.String()
    reason = validators.String()
    denial_reason = validators.String(if_missing=None, if_empty=None)
    device_id = validators.String()
    auth_policy = AuthPolicyValidator(if_missing=None)
    auth_methods = ForEach(AuthMethodsValidator())
    allow_extra_fields = True


class AuthorizeValidator(Schema):
    """Authorize entity validator"""
    auth_request = validators.String(not_empty=True)
    push_package = validators.String(if_missing=None, not_empty=True)
    device_ids = ForEach(validators.String(), if_missing=None)
    allow_extra_fields = True


class AuthorizeSSEValidator(Schema):
    """Authorize server-sent-event (webhook) validator"""
    service_user_hash = validators.String()
    api_time = validators.String()
    allow_extra_fields = True


class ServiceValidator(Schema):
    """Service entity validation"""
    id = validators.String()
    icon = validators.String()
    name = validators.String()
    description = validators.String()
    active = validators.Bool()
    callback_url = validators.String()
    allow_extra_fields = True


class ServiceTOTPVerificationValidator(Schema):
    """Service TOTP verification validation"""
    valid = validators.Bool()
    allow_extra_fields = True


class DirectoryUserTOTPValidator(Schema):
    """Directory TOTP post validator"""
    algorithm = validators.String()
    digits = validators.Int()
    period = validators.Int()
    secret = validators.String()
    allow_extra_fields = True
