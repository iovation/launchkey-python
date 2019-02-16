from uuid import uuid4

from behave import given, when, then


# Create Directory Service

@given("I created a Directory Service")
def create_service(context):
    current_directory = context.entity_manager.get_current_directory()
    context.sent_kwargs = kwargs = {
        "name": str(uuid4())
    }
    context.directory_service_manager.create_service(
        current_directory.id, **kwargs)


@given("I attempt to create a Directory Service with the same name")
def attempt_to_create_service_with_same_name(context):
    current_directory = context.entity_manager.get_current_directory()
    kwargs = {
        "name": context.sent_kwargs.get("name")
    }
    try:
        context.directory_service_manager.create_service(current_directory.id,
                                                         **kwargs)
    except Exception as e:
        context.current_exception = e


@when("I create a Directory Service with the following")
@given("I created a Directory Service with the following")
def create_service_with_values(context):
    current_directory = context.entity_manager.get_current_directory()
    kwargs = {}
    for row in context.table:
        kwargs[row['key']] = row['value']
    context.sent_kwargs = kwargs
    kwargs['name'] = str(uuid4())
    context.directory_service_manager.create_service(current_directory.id,
                                                     **kwargs)


# Get Directory Service


@when("I retrieve the created Directory Service")
def retrieve_current_service(context):
    current_directory = context.entity_manager.get_current_directory()
    current_service = context.entity_manager.get_current_directory_service()
    context.directory_service_manager.retrieve_service(current_directory.id,
                                                       current_service.id)


@when("I attempt to retrieve the Directory Service with the ID "
      "\"{service_id}\"")
def attempt_to_retrieve_service_from_id(context, service_id):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_service_manager.retrieve_service(
            current_directory.id,
            service_id
        )
    except Exception as e:
        context.current_exception = e


@then("the Directory Service name is the same as was sent")
def verify_directory_name_matches_send_kwargs(context):
    current_service = context.entity_manager.get_current_directory_service()
    if current_service.name != context.sent_kwargs.get("name"):
        raise Exception(
            "Expected %s as the Service name but got %s" %
            (current_service.name, context.sent_kwargs.get("name"))
        )


@then("the Directory Service description is \"{description}\"")
def verify_directory_description_matches_send_kwargs(context, description):
    current_service = context.entity_manager.get_current_directory_service()
    if current_service.description != context.sent_kwargs.get("description"):
        raise Exception(
            "Expected %s as the Service description but got %s" %
            (
                current_service.description,
                context.sent_kwargs.get("description")
            )
        )


@then("the Directory Service icon is \"{icon}\"")
def verify_directory_icon_matches_send_kwargs(context, icon):
    current_service = context.entity_manager.get_current_directory_service()
    if current_service.icon != context.sent_kwargs.get("icon"):
        raise Exception(
            "Expected %s as the Service icon but got %s" %
            (
                current_service.icon,
                context.sent_kwargs.get("icon")
            )
        )


@then("the Directory Service callback_url is \"{callback_url}\"")
def verify_directory_callback_url_matches_send_kwargs(context, callback_url):
    current_service = context.entity_manager.get_current_directory_service()
    if current_service.callback_url != context.sent_kwargs.get("callback_url"):
        raise Exception(
            "Expected %s as the Service callback_url but got %s" %
            (
                current_service.callback_url,
                context.sent_kwargs.get("callback_url")
            )
        )


@then("the Directory Service is active")
def verify_directory_service_is_active(context):
    current_service = context.entity_manager.get_current_directory_service()
    if not current_service.active:
        raise Exception("Service was not active when it was expected to be")


@then("the Directory Service is not active")
def verify_directory_service_is_not_active(context):
    current_service = context.entity_manager.get_current_directory_service()
    if current_service.active:
        raise Exception("Service was active when it was expected to not be")


# Get Directory Service List


@when("I retrieve a list of all Directory Services")
def retrieve_all_directory_services(context):
    current_directory = context.entity_manager.get_current_directory()
    context.directory_service_manager.retrieve_all_services(
        current_directory.id)


@then("the current Directory Service is in the Services list")
def verify_current_directory_is_in_current_service_list(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_service_list = context.entity_manager.\
        get_current_directory_service_list()
    for service in current_service_list:
        if service.id == current_service.id:
            return
    raise Exception("The current Service is not in the "
                    "list when it was expected")


@then("the current Directory Service list is an empty list")
def verify_current_directory_service_list_is_empty(context):
    current_service_list = context.entity_manager.\
        get_current_directory_service_list()
    if current_service_list != []:
        raise Exception("Service list expected to be empty but it was: %s" %
                        current_service_list)


@when("I retrieve a list of Directory Services with the created Service's ID")
def retrieve_directory_services_with_current_service_id_in_list(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    context.directory_service_manager.retrieve_services(
        current_directory.id,
        [current_service.id]
    )


@when("I attempt retrieve a list of Directory Services with the Service ID "
      "\"{service_id}\"")
def attempt_to_retrieve_direftory_service_lists_from_id(context, service_id):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_service_manager.retrieve_services(
            current_directory.id,
            [service_id]
        )
    except Exception as e:
        context.current_exception = e


@then("the current Directory Service list is a list with only the current "
      "Service")
def verify_directory_service_list_is_only_current_service(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_service_list = context.entity_manager. \
        get_current_directory_service_list()
    if len(current_service_list) != 1 or \
            current_service_list[0].id != current_service.id:
        raise Exception("Service list expect to just contain current "
                        "Service, but was: %s" % current_service_list)


# Update Directory Service

@when("I update the Directory Service with the following")
def update_directory_service_with_table_values(context):
    current_directory = context.entity_manager.get_current_directory()
    current_service = context.entity_manager.get_current_directory_service()
    kwargs = {}
    for row in context.table:
        if row['value'] == "True":
            kwargs[row['key']] = True
        elif row['value'] == "False":
            kwargs[row['key']] = False
        else:
            kwargs[row['key']] = row['value']
    context.sent_kwargs = kwargs
    kwargs['name'] = str(uuid4())
    context.directory_service_manager.update_service(
        current_directory.id,
        current_service.id,
        **kwargs
    )


@when("I attempt to update the active status of the Directory Service with "
      "the ID \"{service_id}\"")
def attempt_to_update_active_status_for_directory_service(context, service_id):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_service_manager.update_service(
            current_directory.id,
            service_id,
            active=True
        )
    except Exception as e:
        context.current_exception = e
