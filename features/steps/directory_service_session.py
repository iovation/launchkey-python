from behave import given, when, then

# Session Start


@given("I sent a Session Start request")
@when("I send a Session Start request with no Auth Request ID")
def send_service_session_end_request(context):
    current_service = context.entity_manager.get_current_directory_service()
    user_identifier = context.entity_manager.get_current_user_identifier()
    context.directory_service_session_manager.start_session(
        current_service.id,
        user_identifier
    )


@when("I send a Session Start request with Auth Request ID \"{auth_id}\"")
def send_service_session_end_request(context, auth_id):
    current_service = context.entity_manager.get_current_directory_service()
    user_identifier = context.entity_manager.get_current_user_identifier()
    context.directory_service_session_manager.start_session(
        current_service.id,
        user_identifier,
        auth_id
    )


@when("I attempt to send a Session Start request for user "
      "\"{user_identifier}\"")
def attempt_to_send_session_start_request_with_user_identifier(
        context, user_identifier):
    current_service = context.entity_manager.get_current_directory_service()
    try:
        context.directory_service_session_manager.start_session(
            current_service.id,
            user_identifier
        )
    except Exception as e:
        context.current_exception = e


# Session End


@when("I send a Session End request")
def send_service_session_end_request(context):
    current_service = context.entity_manager.get_current_directory_service()
    user_identifier = context.entity_manager.get_current_user_identifier()
    context.directory_service_session_manager.end_session(
        current_service.id,
        user_identifier
    )


@when("I attempt to send a Session End request for user \"{user_identifier}\"")
def attempt_to_send_session_end_request_with_user_identifier(context,
                                                             user_identifier):
    current_service = context.entity_manager.get_current_directory_service()
    try:
        context.directory_service_session_manager.end_session(
            current_service.id,
            user_identifier
        )
    except Exception as e:
        context.current_exception = e
