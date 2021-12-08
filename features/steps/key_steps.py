from launchkey import LAUNCHKEY_PRODUCTION
from launchkey.factories import OrganizationFactory
from behave import given, when, then
from hamcrest import assert_that, equal_to, string_contains_in_order

from managers import DirectoryManager


@given("I am using single purpose keys")
def use_single_purpose_keys(context):
    organization_factory = OrganizationFactory(
        context.organization_id,
        context.organization_signature_private_key,
        url=getattr(context, 'launchkey_url', LAUNCHKEY_PRODUCTION)
    )

    organization_factory.add_encryption_private_key(context.organization_encryption_private_key)
    # Add single purpose key organization factory to context so it may be referenced
    # by other steps
    context.single_purpose_key_organization_factory = organization_factory


@given("I am using single purpose keys but I am using my encryption key to sign")
def use_single_purpose_keys_with_encryption_key_as_signature_key(context):
    # Intentionally passing encryption key as signature key
    organization_factory = OrganizationFactory(
        context.organization_id,
        context.organization_encryption_private_key,
        url=getattr(context, 'launchkey_url', LAUNCHKEY_PRODUCTION)
    )
    # Add single purpose key organization factory to context so it may be referenced
    # by other steps
    context.single_purpose_key_organization_factory = organization_factory


@given("I am using single purpose keys but I only set my signature key")
def use_single_purpose_keys(context):
    # Intentionally omitting encryption key in Organization Factory creation
    organization_factory = OrganizationFactory(
        context.organization_id,
        context.organization_signature_private_key,
        url=getattr(context, 'launchkey_url', LAUNCHKEY_PRODUCTION)
    )
    # Add single purpose key organization factory to context so it may be referenced
    # by other steps
    context.single_purpose_key_organization_factory = organization_factory


@when("I perform an API call using single purpose keys")
def perform_basic_api_call(context):
    directory_manager = DirectoryManager(context.single_purpose_key_organization_factory)
    directory_manager.create_directory()


@when("I attempt an API call using single purpose keys")
def attempt_basic_api_call(context):
    try:
        directory_manager = DirectoryManager(context.single_purpose_key_organization_factory)
        directory_manager.create_directory()

    except Exception as e:
        context.current_exception = e


@then("no valid key will be available to decrypt response")
def no_key_exists_to_decrypt_response(context):

    assert_that(str(context.current_exception),
                string_contains_in_order("The key id:", "could not be found in the entities available keys."))

    context.execute_steps("Then a EntityKeyNotFound error occurs")
