# Created by branden.jordan at 2019-09-09
Feature: SDK Policy Object Creation Limitations
  I should be able to create Policy objects and they will behave appropriately

  # SDK Tests
  Scenario Outline: Setting device integrity checks on FactorsPolicy inside nested conditions are invalid
    When I create a new Factors Policy
    And I set the factors to "Knowledge"
    And I set <field> on the Policy to <value>
    And I attempt to create a new Conditional Geofence Policy with the inside policy set to the new policy
    Then an InvalidPolicyAttributes error occurs
  Examples:
  | field                   | value |
  | deny_rooted_jailbroken  | True  |
  | deny_emulator_simulator | True  |

  Scenario Outline: Setting device integrity checks on FactorsPolicy outside nested conditions are invalid
    When I create a new Factors Policy
    And I set the factors to "Knowledge"
    And I set <field> on the Policy to <value>
    And I attempt to create a new Conditional Geofence Policy with the outside policy set to the new policy
    Then an InvalidPolicyAttributes error occurs
  Examples:
  | field                   | value |
  | deny_rooted_jailbroken  | True  |
  | deny_emulator_simulator | True  |

  Scenario Outline: Setting device integrity checks on MethodAmountPolicy inside nested conditions are invalid
    When I create a new MethodAmountPolicy
    And I set the amount to "2"
    And I set <field> on the Policy to <value>
    And I attempt to create a new Conditional Geofence Policy with the inside policy set to the new policy
    Then an InvalidPolicyAttributes error occurs
  Examples:
  | field                   | value |
  | deny_rooted_jailbroken  | True  |
  | deny_emulator_simulator | True  |

  Scenario Outline: Setting device integrity checks on MethodAmountPolicy outside nested conditions are invalid
    When I create a new MethodAmountPolicy
    And I set the amount to "2"
    And I set <field> on the Policy to <value>
    And I attempt to create a new Conditional Geofence Policy with the outside policy set to the new policy
    Then an InvalidPolicyAttributes error occurs
  Examples:
  | field                   | value |
  | deny_rooted_jailbroken  | True  |
  | deny_emulator_simulator | True  |

  Scenario: Stacked Conditional Geofences are not allowed
    Given I have any Conditional Geofence Policy
    When I attempt to set the inside policy to any Conditional Geofence Policy
    Then an InvalidPolicyAttributes error occurs
