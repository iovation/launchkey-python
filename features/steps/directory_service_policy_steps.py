from datetime import time
from pytz import utc

from behave import given, when, then, step

from launchkey.entities.service import TimeFence, GeoFence


# Retrieve Directory Service Policy

@when("I retrieve the Policy for the Current Directory Service")
def retrieve_policy_for_current_directory_service(context):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    context.directory_service_policy_manager.retrieve_service_policy(
        current_service.id,
        current_directory.id
    )


@then("the Directory Service Policy has no requirement for inherence")
def verify_current_directory_service_policy_has_no_inherence_requirement(
        context):
    current_policy = context.entity_manager.\
        get_current_directory_service_policy()
    if "inherence" in current_policy.minimum_requirements:
        raise Exception(
            "Found inherence in current policy requirements when it "
            "should not have been: %s" % current_policy.minimum_requirements
        )


@then("the Directory Service Policy has no requirement for knowledge")
def verify_current_directory_service_policy_has_no_knowledge_requirement(
        context):
    current_policy = context.entity_manager.\
        get_current_directory_service_policy()
    if "knowledge" in current_policy.minimum_requirements:
        raise Exception(
            "Found knowledge in current policy requirements when it "
            "should not have been: %s" % current_policy.minimum_requirements
        )


@then("the Directory Service Policy has no requirement for possession")
def verify_current_directory_service_policy_has_no_possession_requirement(
        context):
    current_policy = context.entity_manager.\
        get_current_directory_service_policy()
    if "possession" in current_policy.minimum_requirements:
        raise Exception(
            "Found possession in current policy requirements when it "
            "should not have been: %s" % current_policy.minimum_requirements
        )


@then("the Directory Service Policy has no requirement for number of factors")
def verify_current_directory_service_policy_has_factor_count_requirement(
        context):
    current_policy = context.entity_manager.\
        get_current_directory_service_policy()
    if current_policy.minimum_amount is not 0:
        raise Exception(
            "Expected minimum requirement amount to be 0 but it was %s" %
            current_policy.minimum_amount
        )


@then("the Directory Service Policy requires {count:d} factors")
def verify_directory_service_policy_requires_count(context, count):
    current_policy = context.entity_manager. \
        get_current_directory_service_policy()
    if current_policy.minimum_amount is not count:
        raise Exception(
            "Expected minimum requirement amount to be %s but it was %s" %
            (count, current_policy.minimum_amount)
        )


@when("I attempt to retrieve the Policy for the Directory Service with the ID "
      "\"{service_id}\"")
def attempt_to_retrieve_policy_for_given_directory_service_id(context,
                                                              service_id):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_service_policy_manager.retrieve_service_policy(
            service_id,
            current_directory.id
        )
    except Exception as e:
        context.current_exception = e


# Set Directory Service Policy

@given("the Directory Service Policy is set to require {count:d} factor")
@step("the Directory Service Policy is set to require {count:d} factors")
def set_current_directory_policy_require_count(context, count):
    current_service = context.entity_manager.get_current_directory_service()
    current_directory = context.entity_manager.get_current_directory()
    context.directory_service_policy_manager.retrieve_service_policy(
        current_service.id,
        current_directory.id
    )
    policy = context.entity_manager.get_current_directory_service_policy()
    policy.set_minimum_requirements(minimum_amount=count)
    context.entity_manager.set_current_directory_service_policy(policy)


def set_current_directory_policy_require_type(context, policy_type):
    policy = context.entity_manager.get_current_directory_service_policy()
    kwargs = {}

    # Make sure the previously set requirements remain
    for additional_policy_type in policy.minimum_requirements:
        kwargs[additional_policy_type] = True

    kwargs[policy_type] = True

    try:
        policy.set_minimum_requirements(**kwargs)
    except TypeError:
        raise Exception("Invalid policy input %s" % policy_type)
    context.entity_manager.set_current_directory_service_policy(policy)


@given("the Directory Service Policy is set to require knowledge")
def set_current_directory_policy_require_type_knowledge(context):
    set_current_directory_policy_require_type(context, "knowledge")


@given("the Directory Service Policy is set to require inherence")
def set_current_directory_policy_require_type_inherence(context):
    set_current_directory_policy_require_type(context, "inherence")


@given("the Directory Service Policy is set to require possession")
def set_current_directory_policy_require_type_possession(context):
    set_current_directory_policy_require_type(context, "possession")


@given("the Directory Service Policy is set to require jail break protection")
def set_directory_policy_required_jailbreak_protection(context):
    policy = context.entity_manager.get_current_directory_service_policy()
    policy.require_jailbreak_protection(True)


def verify_directory_service_policy_requires_type(context, policy_type):
    policy = context.entity_manager.get_current_directory_service_policy()
    if policy_type.lower() not in policy.minimum_requirements:
        raise Exception("%s not in the requested Service policies, %s" %
                        (policy_type, policy.minimum_requirements))


@then("the Directory Service Policy does require knowledge")
def verify_directory_service_policy_requires_type_knowledge(context):
    verify_directory_service_policy_requires_type(context, "knowledge")


@then("the Directory Service Policy does require inherence")
def verify_directory_service_policy_requires_type_inherence(context):
    verify_directory_service_policy_requires_type(context, "inherence")


@then("the Directory Service Policy does require possession")
def verify_directory_service_policy_requires_type_possession(context):
    verify_directory_service_policy_requires_type(context, "possession")


@then("the Directory Service Policy does require jail break protection")
def verify_directory_service_policy_requires_jailbreak_protection(context):
    policy = context.entity_manager.get_current_directory_service_policy()
    if policy.jailbreak_protection is False:
        raise Exception("Policy did not required jailbreak protection when "
                        "it should")


@given("I set the Policy for the Directory Service")
@given("I set the Policy for the Current Directory Service")
@when("I set the Policy for the Current Directory Service")
def set_directory_service_policy_require_to_current_policy(context):
    current_directory = context.entity_manager.get_current_directory()
    current_service = context.entity_manager.get_current_directory_service()
    policy = context.entity_manager.get_current_directory_service_policy()
    context.directory_service_policy_manager.set_service_policy(
        current_service.id,
        current_directory.id,
        policy
    )


@given("the Directory Service Policy is set to have the following Time Fences")
def set_directory_service_policy_time_fences_from_table(context):
    policy = context.entity_manager.get_current_directory_service_policy()
    for row in context.table:
        days = {}
        for day in row['Days'].split(","):
            days[day.lower()] = True
        policy.add_timefence(
            row['Name'],
            time(hour=int(row['Start Hour']), minute=int(row['Start Minute'])),
            time(hour=int(row['End Hour']), minute=int(row['End Minute'])),
            **days
        )
    context.entity_manager.set_current_directory_service_policy(policy)


@then("the Directory Service Policy has the following Time Fences")
def verify_directory_service_policy_time_fences_from_table(context):
    policy = context.entity_manager.get_current_directory_service_policy()
    for row in context.table:
        days = {}
        for day in row['Days'].split(","):
            days[day.lower()] = True

        timefence = TimeFence(
            row['Name'],
            time(hour=int(row['Start Hour']), minute=int(row['Start Minute']),
                 tzinfo=utc),
            time(hour=int(row['End Hour']), minute=int(row['End Minute']),
                 tzinfo=utc),
            **days
        )
        if timefence not in policy.timefences:
            raise Exception("%s not in policy timefences: %s" %
                            (timefence, policy.timefences))


@given("the Directory Service Policy is set to have the following "
       "Geofence locations")
def set_directory_service_policy_geo_fences_from_table(context):
    policy = context.entity_manager.get_current_directory_service_policy()
    for row in context.table:
        policy.add_geofence(
            row['Latitude'],
            row['Longitude'],
            row['Radius'],
            name=row['Name']
        )
    context.entity_manager.set_current_directory_service_policy(policy)


@then("the Directory Service Policy has {count:d} locations")
def verify_directory_service_policy_has_count_locations(context, count):
    policy = context.entity_manager.get_current_directory_service_policy()
    for row in context.table:
        geofence = GeoFence(
            row['Latitude'],
            row['Longitude'],
            row['Radius'],
            row['Name']
        )
        if geofence not in policy.geofences:
            raise Exception("%s not in policy geofences: %s" %
                            (geofence, policy.geofences))


@when("I attempt to set the Policy for the Directory Service with the ID "
      "\"{service_id}\"")
def attempt_to_set_policy_for_directory_service_from_id(context, service_id):
    current_directory = context.entity_manager.get_current_directory()
    policy = context.entity_manager.get_current_directory_service_policy()
    try:
        context.directory_service_policy_manager.set_service_policy(
            service_id,
            current_directory.id,
            policy
        )
    except Exception as e:
        context.current_exception = e


# Remove Directory Service Policy

@when("I remove the Policy for the Directory Service")
def remove_policy_for_current_directory_service(context):
    current_directory = context.entity_manager.get_current_directory()
    current_service = context.entity_manager.get_current_directory_service()
    context.directory_service_policy_manager.remove_service_policy(
        current_service.id,
        current_directory.id
    )


@when("I attempt to remove the Policy for the Directory Service with the ID "
      "\"{service_id}\"")
def attempt_to_remove_policy_from_given_directory_service_id(context,
                                                             service_id):
    current_directory = context.entity_manager.get_current_directory()
    try:
        context.directory_service_policy_manager.remove_service_policy(
            service_id,
            current_directory.id
        )
    except Exception as e:
        context.current_exception = e
