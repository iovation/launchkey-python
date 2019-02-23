from behave import given, when, then, step


# Auth Creation

@when("I attempt to make an Authorization request")
def attempt_to_make_auth_for_current_user_identifier(context):
    current_service = context.entity_manager.get_current_directory_service()
    user_identifier = context.entity_manager.get_current_user_identifier()
    try:
        context.directory_service_auths_manager.create_auth_request(
            current_service.id,
            user_identifier
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to make an Authorization request for the User identified by "
      "\"{user_identifier}\"")
def attempt_to_make_auth_request_for_given_user_identifier(context,
                                                           user_identifier):
    current_service = context.entity_manager.get_current_directory_service()
    try:
        context.directory_service_auths_manager.create_auth_request(
            current_service.id,
            user_identifier
        )
    except Exception as e:
        context.current_exception = e


@when("I attempt to make an Authorization request with the context value "
      "\"{context_value}\"")
def attempt_to_create_auth_request_with_given_context(context, context_value):
    current_service = context.entity_manager.get_current_directory_service()
    user_identifier = context.entity_manager.get_current_user_identifier()
    try:
        context.directory_service_auths_manager.create_auth_request(
            current_service.id,
            user_identifier,
            context=context_value
        )
    except Exception as e:
        context.current_exception = e


# Auth Get

@when("I get the response for Authorization request \"{auth_id}\"")
def retrieve_auth_request_by_id(context, auth_id):
    current_service = context.entity_manager.get_current_directory_service()
    context.directory_service_auths_manager.get_auth_response(
        current_service.id, auth_id
    )


@then("the Authorization response is not returned")
def verify_current_auth_response_is_none(context):
    current_auth = context.entity_manager.get_current_auth_response()
    if current_auth:
        raise Exception("Auth response was found when it was not expected")

