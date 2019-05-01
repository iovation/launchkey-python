from uuid import uuid4

from behave import given, when, then
from formencode import Invalid, validators


@given("I made a Device linking request")
@when("I make a Device linking request")
def make_device_linking_request(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_device_manager.create_linking_request(
        user_identifier=str(uuid4()),
        directory_id=current_directory.id
    )


@then("the Device linking response contains a valid QR Code URL")
def linking_response_contains_valid_qr_code_url(context):
    try:
        validators.URL().to_python(
            context.entity_manager.get_current_linking_response().qrcode
        )
    except Invalid as e:
        raise Exception("Could not parse QR Code as URL: %s" % e)


@then("the Device linking response contains a valid Linking Code")
def linking_response_contains_valid_linking_code(context):
    code = context.entity_manager.get_current_linking_response().code
    if not code:
        raise Exception("Linking code was not valid: %s" % type(code))


@given("I retrieve the Devices list for the current User")
@when("I retrieve the Devices list for the current User")
def retrieve_devices_list_for_current_user(context):
    current_directory = context.entity_manager.get_current_directory()
    current_user_identifier = context.directory_device_manager.\
        current_user_identifier
    context.directory_device_manager.retrieve_user_devices(
        current_user_identifier, current_directory.id)


@when("I retrieve the Devices list for the user \"{user_identifier}\"")
def retrieve_devices_list_for_current_user(context, user_identifier):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_device_manager.retrieve_user_devices(
        user_identifier,
        current_directory.id
    )


@then("the Device List has {count:d} Device")
@then("the Device List has {count:d} Devices")
@then("there should be {count:d} Device in the Devices list")
@then("there should be {count:d} Devices in the Devices list")
def verify_device_list_count(context, count):
    current_device_list = context.entity_manager.get_current_device_list()
    if current_device_list is None or len(current_device_list) != count:
        raise Exception("Device list length length is not %s: %s" % (
            count, current_device_list))


@then("all of the devices should be inactive")
def verify_device_list_count(context):
    current_device_list = context.entity_manager.get_current_device_list()
    for device in current_device_list:
        if device.status.is_active:
            raise Exception("Device was active: %s" % device)


@then("all of the devices should be active")
def verify_device_list_count(context):
    current_device_list = context.entity_manager.get_current_device_list()
    for device in current_device_list:
        if not device.status.is_active:
            raise Exception("Device was not active: %s" % device)


@when("I unlink the Device with the ID \"{device_id}\"")
def unlink_device_with_id(context, device_id):
    current_directory = context.entity_manager.get_current_directory()
    current_user_identifier = context.directory_device_manager. \
        current_user_identifier
    context.directory_device_manager.unlink_device(
        device_id,
        current_user_identifier,
        current_directory.id
    )


@when("I unlink the current Device")
def unlink_current_device(context):
    current_directory = context.entity_manager.get_current_directory()
    current_user_identifier = context.directory_device_manager. \
        current_user_identifier
    current_device = context.entity_manager.get_current_device()
    context.directory_device_manager.unlink_device(
        current_device.id,
        current_user_identifier,
        current_directory.id
    )


@when("I attempt to unlink the device with the ID \"{device_id}\"")
def attempt_to_unlink_device_with_id(context, device_id):
    current_directory = context.entity_manager.get_current_directory()
    current_user_identifier = context.directory_device_manager. \
        current_user_identifier
    try:
        context.directory_device_manager.unlink_device(
            device_id,
            current_user_identifier,
            current_directory.id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to unlink the device from the User Identifier "
      "\"{user_identifier}\"")
def attempt_to_unlink_user_identifier_device(context, user_identifier):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_device_manager.unlink_device(
            str(uuid4()),
            user_identifier,
            current_directory.id
        )
    except Exception as e:
        context.current_exception = e

# Device manager steps


@given("I have a linked device")
def link_device(context):
    context.execute_steps('''
    Given I made a Device linking request
    When I link my device
    ''')


@when("I link my device")
def link_physical_device(context):
    sdk_key = context.entity_manager.get_current_directory_sdk_keys()[0]
    linking_code = context.entity_manager.get_current_linking_response().code
    context.sample_app_device_manager.link_device(sdk_key, linking_code)


@when("I link my physical device with the name \"{device_name}\"")
def link_device_with_name(context, device_name):
    sdk_key = context.entity_manager.get_current_directory_sdk_keys()[0]
    linking_code = context.entity_manager.get_current_linking_response().code
    context.sample_app_device_manager.link_device(sdk_key, linking_code,
                                                  device_name=device_name)


@when("I approve the auth request")
def approve_auth_request(context):
    context.sample_app_device_manager.approve_request()


@when("I deny the auth request")
def deny_auth_request(context):
    context.sample_app_device_manager.deny_request()


@when("I receive the auth request and acknowledge the failure message")
def deny_auth_request(context):
    context.sample_app_device_manager.receive_and_acknowledge_auth_failure()
