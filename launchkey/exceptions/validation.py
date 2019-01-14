"""Validators"""

from formencode import Schema, validators
from ..utils.validation import ValidateISODate


class AuthorizationInProgressValidator(Schema):
    """Pre-existing auth (Busy Signal) validation"""
    auth_request = validators.String()
    expires = ValidateISODate()
    from_same_service = validators.Bool()
    allow_extra_fields = True
