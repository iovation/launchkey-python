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
    """GeoFence validator"""
    name = validators.String(if_missing=None)
    latitude = validators.Number()
    longitude = validators.Number()
    radius = validators.Number()


class AuthPolicyValidator(Schema):
    """Auth policy validate for auth method insights"""
    requirement = validators.String(if_missing=None, if_empty=None)
    amount = validators.Number(if_missing=None)
    types = ForEach(validators.String(), if_missing=None)
    geofences = ForEach(GeoFenceValidator(), if_missing=[], if_empty=[])


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


class ServiceSecurityPolicyValidator(Schema):
    """Service Security Policy entity validator"""
    allow_extra_fields = True
