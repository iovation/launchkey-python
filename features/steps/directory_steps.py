from uuid import uuid4

from behave import given, when, then
from hamcrest import assert_that, equal_to, empty


# Create Directory


@given("I created a Directory")
@when("I create a Directory with a unique name")
def create_directory(context):
    context.sent_directory_name = str(uuid4())
    directory = context.directory_manager.create_directory(
        name=context.sent_directory_name)
    context.received_directory_id = directory.id


@given("I attempt to create a Directory with the same name")
def attempt_to_create_directory_matching_current_directory_name(context):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_manager.create_directory(
            name=current_directory.name)
    except Exception as e:
        context.current_exception = e


# Retrieve Directory

@when("I retrieve the updated Directory")
@when("I retrieve the created Directory")
@when("I retrieve the current Directory")
def retrieve_current_directory(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.retrieve_directory(current_directory.id)


@when("I attempt retrieve the Directory identified by \"{directory_id}\"")
def attempt_to_retrieve_directory_from_id(context, directory_id):
    try:
        context.directory_manager.retrieve_directory(directory_id)
    except Exception as e:
        context.current_exception = e


@then("the Directory name is the same as was sent")
def verify_directory_name_matches_sent_name(context):
    current_directory = context.entity_manager.get_current_directory()
    if current_directory.name != context.sent_directory_name:
        raise Exception("Directory name does not match what was sent")


@when("I retrieve a list of all Directories")
def retrieve_list_of_directories(context):
    context.directory_manager.retrieve_all_directories()


@then("the current Directory is in the Directory list")
def verify_current_directory_is_in_directory_list(context):
    current_directory = context.entity_manager.get_current_directory()
    current_directories = context.entity_manager.get_current_directory_list()
    for directory in current_directories:
        if directory.id == current_directory.id:
            return
    raise Exception("Current directory wasn't in the Directory list")


@when("I retrieve a list of Directories with the created Directory's ID")
def retrieve_list_of_directories_from_active_directory_id(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.retrieve_directories([current_directory.id])


@when("I attempt retrieve a list of Directories with the Directory ID "
      "\"{directory_id}\"")
def retrieve_list_of_directories_using_given_id(context, directory_id):
    try:
        context.directory_manager.retrieve_directories([directory_id])
    except Exception as e:
        context.current_exception = e


@then("the current Directory list is a list with only the current Directory")
def verify_directory_list_only_contains_current_directory(context):
    current_directory = context.entity_manager.get_current_directory()
    current_directories = context.entity_manager.get_current_directory_list()
    if len(current_directories) != 1 and current_directories[0] != \
            current_directory:
        raise Exception("Current directory list did not consist of only the "
                        "current Directory: %s" % current_directories)


@then("the ID matches the value returned when the Directory was created")
def verify_directory_id_matches_what_was_returned(context):
    current_directory = context.entity_manager.get_current_directory()
    if context.received_directory_id != current_directory.id:
        raise Exception("Retrieved Directory ID does not match what was "
                        "returned")


@then("the Directory is active")
def verify_directory_is_active(context):
    current_directory = context.entity_manager.get_current_directory()
    if not current_directory.active:
        raise Exception("Directory was not active when it should have been")


@then("the Directory is not active")
def verify_directory_is_not_active(context):
    current_directory = context.entity_manager.get_current_directory()
    if current_directory.active:
        raise Exception("Directory was active when it should not have been")


@then("the Directory has no Android Key")
def verify_directory_does_not_have_android_key(context):
    current_directory = context.entity_manager.get_current_directory()
    if current_directory.android_key:
        raise Exception("Directory should not have had android key but it had:"
                        " %s" % current_directory.android_key)


@then("the Directory Android Key is \"{android_key}\"")
def verify_directory_android_key_matches_expected(context, android_key):
    current_directory = context.entity_manager.get_current_directory()
    if current_directory.android_key != android_key:
        raise Exception("Directory android key %s didn't match expected: %s" %
                        (current_directory.android_key, android_key))


@then("Directory the iOS Certificate Fingerprint matches the provided "
      "certificate")
def verify_directory_ios_certificate_fingerprint_matches_expected(context):
    current_directory = context.entity_manager.get_current_directory()
    expected_fingerprint = context.keys_manager.alpha_certificate_fingerprint
    if current_directory.ios_certificate_fingerprint != expected_fingerprint:
        raise Exception("Directory ios cert %s didn't match expected: %s" %
                        (current_directory.ios_certificate_fingerprint,
                         expected_fingerprint))


@then("the Directory has the added SDK Key")
@then("the SDK Key is in the list for the Directory")
def verify_directory_sdk_keys(context):
    current_directory = context.entity_manager.get_current_directory()
    sdk_keys = context.entity_manager.get_current_directory_sdk_keys()
    if set(current_directory.sdk_keys) != set(sdk_keys):
        raise Exception("Directory SDK Keys %s did not match expected: %s" %
                        (current_directory.sdk_keys, sdk_keys))


@then("the Directory has the added Service IDs")
def verify_directory_has_two_service_ids(context):
    current_directory = context.entity_manager.get_current_directory()
    if len(current_directory.service_ids) != 2:
        raise Exception("Directory did not have 2 expected Service IDs" %
                        current_directory.service_ids)


@when("I retrieve the current Directory's SDK Keys")
def retrieve_current_directory_sdk_keys(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.retrieve_directory_sdk_keys(current_directory.id)


@when("I attempt to retrieve the current Directory SDK Keys for the Directory "
      "with the ID \"{directory_id}\"")
def attempt_to_retieve_directory_sdk_keys_from_directory_id(context,
                                                            directory_id):
    try:
        context.directory_manager.retrieve_directory_sdk_keys(directory_id)
    except Exception as e:
        context.current_exception = e


@then("all of the SDK Keys for the Directory are in the SDK Keys list")
def verify_directory_sdk_keys_match_expected(context):
    previous = context.entity_manager.get_previous_directory_sdk_keys()
    current = context.entity_manager.get_current_directory_sdk_keys()
    if set(previous) != set(current):
        raise Exception("Expected SDK Keys to be %s but they were: %s" % (
            previous, current))


@then("the last generated SDK Key is not in the list for the Directory")
def verify_last_generated_sdk_key_not_in_list(context):
    previous = context.entity_manager.get_previous_directory_sdk_keys()
    current = context.entity_manager.get_current_directory_sdk_keys()
    if previous[-1] in current:
        raise Exception("Last generated SDK key %s was in list: %s" %
                        (previous[-1], current))


# Update directory

@given("I updated the Directory as active")
def update_directory_to_active(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.update_directory(current_directory.id,
                                               active=True)


@when("I attempt to update the active status of the Directory with the ID "
      "\"{directory_id}\"")
def attempt_to_update_directory_active_status_with_directory_id(context,
                                                                directory_id):
    try:
        context.directory_manager.update_directory(directory_id, active=True)
    except Exception as e:
        context.current_exception = e


@when("I update the Directory as inactive")
def update_directory_to_active(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.update_directory(current_directory.id,
                                               active=False)


@when("I update the Directory Android Key with null")
def update_directory_android_key_as_null(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.update_directory(current_directory.id,
                                               android_key=None)


@when("I update the Directory Android Key with \"{android_key}\"")
@given("I updated the Directory Android Key with \"{android_key}\"")
def update_directory_android_key(context, android_key):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.update_directory(current_directory.id,
                                               android_key=android_key)


@when("I update the Directory iOS P12 with a valid certificate")
@given("I updated the Directory iOS P12 with a valid certificate")
def update_directory_ios_p12(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.update_directory(
        current_directory.id,
        ios_p12=context.keys_manager.alpha_p12
    )


@when("I update the Directory iOS P12 with null")
def update_directory_ios_p12_to_null(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.update_directory(
        current_directory.id,
        ios_p12=None
    )


@then("the Directory has no IOS Certificate Fingerprint")
def verify_directory_ios_fingerprint_is_not_set(context):
    current_directory = context.entity_manager.get_current_directory()
    if current_directory.ios_certificate_fingerprint:
        raise Exception("IOS Certificate fingerprint was not null: %s"
                        % current_directory.ios_certificate_fingerprint)


@given("I have added an SDK Key to the Directory")
@when("I generate and add an SDK Key to the Directory")
def generate_and_add_sdk_key_to_directory(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.generate_and_add_directory_sdk_key_to_directory(
        current_directory.id
    )


@when("I attempt to generate and add an SDK Key to the Directory with the ID "
      "\"{directory_id}\"")
def attempt_to_generate_and_add_sdk_key_to_directory_id(context, directory_id):
    try:
        context.directory_manager.generate_and_add_directory_sdk_key_to_directory(
            directory_id
        )
    except Exception as e:
        context.current_exception = e


@given("I generated and added {count:d} SDK Key to the Directory")
@given("I generated and added {count:d} SDK Keys to the Directory")
def generate_and_add_count_sdk_keys_to_directory(context, count):
    current_directory = context.entity_manager.get_current_directory()
    for x in range(count):
        context.directory_manager.\
            generate_and_add_directory_sdk_key_to_directory(
                current_directory.id
            )


@given("I added {count:d} Services to the Directory")
def add_count_services_to_directory(context, count):
    current_directory = context.entity_manager.get_current_directory()
    for x in range(count):
        context.directory_service_manager.\
            create_service(
                current_directory.id
            )


@given("I have removed the last generated SDK Key from the Directory")
@when("I remove the last generated SDK Key from the Directory")
def remove_last_generated_sdk_key(context):
    current_directory = context.entity_manager.get_current_directory()
    sdk_keys = context.entity_manager.get_current_directory_sdk_keys()
    context.directory_manager.remove_sdk_key_from_directory(
        sdk_keys[-1],
        current_directory.id
    )


@when("I attempt to remove the last generated SDK Key from the Directory")
def attempt_to_remove_last_generated_sdk_key_from_directory(context):
    current_directory = context.entity_manager.get_current_directory()
    sdk_keys = context.entity_manager.get_current_directory_sdk_keys()
    try:
        context.directory_manager.remove_sdk_key_from_directory(
            sdk_keys[-1],
            current_directory.id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to remove the last generated SDK Key from the Directory with "
      "the ID \"{directory_id}\"")
def attempt_to_remove_last_generated_sdk_key_from_directory_id(context,
                                                               directory_id):
    sdk_keys = context.entity_manager.get_current_directory_sdk_keys()
    try:
        context.directory_manager.remove_sdk_key_from_directory(
            sdk_keys[-1],
            directory_id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to remove the last generated SDK Key \"{sdk_key}\" from the "
      "Directory")
def attempt_to_remove_last_generated_sdk_key_from_directory(context, sdk_key):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_manager.remove_sdk_key_from_directory(
            sdk_key,
            current_directory.id
        )
    except Exception as e:
        context.current_exception = e


@given("I updated the Directory webhook url to \"{webhook_url}\"")
@when("I update the Directory webhook url to \"{webhook_url}\"")
def update_directory_webhook_url_to_value(context, webhook_url):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.update_directory(
        current_directory.id,
        webhook_url=webhook_url
    )


@when("I update the Directory webhook url to null")
def update_directory_webhook_url_to_value(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.update_directory(
        current_directory.id,
        webhook_url=None
    )


@then("the Directory webhook url is \"{webhook_url}\"")
def verify_directory_webhook_url_is_value(context, webhook_url):
    current_directory = context.entity_manager.get_current_directory()
    assert_that(current_directory.webhook_url, equal_to(webhook_url),
                "Directory webhook url is incorrect")


@then("the Directory webhook url is empty")
def verify_directory_webhook_url_is_null(context):
    current_directory = context.entity_manager.get_current_directory()
    assert_that(current_directory.webhook_url, empty(),
                "Directory webhook url is set when it shouldn't be")


@then('DenialContextInquiryEnabled is set to "{boolean}"')
@then('DenialContextInquiryEnabled should be set to "{boolean}"')
def denial_context_set_to_bool(context, boolean):
    current_directory = context.entity_manager.get_current_directory()
    assert_that(
        current_directory.denial_context_inquiry_enabled,
        bool(boolean),
        "DenialContext was not approriately set"
    )


@when('I update the DenialContextInquiryEnabled to "{boolean}"')
def step_impl(context, boolean):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.update_directory(
        current_directory.id,
        denial_context_inquiry_enabled=bool(boolean)
    )
