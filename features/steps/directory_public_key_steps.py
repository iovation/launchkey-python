from dateutil.parser import parse
from calendar import timegm

from behave import given, when, then

from launchkey.entities.shared import KeyType, PublicKey

from . import string_to_key_type

# Add public keys

@given("I added a Public Key to the Directory")
@when("I add a Public Key to the Directory")
def add_public_key_to_directory(context):
    current_directory = context.entity_manager.get_current_directory()
    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key
    })
    context.directory_manager.add_public_key_to_directory(
        public_key,
        current_directory.id
    )


@when("I add a Public Key with a {key_type} type to the Directory")
def add_public_key_with_key_type_to_directory_service(context, key_type):
    current_directory = context.entity_manager.get_current_directory()

    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key,
        "key_type": KeyType(int(key_type))
    })

    context.directory_manager.add_public_key_to_directory(
        public_key,
        current_directory.id
    )


@when("I attempt to add a Public Key with a \"{key_type}\" type to the Directory")
def add_public_key_with_key_type_to_directory_service(context, key_type):
    current_directory = context.entity_manager.get_current_directory()

    try:
        # Ensure that integers remain integers and are not recognized
        # by Selenium as strings, and that strings remain strings
        sanitized_key_type = int(key_type)

    except ValueError:
        sanitized_key_type = key_type

    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key,
        "key_type": sanitized_key_type
    })

    try:
        context.directory_manager.add_public_key_to_directory(
            public_key,
            current_directory.id
        )

    except Exception as e:
        context.current_exception = e


@when("I attempt to add the same Public Key to the Directory")
def attempt_to_add_public_key_to_directory_service(context):
    current_directory = context.entity_manager.get_current_directory()
    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key
    })
    try:
        context.directory_manager.add_public_key_to_directory(
            public_key,
            current_directory.id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to add a Public Key to the Directory with the ID "
      "\"{directory_id}\"")
def attempt_to_add_public_key_to_directory_service(context, directory_id):
    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key
    })
    try:
        context.directory_manager.add_public_key_to_directory(
            public_key,
            directory_id
        )
    except Exception as e:
        context.current_exception = e


@given("I added another Public Key to the Directory")
@when("I add another Public Key to the Directory")
def add_another_public_key_to_directory(context):
    current_directory = context.entity_manager.get_current_directory()
    public_key = PublicKey({
        "id": context.keys_manager.beta_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.beta_public_key
    })
    context.directory_manager.add_public_key_to_directory(
        public_key,
        current_directory.id
    )


@given("I added a Public Key to the Directory which is active and "
       "expires on \"{expiration_timestamp}\"")
def add_public_key_to_directory_with_expiration_time_and_active(
        context, expiration_timestamp):
    current_directory = context.entity_manager.get_current_directory()

    public_key = PublicKey({
        "id": context.keys_manager.beta_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": parse(expiration_timestamp),
        "public_key": context.keys_manager.alpha_public_key
    })

    context.directory_manager.add_public_key_to_directory(
        public_key,
        current_directory.id,
    )


@given("I added a Public Key to the Directory which is inactive and "
       "expires on \"{expiration_timestamp}\"")
def add_public_key_to_directory_with_expiration_time_and_inactive(
        context,
        expiration_timestamp):
    current_directory = context.entity_manager.get_current_directory()

    public_key = PublicKey({
        "id": context.keys_manager.beta_md5_fingerprint,
        "active": False,
        "date_created": None,
        "date_expires": parse(expiration_timestamp),
        "public_key": context.keys_manager.alpha_public_key
    })

    context.directory_manager.add_public_key_to_directory(
        public_key,
        current_directory.id,
    )


# Retrieve public keys

@when("I retrieve the current Directory's Public Keys")
def retrieve_directory_service_public_keys(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.retrieve_directory_public_keys(
        current_directory.id
    )


@when("I attempt to retrieve the Public Keys for the Directory with the "
      "ID \"{directory_id}\"")
def attempt_to_retrieve_directory_public_key_with_id(
        context, directory_id):
    try:
        context.directory_manager.retrieve_directory_public_keys(
            directory_id
        )
    except Exception as e:
        context.current_exception = e


@then("the Directory Public Keys list is empty")
def verify_directory_public_keys_list_is_empty(context):
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_public_keys()
    if current_directory_public_keys:
        raise Exception("Expected public keys list to be empty but it was: %s"
                        % current_directory_public_keys)


@then("the Public Key is in the list of Public Keys for the Directory")
def verify_directory_public_key_is_in_list_of_public_keys(context):
    alpha_public_key = context.keys_manager.alpha_public_key
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_public_keys()
    for key in current_directory_public_keys:
        if key.public_key == alpha_public_key:
            return
    raise Exception("Unable to find the current directory public key")


@then("the Public Key is in the list of Public Keys for the Directory and has "
      "a {key_type} key type")
@then("the Public Key is in the list of Public Keys for the Directory and has "
      "a \"{key_type}\" key type")
def verify_directory_public_key_is_in_list_of_public_keys(context, key_type):
    key_type_enum = string_to_key_type(key_type)
    alpha_public_key = context.keys_manager.alpha_public_key
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_public_keys()
    for key in current_directory_public_keys:
        if key.public_key == alpha_public_key and key.key_type == key_type_enum:
            return
    raise Exception("Unable to find the current directory public key")


@then("the other Public Key is in the list of Public Keys for the Directory")
def verify_other_directory_public_key_is_in_list_of_public_keys(context):
    beta_public_key = context.keys_manager.beta_public_key
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_public_keys()
    for key in current_directory_public_keys:
        if key.public_key == beta_public_key:
            return
    raise Exception("Unable to find the other directory public key")


@then("the Directory Public Key is inactive")
def verify_directory_public_key_is_inactive(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_public_keys()
    for key in current_directory_public_keys:
        if key.id == key_id:
            if not key.active:
                return
            else:
                raise Exception("Key was set to active when it was "
                                "expected as inactive")
    raise Exception("Unable to find the current directory public key")


@then("the Directory Public Key Expiration Date is "
      "\"{expiration_timestamp}\"")
def verify_directory_public_key_expiration_date(context,
                                                expiration_timestamp):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_public_keys()
    for key in current_directory_public_keys:
        if key.id == key_id:
            if key.expires == parse(expiration_timestamp):
                return
            else:
                print(parse(expiration_timestamp))
                raise Exception("Public key expiration date was not "
                                "what was expected: %s" % key.expires)


@then("the last current Directory's Public Key is not in the list")
def verify_first_public_key_is_not_in_directory_public_keys(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_public_keys()
    for key in current_directory_public_keys:
        if key.id == key_id:
            raise Exception("Last current public key was found when it "
                            "shouldn't have been")


# Remove public key


@when("I remove the current Directory Public Key")
def remove_current_directory_public_key(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_directory = context.entity_manager.get_current_directory()
    context.directory_manager.remove_directory_public_key(
        key_id,
        current_directory.id
    )


@when("I attempt to remove the current Directory Public Key")
def attempt_to_remove_current_directory_public_key(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_manager.remove_directory_public_key(
            key_id,
            current_directory.id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to remove a Public Key from the Directory with the "
      "ID \"{directory_id}\"")
def attempt_to_remove_public_key_from_directory_from_id(context, directory_id):
    key_id = context.keys_manager.alpha_md5_fingerprint
    try:
        context.directory_manager.remove_directory_public_key(
            key_id,
            directory_id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to remove a Public Key identified by \"{key_id}\" "
      "from the Directory")
def attempt_to_remove_directory_public_key_from_key_id(context, key_id):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_manager.remove_directory_public_key(
            key_id,
            current_directory.id
        )
    except Exception as e:
        context.current_exception = e


# Update public key

@when("I update the Directory Public Key to inactive")
def update_directory_public_key_to_inactive(context):
    current_directory = context.entity_manager.get_current_directory()
    key_id = context.keys_manager.alpha_md5_fingerprint
    context.directory_manager.update_directory_public_key(
        key_id,
        current_directory.id,
        active=False
    )


@when("I updated the Directory Public Key expiration date to "
      "\"{expiration_timestamp}\"")
def update_directory_public_key_expiration_date(context, expiration_timestamp):
    current_directory = context.entity_manager.get_current_directory()
    key_id = context.keys_manager.alpha_md5_fingerprint
    context.directory_manager.update_directory_public_key(
        key_id,
        current_directory.id,
        expires=parse(expiration_timestamp)
    )


@when("I attempt to update a Public Key for the Directory with the ID "
      "\"{directory_id}\"")
def attempt_to_update_directory_service_public_key_with_service_id(
        context, directory_id):
    key_id = context.keys_manager.alpha_md5_fingerprint
    try:
        context.directory_manager.update_directory_public_key(
            key_id,
            directory_id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to update a Public Key identified by \"{key_id}\" for "
      "the Directory")
def attempt_to_update_directory_public_key_using_key_id(
        context, key_id):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_manager.update_directory_public_key(
            key_id,
            current_directory.id
        )
    except Exception as e:
        context.current_exception = e
