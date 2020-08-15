from uuid import uuid4
from behave import when, then


@when("I verify a TOTP code with a valid code")
def verify_totp_using_valid_code(context):
    totp = context.entity_manager.get_current_totp_configuration()
    service_id = context.entity_manager.get_current_directory_service().id
    current_user_identifier = context.entity_manager.get_current_totp_user_identifier()
    context.directory_totp_manager.verify_totp(
        current_user_identifier,
        totp.now(),
        service_id
    )


@when("I verify a TOTP code with an invalid code")
def verify_totp_using_invalid_code(context):
    service_id = context.entity_manager.get_current_directory_service().id
    current_user_identifier = context.entity_manager.get_current_totp_user_identifier()
    context.directory_totp_manager.verify_totp(
        current_user_identifier,
        "123456",
        service_id
    )


@then("the TOTP verification response is True")
def verify_totp_verification_response_is_true(context):
    response = context.entity_manager.get_current_totp_verification_response()
    if response is not True:
        raise Exception("Expected totp response to be True but "
                        "it was: %s" % response)


@then("the TOTP verification response is False")
def verify_totp_verification_response_is_true(context):
    response = context.entity_manager.get_current_totp_verification_response()
    if response is not False:
        raise Exception("Expected totp response to be False but "
                        "it was: %s" % response)


@when("I attempt to verify a TOTP code with an invalid User")
def verify_totp_code_with_invalid_user(context):
    totp = context.entity_manager.get_current_totp_configuration()
    service_id = context.entity_manager.get_current_directory_service().id
    try:
        context.directory_totp_manager.verify_totp(
            str(uuid4()),
            totp.now(),
            service_id
        )
    except Exception as e:
        context.current_exception = e
