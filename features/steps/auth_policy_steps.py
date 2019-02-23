from behave import given, when, then, step
from uuid import uuid4

from launchkey.entities.service import GeoFence


@given("the current Authorization Policy requires {count:d} factors")
def update_current_auth_policy_to_require_count_factors(context, count):
    current_auth = context.entity_manager.get_current_auth_policy()
    current_auth.set_minimum_requirements(minimum_amount=count)


@given("the current Authorization Policy requires inherence")
def update_current_auth_policy_to_require_inherence(context):
    current_auth = context.entity_manager.get_current_auth_policy()
    current_auth.set_minimum_requirements(inherence=True)


@given("the current Authorization Policy requires possession")
def update_current_auth_policy_to_require_possession(context):
    current_auth = context.entity_manager.get_current_auth_policy()
    current_auth.set_minimum_requirements(possession=True)


@given("the current Authorization Policy requires knowledge")
def update_current_auth_policy_to_require_knowledge(context):
    current_auth = context.entity_manager.get_current_auth_policy()
    current_auth.set_minimum_requirements(knowledge=True)


@when("I attempt to make an Policy based Authorization request for the User "
      "identified by \"{user_identifier}\"")
def attempt_to_make_policy_auth_with_directory_service\
                (context, user_identifier):
    current_service = context.entity_manager.get_current_directory_service()
    user_identifier = context.entity_manager.get_current_user_identifier()
    policy = context.entity_manager.get_current_auth_policy()
    try:
        context.directory_service_auths_manager.create_auth_request(
            current_service.id,
            user_identifier,
            policy=policy
        )
    except Exception as e:
        context.current_exception = e


@given("the current Authorization Policy requires a geofence with a radius "
       "of {radius:f}, a latitude of {latitude:f}, and a longitude of "
       "{longitude:f}")
def update_current_auth_policy_to_require_given_geofence(context, radius,
                                                         latitude, longitude):
    current_auth = context.entity_manager.get_current_auth_policy()
    current_auth.add_geofence(latitude, longitude, radius)
