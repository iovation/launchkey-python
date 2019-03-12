from dateutil.parser import parse
from calendar import timegm

from behave import given, when, then

from launchkey.entities.shared import PublicKey


# Add public keys

@when("I add a Public Key to the Directory Service")
@given("I added a Public Key to the Directory Service")
def add_public_key_to_directory_service(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key
    })
    context.directory_service_manager.add_public_key_to_service(
        current_directory.id,
        public_key,
        current_service.id
    )


@when("I attempt to add the same Public Key to the Directory Service")
def attempt_to_add_public_key_to_directory_service(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key
    })
    try:
        context.directory_service_manager.add_public_key_to_service(
            current_directory.id,
            public_key,
            current_service.id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to add a Public Key to the Directory Service with the ID "
      "\"{service_id}\"")
def attempt_to_add_public_key_to_directory_service(context, service_id):
    current_directory = context.entity_manager.get_current_directory()
    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key
    })
    try:
        context.directory_service_manager.add_public_key_to_service(
            current_directory.id,
            public_key,
            service_id
        )
    except Exception as e:
        context.current_exception = e


@given("I added another Public Key to the Directory Service")
@when("I add another Public Key to the Directory Service")
def add_another_public_key_to_directory_service(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    public_key = PublicKey({
        "id": context.keys_manager.beta_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.beta_public_key
    })
    context.directory_service_manager.add_public_key_to_service(
        current_directory.id,
        public_key,
        current_service.id
    )


@given("I added a Public Key to the Directory Service which is active and "
       "expires on \"{expiration_timestamp}\"")
def add_public_key_to_directory_with_expiration_time_and_active(
        context, expiration_timestamp):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()

    public_key = PublicKey({
        "id": context.keys_manager.beta_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": parse(expiration_timestamp),
        "public_key": context.keys_manager.alpha_public_key
    })

    context.directory_service_manager.add_public_key_to_service(
        current_directory.id,
        public_key,
        current_service.id
    )


@given("I added a Public Key to the Directory Service which is inactive and "
       "expires on \"{expiration_timestamp}\"")
def add_public_key_to_directory_with_expiration_time_and_inactive(
        context,
        expiration_timestamp):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()

    public_key = PublicKey({
        "id": context.keys_manager.beta_md5_fingerprint,
        "active": False,
        "date_created": None,
        "date_expires": parse(expiration_timestamp),
        "public_key": context.keys_manager.alpha_public_key
    })

    context.directory_service_manager.add_public_key_to_service(
        current_directory.id,
        public_key,
        current_service.id
    )


# Retrieve public keys

@when("I retrieve the current Directory Service's Public Keys")
def retrieve_directory_service_public_keys(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    context.directory_service_manager.retrieve_public_keys_list(
        current_directory.id,
        current_service.id
    )


@when("I attempt to retrieve the Public Keys for the Directory Service with "
      "the Service ID \"{service_id}\"")
def attempt_to_retrieve_directory_service_public_key_with_service_id(context,
                                                                     service_id):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_service_manager.retrieve_public_keys_list(
            current_directory.id,
            service_id
        )
    except Exception as e:
        context.current_exception = e


@then("the Directory Service Public Keys list is empty")
def verify_directory_service_public_keys_list_is_empty(context):
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_service_public_keys()
    if current_directory_public_keys:
        raise Exception("Expected public keys list to be empty but it was: %s"
                        % current_directory_public_keys)


@then("the Directory Service Public Key is in the list of Public Keys for the "
      "Directory Service")
@then("the Public Key is in the list of Public Keys for the Directory Service")
def verify_directory_service_public_key_is_in_list_of_public_keys(context):
    alpha_public_key = context.keys_manager.alpha_public_key
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_service_public_keys()
    for key in current_directory_public_keys:
        if key.public_key == alpha_public_key:
            return
    raise Exception("Unable to find the current directory public key")


@then("the other Public Key is in the list of Public Keys for the Directory "
      "Service")
def verify_other_directory_service_public_key_is_in_list_of_public_keys(context):
    beta_public_key = context.keys_manager.beta_public_key
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_service_public_keys()
    for key in current_directory_public_keys:
        if key.public_key == beta_public_key:
            return
    raise Exception("Unable to find the other directory public key")


@then("the Directory Service Public Key is inactive")
def verify_directory_service_public_key_is_inactive(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_service_public_keys()
    for key in current_directory_public_keys:
        if key.id == key_id:
            if not key.active:
                return
            else:
                raise Exception("Key was set to active when it was "
                                "expected as inactive")
    raise Exception("Unable to find the current directory public key")


@then("the Directory Service Public Key Expiration Date is "
      "\"{expiration_timestamp}\"")
def verify_directory_service_public_key_expiration_date(context,
                                                        expiration_timestamp):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_service_public_keys()
    for key in current_directory_public_keys:
        if key.id == key_id:
            if key.expires == parse(expiration_timestamp):
                return
            else:
                print(parse(expiration_timestamp))
                raise Exception("Public key expiration date was not "
                                "what was expected: %s" % key.expires)


@then("the last current Directory Service's Public Key is not in the list")
def verify_first_public_key_is_not_in_directory_service_public_keys(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_directory_public_keys = context.entity_manager. \
        get_current_directory_service_public_keys()
    for key in current_directory_public_keys:
        if key.id == key_id:
            raise Exception("Last current public key was found when it "
                            "shouldn't have been")


# Remove public key


@when("I remove the current Directory Service Public Key")
def remove_current_directory_service_public_key(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    context.directory_service_manager.remove_public_key(
        current_directory.id,
        key_id,
        current_service.id
    )


@when("I attempt to remove the current Directory Service Public Key")
def attempt_to_remove_current_directory_service_public_key(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_service_manager.remove_public_key(
            current_directory.id,
            key_id,
            current_service.id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to remove a Public Key from the Directory Service with the "
      "ID \"{service_id}\"")
def attempt_to_remove_public_key_from_directory_service_from_id(context,
                                                                service_id):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_service_manager.remove_public_key(
            current_directory.id,
            key_id,
            service_id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to remove a Public Key identified by \"{key_id}\" "
      "from the Directory Service")
def attempt_to_remove_directory_service_public_key_from_key_id(context, key_id):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_service_manager.remove_public_key(
            current_directory.id,
            key_id,
            current_service.id
        )
    except Exception as e:
        context.current_exception = e


# Update public key

@when("I updated the Directory Service Public Key to inactive")
def update_dirtory_service_public_key_to_inactive(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    key_id = context.keys_manager.alpha_md5_fingerprint
    context.directory_service_manager.update_public_key(
        current_directory.id,
        key_id,
        current_service.id,
        active=False
    )


@when("I updated the Directory Service Public Key expiration date to "
      "\"{expiration_timestamp}\"")
def update_directory_service_public_key_expiration_date(context,
                                                        expiration_timestamp):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    key_id = context.keys_manager.alpha_md5_fingerprint
    context.directory_service_manager.update_public_key(
        current_directory.id,
        key_id,
        current_service.id,
        expires=parse(expiration_timestamp)
    )


@when("I attempt to update a Public Key for the Directory Service with the ID "
      "\"{service_id}\"")
def attempt_to_update_directory_service_public_key_with_service_id(context,
                                                                   service_id):
    current_directory = context.entity_manager.get_current_directory()
    key_id = context.keys_manager.alpha_md5_fingerprint
    try:
        context.directory_service_manager.update_public_key(
            current_directory.id,
            key_id,
            service_id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to update a Public Key identified by \"{key_id}\" for "
      "the Directory Service")
def attempt_to_update_directory_service_public_key_using_key_id(
        context, key_id):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_service_manager.update_public_key(
            current_directory.id,
            key_id,
            current_service.id
        )
    except Exception as e:
        context.current_exception = e
