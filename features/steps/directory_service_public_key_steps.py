from base64 import encodebytes

from behave import given, when, then

from launchkey.entities.shared import PublicKey


@when("I add a Public Key to the Directory Service")
def add_public_key_to_directory_service(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    public_key = PublicKey({
        "id": context.keys_manager.alpha_public_key,
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
        "id": context.keys_manager.alpha_public_key,
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


@when("I add another Public Key to the Directory Service")
def add_another_public_key_to_directory_service(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    public_key = PublicKey({
        "id": context.keys_manager.beta_public_key,
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


@when("I retrieve the current Directory Service's Public Keys")
def retrieve_directory_service_public_keys(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    context.directory_service_manager.retrieve_public_keys_list(
        current_directory.id,
        current_service.id
    )


@then("the Directory Service Public Key is in the list of Public Keys for the "
      "Directory Service")
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
    raise Exception("Unable to find the current directory public key")


@when("I attempt to add a Public Key to the Directory Service with the ID "
      "\"{service_id}\"")
def attempt_to_add_public_key_to_directory_service(context, service_id):
    current_directory = context.entity_manager.get_current_directory()
    public_key = PublicKey({
        "id": context.keys_manager.alpha_public_key,
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
