from uuid import uuid4

from behave import given, when, then


# Delete session
@when("I delete the Sessions for the current User")
def delete_session_for_current_user(context):
    current_directory = context.entity_manager.get_current_directory()
    user_identifier = context.entity_manager.get_current_user_identifier()
    context.directory_session_manager.end_all_sessions_for_user(
        user_identifier,
        current_directory.id,
    )


@when("I attempt to delete the Sessions for the User \"{user_identifier}\"")
def attempt_to_delete_session_for_given_user(context, user_identifier):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_session_manager.end_all_sessions_for_user(
            user_identifier,
            current_directory.id,
        )
    except Exception as e:
        context.current_exception = e


# Retrieve session
@when("I retrieve the Session list for the current User")
def retrieve_session_for_current_user(context):
    current_directory = context.entity_manager.get_current_directory()
    user_identifier = context.entity_manager.get_current_user_identifier()
    context.directory_session_manager.retrieve_session_list_for_user(
        user_identifier,
        current_directory.id,
    )


@when("I attempt to retrieve the Session list for the User "
      "\"{user_identifier}\"")
def attempt_to_retrieve_session_list_for_user_identifier(context,
                                                         user_identifier):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_session_manager.retrieve_session_list_for_user(
            user_identifier,
            current_directory.id,
        )
    except Exception as e:
        context.current_exception = e


@then("the Service User Session List has {count:d} Sessions")
def verify_service_user_session_has_count_sessions(context, count):
    sessions_list = context.entity_manager.\
        get_current_directory_user_sessions()
    if len(sessions_list) != count:
        raise Exception("Session list length was %s when it was "
                        "expected to be %s" % len(sessions_list, count))
