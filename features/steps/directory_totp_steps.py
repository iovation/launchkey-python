from uuid import uuid4
from behave import when, then, given


@when("I make a User TOTP create request")
@given("I have created a User TOTP")
def make_user_totp_create_request(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_totp_manager.generate_user_totp(
        str(uuid4()),
        current_directory.id,
    )


@then("the User TOTP create response contains a valid algorithm")
def verify_totp_response_contains_valid_algorithm(context):
    totp = context.entity_manager.get_current_totp_response()
    if not isinstance(totp.algorithm, str):
        raise Exception(
            "TOTP algorithm was expected to be string but it was a %s" % type(
                totp.algorithm)
        )
    valid_algorithms = ["SHA1", "SHA256", "SHA512"]
    if totp.algorithm.upper() not in valid_algorithms:
        raise Exception(
            "TOTP algorithm was expected to be one of %s but was %s" % (
                valid_algorithms, totp.algorithm)
        )


@then("the User TOTP create response contains a valid amount of digits")
def verify_totp_response_contains_valid_digits(context):
    totp = context.entity_manager.get_current_totp_response()
    if not isinstance(totp.digits, int):
        raise Exception(
            "TOTP digits was expected to be an int but it was a %s" % type(
                totp.digits)
        )
    if totp.digits < 6:
        raise Exception(
            "TOTP digits should have been at least 6 but was %s" % totp.digits
        )


@then("the User TOTP create response contains a valid period")
def verify_totp_response_contains_valid_period(context):
    totp = context.entity_manager.get_current_totp_response()
    if not isinstance(totp.period, int):
        raise Exception(
            "TOTP period was expected to be an int but it was a %s" % type(
                totp.period)
        )
    if totp.period < 30:
        raise Exception(
            "TOTP digits should have been at least 30 but was %s" % totp.period
        )


@then("the User TOTP create response contains a valid secret")
def verify_totp_response_contains_valid_secret(context):
    totp = context.entity_manager.get_current_totp_response()
    if not isinstance(totp.secret, str):
        raise Exception(
            "TOTP secret was expected to be an str but it was a %s" % type(
                totp.period)
        )
    if len(totp.secret) != 32:
        raise Exception(
            "TOTP secret should have been 32 characters but was %s" % totp.secret
        )


@when("I make a User TOTP delete request")
def delete_totp_for_current_user(context):
    current_directory = context.entity_manager.get_current_directory()
    current_user_identifier = context.entity_manager.get_current_totp_user_identifier()
    context.directory_totp_manager.remove_user_totp(
        current_user_identifier if current_user_identifier else str(uuid4()),
        current_directory.id,
    )
