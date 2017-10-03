from formencode import Schema, validators, FancyValidator, Invalid, ForEach
from dateutil.parser import parse


class ValidateISODate(FancyValidator):

    @staticmethod
    def _to_python(value, state):
        try:
            val = parse(value)
        except ValueError:
            raise Invalid("Date/time format is invalid, it must be ISO 8601 formatted "
                          "for UTZ with no offset (i.e. 2010-01-01T01:01:01Z)", value, state)
        return val


class PublicKeyValidator(Schema):
    id = validators.String()
    active = validators.Bool()
    date_created = ValidateISODate()
    date_expires = ValidateISODate()
    public_key = validators.String()
    allow_extra_fields = True


class DirectoryUserDeviceLinkResponseValidator(Schema):
    qrcode = validators.String()  # URL
    code = validators.String(min=7)
    allow_extra_fields = True


class DirectoryGetDeviceResponseValidator(Schema):
    id = validators.String()
    name = validators.String()
    status = validators.Int()
    type = validators.String()
    allow_extra_fields = True


class DirectoryGetSessionsValidator(Schema):
    auth_request = validators.String()
    date_created = ValidateISODate()
    service_icon = validators.String()
    service_id = validators.String()
    service_name = validators.String()
    allow_extra_fields = True


class DirectoryValidator(Schema):
    id = validators.String()
    service_ids = ForEach(validators.String())
    sdk_keys = ForEach(validators.String())
    premium = validators.Bool()
    name = validators.String()
    android_key = validators.String()
    ios_certificate_fingerprint = validators.String()
    active = validators.Bool()
    allow_extra_fields = True


class AuthorizationResponseValidator(Schema):
    auth = validators.String()
    service_user_hash = validators.String()
    org_user_hash = validators.String()
    user_push_id = validators.String()
    public_key_id = validators.String()
    allow_extra_fields = True


class AuthorizationResponsePackageValidator(Schema):
    service_pins = ForEach()
    auth_request = validators.String()  # UUID
    response = validators.Bool()
    device_id = validators.String()
    allow_extra_fields = True


class AuthorizeValidator(Schema):
    auth_request = validators.String()
    allow_extra_fields = True


class AuthorizeSSEValidator(Schema):
    service_user_hash = validators.String()
    api_time = validators.String()
    allow_extra_fields = True


class ServiceValidator(Schema):
    id = validators.String()
    icon = validators.String()
    name = validators.String()
    description = validators.String()
    active = validators.Bool()
    callback_url = validators.String()
    allow_extra_fields = True


class ServiceSecurityPolicyValidator(Schema):
    allow_extra_fields = True
