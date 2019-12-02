from datetime import time
from pytz import utc

from behave import given, when, then, step

from launchkey.entities.service import TimeFence, GeoFence
from launchkey.entities.service.policy import FactorsPolicy


# Retrieve Organization Service Policy
from launchkey.entities.service.policy import ConditionalGeoFencePolicy, \
    TerritoryFence, GeoCircleFence


@step("I retrieve the Policy for the Current Organization Service")
def retrieve_policy_for_current_organization_service(context):
    current_service = context.entity_manager.get_current_organization_service()
    context.organization_service_policy_manager.retrieve_service_policy(
        current_service.id
    )


@step("I retrieve the Advanced Policy for the Current Organization Service")
def retrieve_policy_for_current_organization_service(context):
    current_service = context.entity_manager.get_current_organization_service()
    context.organization_service_policy_manager \
        .retrieve_advanced_service_policy(current_service.id)


@then("the Organization Service Policy has no requirement for inherence")
def verify_current_organization_service_policy_has_no_inherence_requirement(
        context):
    current_policy = context.entity_manager.\
        get_current_organization_service_policy()
    if "inherence" in current_policy.minimum_requirements:
        raise Exception(
            "Found inherence in current policy requirements when it "
            "should not have been: %s" % current_policy.minimum_requirements
        )


@then("the Organization Service Policy has no requirement for knowledge")
def verify_current_organization_service_policy_has_no_knowledge_requirement(
        context):
    current_policy = context.entity_manager.\
        get_current_organization_service_policy()
    if "knowledge" in current_policy.minimum_requirements:
        raise Exception(
            "Found knowledge in current policy requirements when it "
            "should not have been: %s" % current_policy.minimum_requirements
        )


@then("the Organization Service Policy has no requirement for possession")
def verify_current_organization_service_policy_has_no_possession_requirement(
        context):
    current_policy = context.entity_manager.\
        get_current_organization_service_policy()
    if "possession" in current_policy.minimum_requirements:
        raise Exception(
            "Found possession in current policy requirements when it "
            "should not have been: %s" % current_policy.minimum_requirements
        )


@then("the Organization Service Policy has no requirement for number of "
      "factors")
def verify_current_organization_service_policy_has_factor_count_requirement(
        context):
    current_policy = context.entity_manager.\
        get_current_organization_service_policy()
    if current_policy.minimum_amount is not 0:
        raise Exception(
            "Expected minimum requirement amount to be 0 but it was %s" %
            current_policy.minimum_amount
        )


@then("the Organization Service Policy requires {count:d} factors")
def verify_organization_service_policy_requires_count(context, count):
    current_policy = context.entity_manager. \
        get_current_organization_service_policy()
    if current_policy.minimum_amount is not count:
        raise Exception(
            "Expected minimum requirement amount to be %s but it was %s" %
            (count, current_policy.minimum_amount)
        )


@when("I attempt to retrieve the Policy for the Organization Service with "
      "the ID \"{service_id}\"")
def attempt_to_retrieve_policy_for_given_organization_service_id(context,
                                                                 service_id):
    try:
        context.organization_service_policy_manager.retrieve_service_policy(
            service_id
        )
    except Exception as e:
        context.current_exception = e


# Set Organization Service Policy

@given("the Organization Service Policy is set to require {count:d} factor")
@step("the Organization Service Policy is set to require {count:d} factors")
def set_current_organization_policy_require_count(context, count):
    current_service = context.entity_manager.get_current_organization_service()
    context.organization_service_policy_manager.retrieve_service_policy(
        current_service.id
    )
    policy = context.entity_manager.get_current_organization_service_policy()
    policy.set_minimum_requirements(minimum_amount=count)
    context.entity_manager.set_current_organization_service_policy(policy)


def set_current_organization_policy_require_type(context, policy_type):
    policy = context.entity_manager.get_current_organization_service_policy()
    kwargs = {}

    # Make sure the previously set requirements remain
    for additional_policy_type in policy.minimum_requirements:
        kwargs[additional_policy_type] = True

    kwargs[policy_type] = True

    try:
        policy.set_minimum_requirements(**kwargs)
    except TypeError:
        raise Exception("Invalid policy input %s" % policy_type)
    context.entity_manager.set_current_organization_service_policy(policy)


@when("the Organization Service Policy is set to require knowledge")
@given("the Organization Service Policy is set to require knowledge")
def set_current_organization_policy_require_type_knowledge(context):
    set_current_organization_policy_require_type(context, "knowledge")


@when("the Organization Service Policy is set to require inherence")
@given("the Organization Service Policy is set to require inherence")
def set_current_organization_policy_require_type_inherence(context):
    set_current_organization_policy_require_type(context, "inherence")


@when("the Organization Service Policy is set to require possession")
@given("the Organization Service Policy is set to require possession")
def set_current_organization_policy_require_type_possession(context):
    set_current_organization_policy_require_type(context, "possession")


@step("the Organization Service Policy is set to require jail "
      "break protection")
def set_organization_policy_required_jailbreak_protection(context):
    policy = context.entity_manager.get_current_organization_service_policy()
    policy.require_jailbreak_protection(True)


def verify_organization_service_policy_requires_type(context, policy_type):
    policy = context.entity_manager.get_current_organization_service_policy()
    if policy_type.lower() not in policy.minimum_requirements:
        raise Exception("%s not in the requested Service policies, %s" %
                        (policy_type, policy.minimum_requirements))


@then("the Organization Service Policy does require knowledge")
def verify_organization_service_policy_requires_type_knowledge(context):
    verify_organization_service_policy_requires_type(context, "knowledge")


@then("the Organization Service Policy does require inherence")
def verify_organization_service_policy_requires_type_inherence(context):
    verify_organization_service_policy_requires_type(context, "inherence")


@then("the Organization Service Policy does require possession")
def verify_organization_service_policy_requires_type_possession(context):
    verify_organization_service_policy_requires_type(context, "possession")


@then("the Organization Service Policy does require jail break protection")
def verify_organization_service_policy_requires_jailbreak_protection(context):
    policy = context.entity_manager.get_current_organization_service_policy()
    if policy.jailbreak_protection is False:
        raise Exception("Policy did not required jailbreak protection when "
                        "it should")


@then("the Organization Service Policy has no requirement for jail break "
      "protection")
def verify_organization_service_policy_does_not_require_jailbreak_protection(
        context):
    policy = context.entity_manager.get_current_organization_service_policy()
    if policy.jailbreak_protection is True:
        raise Exception("Policy ailbreak protection when it should not have")


@given(u"I set the Policy for the Organization Service")
@step(u"I set the Policy for the Current Organization Service")
def set_organization_service_policy_require_to_current_policy(context):
    current_service = context.entity_manager.get_current_organization_service()
    policy = context.entity_manager.get_current_organization_service_policy()
    context.organization_service_policy_manager.set_service_policy(
        current_service.id,
        policy
    )


@when("the Organization Service Policy is set to have the following "
      "Time Fences")
@given("the Organization Service Policy is set to have the following "
       "Time Fences")
def set_organization_service_policy_time_fences_from_table(context):
    policy = context.entity_manager.get_current_organization_service_policy()
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
    context.entity_manager.set_current_organization_service_policy(policy)


@then("the Organization Service Policy has the following Time Fences")
def verify_organization_service_policy_time_fences_from_table(context):
    policy = context.entity_manager.get_current_organization_service_policy()
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


@when("the Organization Service Policy is set to have the following Geofence "
      "locations")
@given("the Organization Service Policy is set to have the following "
       "Geofence locations")
def set_organization_service_policy_geo_fences_from_table(context):
    policy = context.entity_manager.get_current_organization_service_policy()
    for row in context.table:
        policy.add_geofence(
            row['Latitude'],
            row['Longitude'],
            row['Radius'],
            name=row['Name']
        )
    context.entity_manager.set_current_organization_service_policy(policy)


@then("the Organization Service Policy has the following Geofence locations")
def verify_organization_service_geofence_locations_from_table(context):
    policy = context.entity_manager.get_current_organization_service_policy()
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


@then("the Organization Service Policy has {count:d} locations")
def verify_organization_service_policy_has_count_locations(context, count):
    policy = context.entity_manager.get_current_organization_service_policy()
    found_locations = len(policy.geofences)
    if found_locations != count:
        raise Exception("Found %s locations when it should have been %s: %s" %
                        (found_locations, count, policy.geofences))


@then("the Organization Service Policy has {count:d} time fences")
def verify_organization_service_policy_has_count_timefences(context, count):
    policy = context.entity_manager.get_current_organization_service_policy()
    found_locations = len(policy.timefences)
    if found_locations != count:
        raise Exception("Found %s timefences when it should have been %s: %s" %
                        (found_locations, count, policy.timefences))


@when("I attempt to set the Policy for the Organization Service with the ID "
      "\"{service_id}\"")
def attempt_to_set_policy_for_organization_service_from_id(context,
                                                           service_id):
    policy = context.entity_manager.get_current_organization_service_policy()
    try:
        context.organization_service_policy_manager.set_service_policy(
            service_id,
            policy
        )
    except Exception as e:
        context.current_exception = e


# Remove Organization Service Policy

@when("I remove the Policy for the Organization Service")
def remove_policy_for_current_organization_service(context):
    current_service = context.entity_manager.get_current_organization_service()
    context.organization_service_policy_manager.remove_service_policy(
        current_service.id
    )


@when("I attempt to remove the Policy for the Organization Service with "
      "the ID \"{service_id}\"")
def attempt_to_remove_policy_from_given_organization_service_id(context,
                                                                service_id):
    try:
        context.organization_service_policy_manager.remove_service_policy(
            service_id
        )
    except Exception as e:
        context.current_exception = e


@step("I set the Policy for the Current Organization Service "
      "to the new policy")
def step_impl(context):
    current_service = context.entity_manager.get_current_organization_service()
    policy = context.entity_manager.get_current_auth_policy()
    context.organization_service_policy_manager.set_service_policy(
        current_service.id,
        policy
    )


@step("I set the Advanced Policy for the Current Organization Service "
      "to the new policy")
def step_impl(context):
    current_service = context.entity_manager.get_current_organization_service()
    policy = context.entity_manager.get_current_auth_policy()
    context.organization_service_policy_manager.set_advanced_service_policy(
        current_service.id,
        policy
    )


@given("the Organization Service is set to any Conditional Geofence Policy")
def step_impl(context):

    default_nested_policy = FactorsPolicy(
        knowledge_required=True,
        deny_emulator_simulator=None,
        deny_rooted_jailbroken=None,
        fences=None
    )

    default_cond_geo_policy = ConditionalGeoFencePolicy(
        inside=default_nested_policy,
        outside=default_nested_policy,
        fences=[TerritoryFence("US", name="test1")]
    )

    context.entity_manager.set_current_organization_service_policy(
        default_cond_geo_policy)
    context.entity_manager.set_current_auth_policy(default_cond_geo_policy)


@then(
    'the Organization Service Policy contains the GeoCircleFence "{name}"')
def step_impl(context, name):
    policy = context.entity_manager.get_current_organization_service_policy()
    for fence in policy.fences:
        if fence.name == name:
            if isinstance(fence, GeoCircleFence):
                return True
    raise ValueError("Fence {0} was not found".format(name))


@step('the Organization Service Policy contains the TerritoryFence "{name}"')
def step_impl(context, name):
    policy = context.entity_manager.get_current_organization_service_policy()
    for fence in policy.fences:
        if fence.name == name:
            if isinstance(fence, TerritoryFence):
                return True
    raise ValueError("Fence {0} was not found".format(name))


@then(u'the Organization Service Policy has "{amount}" fences')
def organization_service_amount_fences(context, amount):
    policy = context.entity_manager.get_current_organization_service_policy()
    if len(policy.fences) != int(amount):
        raise ValueError(
            "{0} does not equal current policy amount of {1}".format(
                amount,
                len(policy.fences)
            )
        )


@then(u'the Organization Service Policy has "{amount}" fence')
def single_fence(context, amount):
    # Handles the english phrasing for a single fence without
    # changing the behave matcher
    organization_service_amount_fences(context, amount)
