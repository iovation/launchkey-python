from behave import given, when, then

from launchkey.entities.service.policy import ConditionalGeoFencePolicy, \
    MethodAmountPolicy, GeoCircleFence, TerritoryFence, FactorsPolicy


def default_factors_policy():
    return FactorsPolicy(
        knowledge_required=True,
        deny_emulator_simulator=False,
        deny_rooted_jailbroken=False
    )


def default_cond_geo_policy():
    return ConditionalGeoFencePolicy(
        inside=default_factors_policy(),
        outside=default_factors_policy()
    )


@given("the current Authorization Policy requires {count:d} factors")
def update_current_auth_policy_to_require_count_factors(context, count):
    current_auth = context.entity_manager.get_current_auth_policy()
    current_auth.set_minimum_requirements(minimum_amount=count)


@given("the current Authorization Policy requires inherence")
def update_current_auth_policy_to_require_inherence(context):
    current_auth = context.entity_manager.get_current_auth_policy()
    kwargs = {}
    for k in current_auth.minimum_requirements:
        kwargs[k] = True
    kwargs['inherence'] = True
    current_auth.set_minimum_requirements(**kwargs)


@given("the current Authorization Policy requires possession")
def update_current_auth_policy_to_require_possession(context):
    current_auth = context.entity_manager.get_current_auth_policy()
    kwargs = {}
    for k in current_auth.minimum_requirements:
        kwargs[k] = True
    kwargs['possession'] = True
    current_auth.set_minimum_requirements(**kwargs)


@given("the current Authorization Policy requires knowledge")
def update_current_auth_policy_to_require_knowledge(context):
    current_auth = context.entity_manager.get_current_auth_policy()
    kwargs = {}
    for k in current_auth.minimum_requirements:
        kwargs[k] = True
    kwargs['knowledge'] = True
    current_auth.set_minimum_requirements(**kwargs)


@when("I make a Policy based Authorization request for the User")
def attempt_to_make_policy_auth_with_directory_service(context):
    current_service = context.entity_manager.get_current_directory_service()
    user_identifier = context.entity_manager.get_current_user_identifier()
    policy = context.entity_manager.get_current_auth_policy()
    context.directory_service_auths_manager.create_auth_request(
        current_service.id,
        user_identifier,
        policy=policy
    )


@when("I attempt to make an Policy based Authorization request for the User "
      "identified by \"{user_identifier}\"")
def attempt_to_make_policy_auth_with_directory_service(context,
                                                       user_identifier):
    current_service = context.entity_manager.get_current_directory_service()
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


@given("the current Authorization Policy requires a geofence with a radius "
       "of {radius:f}, a latitude of {latitude:f}, a longitude of "
       "{longitude:f}, and a name of \"{name}\"")
def update_current_auth_policy_to_require_given_geofence(context, radius,
                                                         latitude, longitude,
                                                         name):
    current_auth = context.entity_manager.get_current_auth_policy()
    current_auth.add_geofence(latitude, longitude, radius, name=name)


@when(u"I create a new Factors Policy")
def step_impl(context):
    new_policy = FactorsPolicy()
    context.entity_manager.set_current_auth_policy(new_policy)


@when(u'I set the factors to "{raw_factors}"')
def policy_set_factors(context, raw_factors):
    factors = map(lambda f: f.upper().strip(), raw_factors.split(","))
    policy = context.entity_manager.get_current_auth_policy()
    if isinstance(policy, FactorsPolicy):
        for factor in factors:
            if factor == "INHERENCE":
                policy.inherence_required = True

            if factor == "POSSESSION":
                policy.possession_required = True

            if factor == "KNOWLEDGE":
                policy.knowledge_required = True
    else:
        raise Exception("Policy is not a FactorsPolicy")
    context.entity_manager.set_current_auth_policy(policy)


@when(u"I set {field} on the Policy to {value}")
def step_impl(context, field, value):
    policy = context.entity_manager.get_current_auth_policy()
    if field == "deny_rooted_jailbroken":
        policy.deny_rooted_jailbroken = value
    elif field == "deny_emulator_simulator":
        policy.deny_emulator_simulator = value
    else:
        raise NotImplementedError(u'{0} is not supported'.format(value))


@when(u"I set {field} on the Factors Policy to {value}")
def step_impl(context, field, value):
    policy = context.entity_manager.get_current_auth_policy()

    if not isinstance(policy, FactorsPolicy):
        raise ValueError("Expected FactorsPolicy but value received was not.")

    if field == "deny_rooted_jailbroken":
        policy.deny_rooted_jailbroken = value
    elif field == "deny_emulator_simulator":
        policy.deny_emulator_simulator = value
    else:
        raise NotImplementedError(u'{0} is not supported'.format(value))


@when(u"I set {field} on the Method Amount Policy to {value}")
def step_impl(context, field, value):
    policy = context.entity_manager.get_current_auth_policy()

    if not isinstance(policy, MethodAmountPolicy):
        raise ValueError("Expected MethodAmountPolicy but value received was "
                         "not.")

    if field == "deny_rooted_jailbroken":
        policy.deny_rooted_jailbroken = value
    elif field == "deny_emulator_simulator":
        policy.deny_emulator_simulator = value
    else:
        raise NotImplementedError(u'{0} is not supported'.format(value))


@when(u"I attempt to create a new Conditional Geofence Policy with the "
      u"{nested_policy} policy set to the new policy")
def step_impl(context, nested_policy):
    policy = context.entity_manager.get_current_auth_policy()
    default_nested_policy = MethodAmountPolicy(2)
    try:
        if nested_policy == "inside":
            ConditionalGeoFencePolicy(
                inside=policy,
                outside=default_nested_policy
            )
        else:
            ConditionalGeoFencePolicy(
                inside=default_nested_policy,
                outside=policy
            )
    except Exception as e:
        context.current_exception = e


@when(u"I create a new MethodAmountPolicy")
def step_impl(context):
    new_policy = MethodAmountPolicy()
    context.entity_manager.set_current_auth_policy(new_policy)


@when(u'I set the amount to "{amount}"')
def step_impl(context, amount):
    policy = context.entity_manager.get_current_auth_policy()
    if isinstance(policy, MethodAmountPolicy):
        policy.amount = int(amount)
    else:
        raise Exception("Policy is not a MethodAmountPolicy")
    context.entity_manager.set_current_auth_policy(policy)


@given(u"I have any Conditional Geofence Policy")
def step_impl(context):
    new_policy = default_cond_geo_policy()
    context.entity_manager.set_current_auth_policy(new_policy)


@when(u"I attempt to set the inside policy to any Conditional Geofence Policy")
def step_impl(context):
    policy = context.entity_manager.get_current_auth_policy()
    try:
        ConditionalGeoFencePolicy(
            inside=default_cond_geo_policy(),
            outside=policy.outside
        )
    except Exception as e:
        context.current_exception = e


@then(u'the amount should be set to "{amount}"')
def step_impl(context, amount):
    current_policy = context.entity_manager.get_current_auth_policy()
    if int(current_policy.amount) != int(amount):
        raise ValueError(
            "{0} does not equal current policy amount of {1}".format(
                amount,
                current_policy.amount
            )
        )


@when(u"I add the following GeoCircleFence items")
def step_impl(context):
    policy = context.entity_manager.get_current_auth_policy()
    for row in context.table:
        new_fence = GeoCircleFence(
            latitude=row["latitude"],
            longitude=row["longitude"],
            radius=row["radius"],
            name=row["name"]
        )

        policy.fences.append(new_fence)
    context.entity_manager.set_current_auth_policy(policy)


@when(u"I add the following TerritoryFence items")
def step_impl(context):
    policy = context.entity_manager.get_current_auth_policy()
    for row in context.table:
        new_fence = TerritoryFence(
            country=row["country"],
            administrative_area=row["admin_area"],
            postal_code=row["postal_code"],
            name=row["name"]
        )
        policy.fences.append(new_fence)
    context.entity_manager.set_current_auth_policy(policy)


@when(u'I set deny_rooted_jailbroken to "{bool_value}"')
def step_impl(context, bool_value):
    policy = context.entity_manager.get_current_auth_policy()
    policy.deny_rooted_jailbroken = bool(bool_value)
    context.entity_manager.set_current_auth_policy(policy)


@when('I set deny_emulator_simulator to "{bool_value}"')
def step_impl(context, bool_value):
    policy = context.entity_manager.get_current_auth_policy()
    policy.deny_emulator_simulator = bool(bool_value)
    context.entity_manager.set_current_auth_policy(policy)


@then('deny_rooted_jailbroken should be set to "{bool_value}"')
def step_impl(context, bool_value):
    policy = context.entity_manager.get_current_auth_policy()
    if str(policy.deny_rooted_jailbroken) != bool_value:
        raise ValueError(
            "{0} does not equal current policy amount of {1}".format(
                bool_value,
                policy.deny_rooted_jailbroken
            )
        )


@then('deny_emulator_simulator should be set to "{bool_value}"')
def step_impl(context, bool_value):
    policy = context.entity_manager.get_current_auth_policy()
    if str(policy.deny_emulator_simulator) != bool_value:
        raise ValueError(
            "{0} does not equal current policy amount of {1}".format(
                bool_value,
                policy.deny_emulator_simulator
            )
        )


@then(u'factors should be set to {raw_factors}')
def step_impl(context, raw_factors):
    current_policy = context.entity_manager.get_current_auth_policy()
    factors = map(lambda f: f.strip(), raw_factors.split(","))

    for factor in factors:
        if factor == "INHERENCE" and not current_policy.inherence_required:
            raise ValueError("Inherence was not set in the policy provided")

        if factor == "KNOWLEDGE" and not current_policy.knowledge_required:
            raise ValueError("Knowledge was not set in the policy provided")

        if factor == "POSSESSION" and not current_policy.possession_required:
            raise ValueError("Possession was not set in the policy provided")


@when("I set the {attribute} Policy to a new {policy_type}Policy")
def step_impl(context, attribute, policy_type):
    # SETS INSIDE / OUTSIDE ON COND_GEO
    current_policy = context.entity_manager.get_current_auth_policy()

    policy_type = policy_type.strip()
    if attribute == "inside":
        if policy_type == "Factors":
            current_policy.inside = FactorsPolicy(
                inherence_required=True,
                fences=None,
                deny_rooted_jailbroken=None,
                deny_emulator_simulator=None
            )
        elif policy_type == "MethodAmount":
            current_policy.inside = MethodAmountPolicy(
                amount=0,
                fences=None,
                deny_rooted_jailbroken=None,
                deny_emulator_simulator=None
            )
    elif attribute == "outside":
        if policy_type == "Factors":
            current_policy.outside = FactorsPolicy(
                inherence_required=True,
                fences=None,
                deny_rooted_jailbroken=None,
                deny_emulator_simulator=None
            )
        elif policy_type == "MethodAmount":
            current_policy.outside = MethodAmountPolicy(
                amount=0,
                fences=None,
                deny_rooted_jailbroken=None,
                deny_emulator_simulator=None
            )
    else:
        raise ValueError("{0} was provided and was not a known attribute of a "
                         "policy object".format(attribute))
    context.entity_manager.set_current_auth_policy(current_policy)


@when('I set the inside Policy factors to "Knowledge"')
def step_impl(context):
    current_policy = context.entity_manager.get_current_auth_policy()
    current_policy.inside.knowledge_required = True
    context.entity_manager.set_current_auth_policy(current_policy)


@then("the inside Policy should be a FactorsPolicy")
def step_impl(context):
    current_policy = context.entity_manager.get_current_auth_policy()
    if not isinstance(current_policy.inside, FactorsPolicy):
        raise ValueError("Policy {0} was not a FactorsPolicy".format(
            current_policy.inside
        ))


@then("the inside Policy should be a MethodAmountPolicy")
def step_impl(context):
    current_policy = context.entity_manager.get_current_auth_policy()
    if not isinstance(current_policy.inside, MethodAmountPolicy):
        raise ValueError("Policy {0} was not a MethodAmountPolicy".format(
            current_policy.inside
        ))


@then("the outside Policy should be a FactorsPolicy")
def step_impl(context):
    current_policy = context.entity_manager.get_current_auth_policy()
    if not isinstance(current_policy.outside, FactorsPolicy):
        raise ValueError("Policy {0} was not a FactorsPolicy".format(
            current_policy.outside
        ))


@then("the outside Policy should be a MethodAmountPolicy")
def step_impl(context):
    current_policy = context.entity_manager.get_current_auth_policy()
    if not isinstance(current_policy.outside, MethodAmountPolicy):
        raise ValueError("Policy {0} was not a MethodAmountPolicy".format(
            current_policy.outside
        ))


@when('I set the inside Policy amount to "2"')
def step_impl(context):
    current_policy = context.entity_manager.get_current_auth_policy()
    current_policy.inside.amount = 2
    context.entity_manager.set_current_auth_policy(current_policy)


@when('I set the outside Policy amount to "2"')
def step_impl(context):
    current_policy = context.entity_manager.get_current_auth_policy()
    current_policy.outside.amount = 2
    context.entity_manager.set_current_auth_policy(current_policy)


@when('I set the outside Policy factors to "Knowledge"')
def step_impl(context):
    current_policy = context.entity_manager.get_current_auth_policy()
    current_policy.outside.knowledge_required = True
    context.entity_manager.set_current_auth_policy(current_policy)


@then('the "{fence_name}" fence has a latitude of "{value}"')
def step_impl(context, fence_name, value):
    current_policy = context.entity_manager.get_current_auth_policy()
    for fence in current_policy.fences:
        if fence.name == fence_name:
            if fence.latitude != float(value):
                raise ValueError("The fence latitude of {0} was not {1}".format(
                    fence.latitude, value
                ))
            return True
    raise ValueError("A Fence with the name {0} was not found".format(
        fence_name, value
    ))


@then('the "{fence_name}" fence has a longitude of "{value}"')
def step_impl(context, fence_name, value):
    current_policy = context.entity_manager.get_current_auth_policy()
    for fence in current_policy.fences:
        if fence.name == fence_name:
            if fence.longitude != float(value):
                raise ValueError("A Fence with the name {0} was not found "
                                 "with the value {1}".format(fence.longitude,
                                                             value))
            return True
    raise ValueError("A Fence with the name {0} was not found".format(
        fence_name, value
    ))


@then('the "{fence_name}" fence has a radius of "{value}"')
def step_impl(context, fence_name, value):
    current_policy = context.entity_manager.get_current_auth_policy()
    for fence in current_policy.fences:
        if fence.name == fence_name:
            if fence.radius != float(value):
                raise ValueError(
                    "A Fence with the name {0} was not found with the "
                    "value {1}".format(fence.radius, value)
                )
            return True
    raise ValueError(
        "A Fence with the name {0} was not found with the value {1}".format(
            fence_name, value
        )
    )


@then('the "{fence_name}" fence has a country of "{country}"')
def step_impl(context, fence_name, country):
    current_policy = context.entity_manager.get_current_auth_policy()
    for fence in current_policy.fences:
        if fence.name == fence_name:
            if fence.country != country:
                raise ValueError(
                    "A Fence with the name {0} was not found with the "
                    "value {1}".format(fence.country, country)
                )
            return True
    raise ValueError(
        "A Fence with the name {0} was not found with the value {1}".format(
            fence_name, country
        )
    )


@then('the "{fence_name}" fence has an administrative_area of "{admin_area}"')
def step_impl(context, fence_name, admin_area):
    current_policy = context.entity_manager.get_current_auth_policy()
    for fence in current_policy.fences:
        if fence.name == fence_name:
            if fence.administrative_area != admin_area:
                raise ValueError(
                    "A Fence with the name {0} was not found with the "
                    "value {1}".format(fence.administrative_area, admin_area)
                )
            return True
    raise ValueError(
        "A Fence with the name {0} was not found with the value {1}".format(
            fence_name, admin_area
        )
    )


@then('the "{fence_name}" fence has a postal_code of "{zip_code}"')
def step_impl(context, fence_name, zip_code):
    current_policy = context.entity_manager.get_current_auth_policy()
    for fence in current_policy.fences:
        if fence.name == fence_name:
            if fence.postal_code != zip_code:
                raise ValueError(
                    "A Fence with the name {0} was not found with the "
                    "value {1}".format(fence.postal_code, zip_code)
                )
            return True
    raise ValueError(
        "A Fence with the name {0} was not found with the value {1}".format(
            fence_name, zip_code
        )
    )


@then('amount should be set to "{amount}"')
def calculate_amount(context, amount):
    current_policy = context.entity_manager.get_current_auth_policy()
    if current_policy.amount != int(amount):
        raise ValueError(
            "Amount was set to {0} in the current Policy when it should have "
            "been {1}".format(current_policy.amount,amount)
        )


@then('the inside Policy amount should be set to "{amount}"')
def step_impl(context, amount):
    current_policy = context.entity_manager.get_current_auth_policy()
    if current_policy.inside.amount != int(amount):
        raise ValueError(
            "Amount was set to {0} in the current Policy when it should have "
            "been {1}".format(current_policy.inside.amount, amount)
        )


@then('the outside Policy amount should be set to "{amount}"')
def step_impl(context, amount):
    current_policy = context.entity_manager.get_current_auth_policy()
    if current_policy.outside.amount != int(amount):
        raise ValueError(
            "Amount was set to {0} in the current Policy when it should have "
            "been {1}".format(current_policy.outside.amount, amount)
        )


@then('the {subpolicy} Policy factors should be set to "{raw_factors}"')
def step_impl(context, subpolicy, raw_factors):
    current_policy = context.entity_manager.get_current_auth_policy()
    policy = context.entity_manager.get_current_auth_policy()
    current_subpolicy = current_policy.inside if subpolicy == "inside" else \
        current_policy.outside
    factors = map(lambda f: f.strip(), raw_factors.split(","))

    if not isinstance(policy, ConditionalGeoFencePolicy):
        raise Exception("Policy is not a ConditionalGeoFencePolicy")

    for factor in factors:
        if factor == "INHERENCE" and not current_subpolicy.inherence_required:
            raise ValueError("Inherence was not set in %s policy" % subpolicy)

        if factor == "KNOWLEDGE" and not current_subpolicy.knowledge_required:
            raise ValueError("Knowledge was not set in %s policy" % subpolicy)

        if factor == "POSSESSION" and not current_subpolicy.possession_required:
            raise ValueError("Possession was not set in %s policy" % subpolicy)


@then("the Advanced Authorization response should contain a GeoCircleFence "
      "with a radius of {rad}, a latitude of {lat}, a longitude of {lon}, "
      "and a name of \"{name}\"")
def step_impl(context, rad, lat, lon, name):
    policy = context.entity_manager.get_current_auth_response().policy
    if not policy.fences:
        raise Exception("Expected a GeoCircleFence within the auth response "
                        "but no fences exist.")

    for fence in policy.fences:
        if fence.radius == float(rad) and fence.latitude == float(lat) and \
           fence.longitude == float(lon) and fence.name == name:
            return  # Found a matching fence, can safely exit

    raise ValueError("Expected a policy containing a Geocircle fence with "
                     "a radius of %s, latitude of %s, longitude of %s, and "
                     "name of %s, but found none" % (rad, lat, lon, name))


@then("the Advanced Authorization response should contain a TerritoryFence "
      "with a country of \"{country}\", a administrative area of "
      "\"{admin_area}\", a postal code of \"{postal_code}\", and a name of "
      "\"{name}\"")
def step_impl(context, country, admin_area, postal_code, name):
    policy = context.entity_manager.get_current_auth_response().policy
    if not policy.fences:
        raise Exception("Expected a TerritoryFence within the auth response "
                        "but no fences exist.")

    for fence in policy.fences:
        if isinstance(fence, TerritoryFence) and \
           fence.country == country and \
           fence.administrative_area == admin_area and \
           fence.postal_code == postal_code and fence.name == name:
            return  # Found a matching fence, can safely exit

    raise ValueError("Expected a policy containing a TerritoryFence fence "
                     "with a country of %s, administrative area of %s, postal "
                     "code of %s, and name of %s,  but found none" %
                     (country, admin_area, postal_code, name))
