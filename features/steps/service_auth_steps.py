from behave import given, when, then

from launchkey.entities.service import GeoFence, AuthMethod, AuthMethodType

# Auth Creation


@given("I made an Authorization request")
@when("I make an Authorization request")
def make_auth_for_current_user_identifier(context):
    current_service = context.entity_manager.get_current_directory_service()
    user_identifier = context.entity_manager.get_current_user_identifier()
    context.directory_service_auths_manager.create_auth_request(
        current_service.id,
        user_identifier
    )


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

@when("I get the response for the Authorization request")
def retrieve_current_auth_request(context):
    auth_request_id = context.entity_manager.get_current_auth_request_id()
    current_service = context.entity_manager.get_current_directory_service()
    context.directory_service_auths_manager.get_auth_response(
        current_service.id, auth_request_id
    )


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


@then("the Authorization response should be approved")
def verify_current_auth_response_is_none(context):
    current_auth = context.entity_manager.get_current_auth_response()
    if not current_auth:
        raise Exception("Auth response was found when it was expected")
    if current_auth.authorized is not True:
        raise Exception("Auth was not approved when it should have been: %s" %
                        current_auth)


@then("the Authorization response should be denied")
def verify_current_auth_response_is_none(context):
    current_auth = context.entity_manager.get_current_auth_response()
    if not current_auth:
        raise Exception("Auth response was found when it was expected")
    if current_auth.authorized is not False:
        raise Exception("Auth was approved when it should not have been: %s" %
                        current_auth)


@then("the Authorization response should require {count:d} factors")
def verify_current_auth_response_requires_count_factors(context, count):
    current_auth = context.entity_manager.get_current_auth_response()
    if current_auth.auth_policy.minimum_amount is not count:
        raise Exception("Device response policy did not require %s factors: "
                        "%s" % (count, current_auth.auth_policy))


@then("the Authorization response should contain a geofence with a radius of "
      "{radius:f}, a latitude of {latitude:f}, and a longitude of "
      "{longitude:f}")
def verify_current_auth_response_requires_geofence(context, radius,
                                                   latitude, longitude):
    current_auth = context.entity_manager.get_current_auth_response()

    geofence = GeoFence(
        latitude,
        longitude,
        radius,
        None
    )

    if geofence not in current_auth.auth_policy.geofences:
        raise Exception("%s not in policy geofences: %s" %
                        (geofence, current_auth.auth_policy.geofences))


@then("the Authorization response should contain a geofence with a radius of "
      "{radius:f}, a latitude of {latitude:f}, a longitude of {longitude:f}, "
      "and a name of \"{name}\"")
def verify_current_auth_response_requires_geofence(context, radius,
                                                   latitude, longitude, name):
    current_auth = context.entity_manager.get_current_auth_response()

    geofence = GeoFence(
        latitude,
        longitude,
        radius,
        name
    )

    if geofence not in current_auth.auth_policy.geofences:
        raise Exception("%s not in policy geofences: %s" %
                        (geofence, current_auth.auth_policy.geofences))


def verify_auth_response_policy_requires_type(context, policy_type):
    policy = context.entity_manager.get_current_auth_response().auth_policy
    if policy_type.lower() not in policy.minimum_requirements:
        raise Exception("%s not in the requested Auth policies, %s" %
                        (policy_type, policy.minimum_requirements))


def verify_auth_response_policy_does_not_require_type(context, policy_type):
    policy = context.entity_manager.get_current_auth_response().auth_policy
    if policy_type.lower() in policy.minimum_requirements:
        raise Exception("%s in the requested Auth policies, %s" %
                        (policy_type, policy.minimum_requirements))


@then("the Authorization response should require knowledge")
def verify_auth_response_policy_requires_type_knowledge(context):
    verify_auth_response_policy_requires_type(context, "knowledge")


@then("the Authorization response should not require knowledge")
def verify_auth_response_policy_does_not_require_type_knowledge(context):
    verify_auth_response_policy_does_not_require_type(context, "knowledge")


@then("the Authorization response should require inherence")
def verify_auth_response_policy_requires_type_inherence(context):
    verify_auth_response_policy_requires_type(context, "inherence")


@then("the Authorization response should not require inherence")
def verify_auth_response_policy_does_not_require_type_inherence(context):
    verify_auth_response_policy_does_not_require_type(context, "inherence")


@then("the Authorization response should require possession")
def verify_auth_response_policy_requires_type_possession(context):
    verify_auth_response_policy_requires_type(context, "possession")


@then("the Authorization response should not require possession")
def verify_auth_response_policy_does_not_require_type_possession(context):
    verify_auth_response_policy_does_not_require_type(context, "possession")


@then("the Authorization response should contain the following methods")
def set_directory_service_policy_time_fences_from_table(context):
    def parse_input(value):
        if value.upper() == "TRUE":
            value = True
        elif value.upper() == "FALSE":
            value = False
        elif value.upper() == "NULL":
            value = None
        return value

    methods = context.entity_manager.get_current_auth_response().auth_methods
    for i, method in enumerate(context.table):
        expected_method = AuthMethod(
            AuthMethodType(method['Method'].upper()),
            parse_input(method['Set']),
            parse_input(method['Active']),
            parse_input(method['Allowed']),
            parse_input(method['Supported']),
            parse_input(method['User Required']),
            parse_input(method['Passed']),
            parse_input(method['Error'])
        )
        if methods[i] != expected_method:
            if expected_method.method in \
                    [AuthMethodType.FINGERPRINT, AuthMethodType.FACE] and \
                    expected_method.supported != methods[i].supported:
                raise Exception(
                    "Expected %s but got %s. Be aware that %s "
                    "is not supported on all devices, so this may fail." %
                    (expected_method, methods[i], expected_method.method))
            else:
                raise Exception("Expected %s but got %s" % (expected_method, methods[i]))
