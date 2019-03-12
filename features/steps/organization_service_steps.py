from uuid import uuid4

from behave import given, when, then


# Create Organization Service

@given("I created an Organization Service")
@when("I create an Organization Service")
def create_service(context):
    context.sent_kwargs = kwargs = {
        "name": str(uuid4())
    }
    context.organization_service_manager.create_service(**kwargs)


@given("I attempt to create a Organization Service with the same name")
def attempt_to_create_service_with_same_name(context):
    kwargs = {
        "name": context.sent_kwargs.get("name")
    }
    try:
        context.organization_service_manager.create_service(**kwargs)
    except Exception as e:
        context.current_exception = e


@when("I create a Organization Service with the following")
@given("I created a Organization Service with the following")
def create_service_with_values(context):
    kwargs = {}
    for row in context.table:
        kwargs[row['key']] = row['value']
    context.sent_kwargs = kwargs
    kwargs['name'] = str(uuid4())
    context.organization_service_manager.create_service(**kwargs)


# Get Organization Service


@when("I retrieve the created Organization Service")
def retrieve_current_service(context):
    current_service = context.entity_manager.get_current_organization_service()
    context.organization_service_manager.retrieve_service(current_service.id)


@when("I attempt to retrieve the Organization Service with the ID "
      "\"{service_id}\"")
def attempt_to_retrieve_service_from_id(context, service_id):
    try:
        context.organization_service_manager.retrieve_service(
            service_id
        )
    except Exception as e:
        context.current_exception = e


@then("the Organization Service name is the same as was sent")
def verify_organization_name_matches_send_kwargs(context):
    current_service = context.entity_manager.get_current_organization_service()
    if current_service.name != context.sent_kwargs.get("name"):
        raise Exception(
            "Expected %s as the Service name but got %s" %
            (current_service.name, context.sent_kwargs.get("name"))
        )


@then("the Organization Service description is \"{description}\"")
def verify_organization_description_matches_send_kwargs(context, description):
    current_service = context.entity_manager.get_current_organization_service()
    if current_service.description != context.sent_kwargs.get("description"):
        raise Exception(
            "Expected %s as the Service description but got %s" %
            (
                current_service.description,
                context.sent_kwargs.get("description")
            )
        )


@then("the Organization Service icon is \"{icon}\"")
def verify_organization_icon_matches_send_kwargs(context, icon):
    current_service = context.entity_manager.get_current_organization_service()
    if current_service.icon != context.sent_kwargs.get("icon"):
        raise Exception(
            "Expected %s as the Service icon but got %s" %
            (
                current_service.icon,
                context.sent_kwargs.get("icon")
            )
        )


@then("the Organization Service callback_url is \"{callback_url}\"")
def verify_organization_callback_url_matches_send_kwargs(context, callback_url):
    current_service = context.entity_manager.get_current_organization_service()
    if current_service.callback_url != context.sent_kwargs.get("callback_url"):
        raise Exception(
            "Expected %s as the Service callback_url but got %s" %
            (
                current_service.callback_url,
                context.sent_kwargs.get("callback_url")
            )
        )


@then("the Organization Service is active")
def verify_organization_service_is_active(context):
    current_service = context.entity_manager.get_current_organization_service()
    if not current_service.active:
        raise Exception("Service was not active when it was expected to be")


@then("the Organization Service is not active")
def verify_organization_service_is_not_active(context):
    current_service = context.entity_manager.get_current_organization_service()
    if current_service.active:
        raise Exception("Service was active when it was expected to not be")


# Get Organization Service List


@when("I retrieve a list of all Organization Services")
def retrieve_all_organization_services(context):
    context.organization_service_manager.retrieve_all_services()


@then("the current Organization Service is in the Services list")
def verify_current_organization_is_in_current_service_list(context):
    current_service = context.entity_manager.get_current_organization_service()
    current_service_list = context.entity_manager.\
        get_current_organization_service_list()
    for service in current_service_list:
        if service.id == current_service.id:
            return
    raise Exception("The current Service is not in the "
                    "list when it was expected")


@when("I retrieve a list of Organization Services "
      "with the created Service's ID")
def retrieve_organization_services_with_current_service_id_in_list(context):
    current_service = context.entity_manager.get_current_organization_service()
    context.organization_service_manager.retrieve_services(
        [current_service.id]
    )


@when("I attempt retrieve a list of Organization Services with the Service ID "
      "\"{service_id}\"")
def attempt_to_retrieve_organization_service_lists_from_id(context, service_id):
    try:
        context.organization_service_manager.retrieve_services(
            [service_id]
        )
    except Exception as e:
        context.current_exception = e


@then("the current Organization Service list is a list with only the current "
      "Service")
def verify_organization_service_list_is_only_current_service(context):
    current_service = context.entity_manager.get_current_organization_service()
    current_service_list = context.entity_manager. \
        get_current_organization_service_list()
    if len(current_service_list) != 1 or \
            current_service_list[0].id != current_service.id:
        raise Exception("Service list expect to just contain current "
                        "Service, but was: %s" % current_service_list)


# Update Organization Service

@when("I update the Organization Service with the following")
def update_organization_service_with_table_values(context):
    current_service = context.entity_manager.get_current_organization_service()
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
    context.organization_service_manager.update_service(
        current_service.id,
        **kwargs
    )


@when("I attempt to update the active status of the Organization Service with "
      "the ID \"{service_id}\"")
def attempt_to_update_active_status_for_organization_service(context, service_id):
    try:
        context.organization_service_manager.update_service(
            service_id,
            active=True
        )
    except Exception as e:
        context.current_exception = e
