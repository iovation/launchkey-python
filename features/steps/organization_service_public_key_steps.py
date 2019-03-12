from dateutil.parser import parse

from behave import given, when, then

from launchkey.entities.shared import PublicKey


# Add public keys

@when("I add a Public Key to the Organization Service")
@given("I added a Public Key to the Organization Service")
def add_public_key_to_organization_service(context):
    current_service = context.entity_manager.get_current_organization_service()
    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key
    })
    context.organization_service_manager.add_public_key_to_service(
        public_key,
        current_service.id
    )


@when("I attempt to add the same Public Key to the Organization Service")
def attempt_to_add_public_key_to_organization_service(context):
    current_service = context.entity_manager.get_current_organization_service()
    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key
    })
    try:
        context.organization_service_manager.add_public_key_to_service(
            public_key,
            current_service.id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to add a Public Key to the Organization Service with the ID "
      "\"{service_id}\"")
def attempt_to_add_public_key_to_organization_service(context, service_id):
    public_key = PublicKey({
        "id": context.keys_manager.alpha_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.alpha_public_key
    })
    try:
        context.organization_service_manager.add_public_key_to_service(
            public_key,
            service_id
        )
    except Exception as e:
        context.current_exception = e


@given("I added another Public Key to the Organization Service")
@when("I add another Public Key to the Organization Service")
def add_another_public_key_to_organization_service(context):
    current_service = context.entity_manager.get_current_organization_service()
    public_key = PublicKey({
        "id": context.keys_manager.beta_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": None,
        "public_key": context.keys_manager.beta_public_key
    })
    context.organization_service_manager.add_public_key_to_service(
        public_key,
        current_service.id
    )


@given("I added a Public Key to the Organization Service which is active and "
       "expires on \"{expiration_timestamp}\"")
def add_public_key_to_organization_with_expiration_time_and_active(
        context, expiration_timestamp):
    current_service = context.entity_manager.get_current_organization_service()

    public_key = PublicKey({
        "id": context.keys_manager.beta_md5_fingerprint,
        "active": True,
        "date_created": None,
        "date_expires": parse(expiration_timestamp),
        "public_key": context.keys_manager.alpha_public_key
    })

    context.organization_service_manager.add_public_key_to_service(
        public_key,
        current_service.id
    )


@given("I added a Public Key to the Organization Service which is inactive "
       "and expires on \"{expiration_timestamp}\"")
def add_public_key_to_organization_with_expiration_time_and_inactive(
        context,
        expiration_timestamp):
    current_service = context.entity_manager.get_current_organization_service()

    public_key = PublicKey({
        "id": context.keys_manager.beta_md5_fingerprint,
        "active": False,
        "date_created": None,
        "date_expires": parse(expiration_timestamp),
        "public_key": context.keys_manager.alpha_public_key
    })

    context.organization_service_manager.add_public_key_to_service(
        public_key,
        current_service.id
    )


# Retrieve public keys

@when("I retrieve the current Organization Service's Public Keys")
def retrieve_organization_service_public_keys(context):
    current_service = context.entity_manager.get_current_organization_service()
    context.organization_service_manager.retrieve_public_keys_list(
        current_service.id
    )


@when("I attempt to retrieve the Public Keys for the Organization Service "
      "with the ID \"{service_id}\"")
def attempt_to_retrieve_organization_service_public_key_with_service_id(
        context, service_id):
    try:
        context.organization_service_manager.retrieve_public_keys_list(
            service_id
        )
    except Exception as e:
        context.current_exception = e


@then("the Organization Service Public Keys list is empty")
def verify_organization_service_public_keys_list_is_empty(context):
    current_organization_public_keys = context.entity_manager. \
        get_current_organization_service_public_keys()
    if current_organization_public_keys:
        raise Exception("Expected public keys list to be empty but it was: %s"
                        % current_organization_public_keys)


@then("the Organization Service Public Key is in the list of Public Keys for "
      "the Organization Service")
@then("the Public Key is in the list of Public Keys for the Organization "
      "Service")
def verify_organization_service_public_key_is_in_list_of_public_keys(context):
    alpha_public_key = context.keys_manager.alpha_public_key
    current_organization_public_keys = context.entity_manager. \
        get_current_organization_service_public_keys()
    for key in current_organization_public_keys:
        if key.public_key == alpha_public_key:
            return
    raise Exception("Unable to find the current organization public key")


@then("the other Public Key is in the list of Public Keys for the "
      "Organization Service")
def verify_other_organization_service_public_key_is_in_list_of_public_keys(
        context):
    beta_public_key = context.keys_manager.beta_public_key
    current_organization_public_keys = context.entity_manager. \
        get_current_organization_service_public_keys()
    for key in current_organization_public_keys:
        if key.public_key == beta_public_key:
            return
    raise Exception("Unable to find the other organization public key")


@then("the Organization Service Public Key is inactive")
def verify_organization_service_public_key_is_inactive(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_organization_public_keys = context.entity_manager. \
        get_current_organization_service_public_keys()
    for key in current_organization_public_keys:
        if key.id == key_id:
            if not key.active:
                return
            else:
                raise Exception("Key was set to active when it was "
                                "expected as inactive")
    raise Exception("Unable to find the current organization public key")


@then("the Organization Service Public Key Expiration Date is "
      "\"{expiration_timestamp}\"")
def verify_organization_service_public_key_expiration_date(
        context, expiration_timestamp):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_organization_public_keys = context.entity_manager. \
        get_current_organization_service_public_keys()
    for key in current_organization_public_keys:
        if key.id == key_id:
            if key.expires == parse(expiration_timestamp):
                return
            else:
                print(parse(expiration_timestamp))
                raise Exception("Public key expiration date was not "
                                "what was expected: %s" % key.expires)


@then("the last current Organization Service's Public Key is not in the list")
def verify_first_public_key_is_not_in_organization_service_public_keys(
        context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_organization_public_keys = context.entity_manager. \
        get_current_organization_service_public_keys()
    for key in current_organization_public_keys:
        if key.id == key_id:
            raise Exception("Last current public key was found when it "
                            "shouldn't have been")


# Remove public key


@when("I remove the current Organization Service Public Key")
def remove_current_organization_service_public_key(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_service = context.entity_manager.get_current_organization_service()
    context.organization_service_manager.remove_public_key(
        key_id,
        current_service.id
    )


@when("I attempt to remove the current Organization Service Public Key")
def attempt_to_remove_current_organization_service_public_key(context):
    key_id = context.keys_manager.alpha_md5_fingerprint
    current_service = context.entity_manager.get_current_organization_service()
    try:
        context.organization_service_manager.remove_public_key(
            key_id,
            current_service.id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to remove a Public Key from the Organization Service with "
      "the ID \"{service_id}\"")
def attempt_to_remove_public_key_from_organization_service_from_id(context,
                                                                   service_id):
    key_id = context.keys_manager.alpha_md5_fingerprint
    try:
        context.organization_service_manager.remove_public_key(
            key_id,
            service_id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to remove a Public Key identified by \"{key_id}\" "
      "from the Organization Service")
def attempt_to_remove_organization_service_public_key_from_key_id(context,
                                                                  key_id):
    current_service = context.entity_manager.get_current_organization_service()
    try:
        context.organization_service_manager.remove_public_key(
            key_id,
            current_service.id
        )
    except Exception as e:
        context.current_exception = e


# Update public key

@when("I updated the Organization Service Public Key to inactive")
def update_dirtory_service_public_key_to_inactive(context):
    current_service = context.entity_manager.get_current_organization_service()
    key_id = context.keys_manager.alpha_md5_fingerprint
    context.organization_service_manager.update_public_key(
        key_id,
        current_service.id,
        active=False
    )


@when("I updated the Organization Service Public Key expiration date to "
      "\"{expiration_timestamp}\"")
def update_organization_service_public_key_expiration_date(
        context, expiration_timestamp):
    current_service = context.entity_manager.get_current_organization_service()
    key_id = context.keys_manager.alpha_md5_fingerprint
    context.organization_service_manager.update_public_key(
        key_id,
        current_service.id,
        expires=parse(expiration_timestamp)
    )


@when("I attempt to update a Public Key for the Organization Service with "
      "the ID \"{service_id}\"")
def attempt_to_update_organization_service_public_key_with_service_id(
        context, service_id):
    key_id = context.keys_manager.alpha_md5_fingerprint
    try:
        context.organization_service_manager.update_public_key(
            key_id,
            service_id
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to update a Public Key identified by \"{key_id}\" for "
      "the Organization Service")
def attempt_to_update_organization_service_public_key_using_key_id(
        context, key_id):
    current_service = context.entity_manager.get_current_organization_service()
    try:
        context.organization_service_manager.update_public_key(
            key_id,
            current_service.id
        )
    except Exception as e:
        context.current_exception = e
