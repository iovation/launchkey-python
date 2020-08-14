from uuid import uuid4
from behave import when


@when("I verify a TOTP code with a valid code")
def verify_totp_using_valid_code(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_totp_manager.remove_user_totp(
        str(uuid4()),
        current_directory.id,
    )

