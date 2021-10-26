from behave import then
from launchkey.entities.shared import KeyType


@then("a {exception_class} error occurs")
@then("an {exception_class} error occurs")
def verify_exception_has_occured(context, exception_class):
    if context.current_exception is None:
        raise Exception("%s error expected, but it did not occur.")
    elif context.current_exception.__class__.__name__ != exception_class:
        raise context.current_exception


@then("there are no errors")
def verify_no_exceptions_have_occured(context):
    if context.current_exception:
        raise Exception("An exception was raised when it shouldn't have been: "
                        "%s" % context.current_exception)


def string_to_key_type(rawkeytype):
    switch = {
        "BOTH": KeyType.BOTH,
        "ENCRYPTION": KeyType.ENCRYPTION,
        "SIGNATURE": KeyType.SIGNATURE
    }
    return switch.get(rawkeytype.upper(), KeyType.OTHER)
