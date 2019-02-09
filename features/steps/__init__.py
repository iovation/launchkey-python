from uuid import uuid4

from behave import given, when, then, step
from formencode import Invalid, validators


# Directory Steps

@given("I created a Directory")
def create_directory(context):
    context.directory_manager.get_any_directory()


@given("I created a Directory Service")
def create_directory_service(context):
    pass


@given("I made a Device linking request")
def make_device_linking_request(context):
    pass

# Directory Device Steps


@when("I make a Device linking request")
def make_device_linking_request(context):
    context.device_manager.create_linking_request(
        user_identifier=str(uuid4())
    )


@then("the Device linking response contains a valid QR Code URL")
def linking_response_contains_valid_qr_code_url(context):
    try:
        validators.URL().to_python(
            context.device_manager.current_linking_response.qrcode
        )
    except Invalid as e:
        raise Exception("Could not parse QR Code as URL: %s" % e)


@then("the Device linking response contains a valid Linking Code")
def linking_response_contains_valid_linking_code(context):
    code = context.device_manager.current_linking_response.code
    if not code or not isinstance(code, str):
        raise Exception("Linking code was not valid: %s" % code)


@when("I retrieve the Devices list for the current User")
def retrieve_devices_list_for_current_user(context):
    context.device_manager.retrieve_user_devices()


@then("there should be {count:d} Device in the Devices list")
def verify_device_list_count(context, count):
    if context.device_manager.current_device_list is None or \
            len(context.device_manager.current_device_list) != count:
        raise Exception("Device list length length is not %s: %s" % (
            count, context.device_manager.current_device_list))
