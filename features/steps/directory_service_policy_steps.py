from behave import given, when, then

from launchkey.entities.service import AuthPolicy


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


# Set Directory Service Policy

@given("the Directory Service Policy is set to require {count:d} factors")
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


@given("I set the Policy for the Current Directory Service")
def set_directory_service_policy_require_to_current_policy(context):
    current_directory = context.entity_manager.get_current_directory()
    current_service = context.entity_manager.get_current_directory_service()
    policy = context.entity_manager.get_current_directory_service_policy()
    context.directory_service_policy_manager.set_service_policy(
        current_service.id,
        current_directory.id,
        policy
    )
