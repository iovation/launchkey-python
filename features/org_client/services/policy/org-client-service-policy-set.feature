Feature: Organization Client can set Organization Service Policy
  In order to manage the Authorization Policy of an Organization Service
  As an Organization Client
  I can set the Authorization Policy of an Organization Service

  Background:
    Given I created an Organization Service

  Scenario: Setting the policy for invalid Service throws Forbidden
    When the Organization Service Policy is set to require 2 factors
    And I attempt to set the Policy for the Organization Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a ServiceNotFound error occurs

  Scenario: Setting the required factors will set only the factors and all else will be empty or null
    When the Organization Service Policy is set to require 2 factors
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy requires 2 factors
    And the Organization Service Policy has no requirement for inherence
    And the Organization Service Policy has no requirement for knowledge
    And the Organization Service Policy has no requirement for possession
    And the Organization Service Policy has 0 locations
    And the Organization Service Policy has 0 time fences
    And the Organization Service Policy has no requirement for jail break protection

  Scenario: Setting the individual factors will set only the factors and all else will be empty or null
    When the Organization Service Policy is set to require inherence
    And the Organization Service Policy is set to require knowledge
    And the Organization Service Policy is set to require possession
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy has no requirement for number of factors
    And the Organization Service Policy does require inherence
    And the Organization Service Policy does require knowledge
    And the Organization Service Policy does require possession
    And the Organization Service Policy has 0 locations
    And the Organization Service Policy has 0 time fences
    And the Organization Service Policy has no requirement for jail break protection

  Scenario: Setting jail break protection will only set jail break protection and everything else will be empty of null
    And the Organization Service Policy is set to require jail break protection
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy does require jail break protection
    And the Organization Service Policy has no requirement for number of factors
    And the Organization Service Policy has no requirement for inherence
    And the Organization Service Policy has no requirement for knowledge
    And the Organization Service Policy has no requirement for possession
    And the Organization Service Policy has 0 locations
    And the Organization Service Policy has 0 time fences


  Scenario: When setting Time Fences, they are set and nothing else as expected
    When the Organization Service Policy is set to have the following Time Fences:
      | Name      | Days                                     | Start Hour | Start Minute | End Hour | End Minute | Time Zone           |
      | Week Days | Monday,Tuesday,Wednesday,Thursday,Friday | 0          | 0            | 23       | 59         | America/Los_Angeles |
      | Week Ends | Saturday,Sunday                          | 0          | 0            | 23       | 59         | America/New_York    |
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy has the following Time Fences:
      | Name      | Days                                     | Start Hour | Start Minute | End Hour | End Minute | Time Zone           |
      | Week Days | Monday,Tuesday,Wednesday,Thursday,Friday | 0          | 0            | 23       | 59         | America/Los_Angeles |
      | Week Ends | Saturday,Sunday                          | 0          | 0            | 23       | 59         | America/New_York    |
    And the Organization Service Policy has no requirement for number of factors
    And the Organization Service Policy has no requirement for inherence
    And the Organization Service Policy has no requirement for knowledge
    And the Organization Service Policy has no requirement for possession
    And the Organization Service Policy has 0 locations


  Scenario: Geofence locations work as expected
    When the Organization Service Policy is set to have the following Geofence locations:
      | Name           | Latitude | Longitude | Radius |
      | Location Alpha | 12.3     | 23.4      | 500    |
      | Location Beta  | 32.1     | 43.2      | 1000   |
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy has the following Geofence locations:
      | Name           | Latitude | Longitude | Radius |
      | Location Alpha | 12.3     | 23.4      | 500    |
      | Location Beta  | 32.1     | 43.2      | 1000   |
    And the Organization Service Policy has no requirement for number of factors
    And the Organization Service Policy has no requirement for inherence
    And the Organization Service Policy has no requirement for knowledge
    And the Organization Service Policy has no requirement for possession
    And the Organization Service Policy has 0 time fences

  Scenario: Setting required factors, locations, and fences properly set the values.
    When the Organization Service Policy is set to require 2 factors
    And the Organization Service Policy is set to require jail break protection
    And the Organization Service Policy is set to have the following Time Fences:
      | Name      | Days                                     | Start Hour | Start Minute | End Hour | End Minute | Time Zone           |
      | Week Days | Monday,Tuesday,Wednesday,Thursday,Friday | 0          | 0            | 23       | 59         | America/Los_Angeles |
      | Week Ends | Saturday,Sunday                          | 0          | 0            | 23       | 59         | America/New_York    |
    And the Organization Service Policy is set to have the following Geofence locations:
      | Name           | Latitude | Longitude | Radius |
      | Location Alpha | 12.3     | 23.4      | 500    |
      | Location Beta  | 32.1     | 43.2      | 1000   |
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy requires 2 factors
    And the Organization Service Policy does require jail break protection
    And the Organization Service Policy has no requirement for inherence
    And the Organization Service Policy has no requirement for knowledge
    And the Organization Service Policy has no requirement for possession
    And the Organization Service Policy has the following Time Fences:
      | Name      | Days                                     | Start Hour | Start Minute | End Hour | End Minute | Time Zone           |
      | Week Days | Monday,Tuesday,Wednesday,Thursday,Friday | 0          | 0            | 23       | 59         | America/Los_Angeles |
      | Week Ends | Saturday,Sunday                          | 0          | 0            | 23       | 59         | America/New_York    |
    And the Organization Service Policy has the following Geofence locations:
      | Name           | Latitude | Longitude | Radius |
      | Location Alpha | 12.3     | 23.4      | 500    |
      | Location Beta  | 32.1     | 43.2      | 1000   |

  Scenario: Setting individual factors, locations, and fences properly set the values.
    When the Organization Service Policy is set to require inherence
    And the Organization Service Policy is set to require knowledge
    And the Organization Service Policy is set to require possession
    And the Organization Service Policy is set to require jail break protection
    And the Organization Service Policy is set to have the following Geofence locations:
      | Name           | Latitude | Longitude | Radius |
      | Location Alpha | 12.3     | 23.4      | 500    |
      | Location Beta  | 32.1     | 43.2      | 1000   |
    And the Organization Service Policy is set to have the following Time Fences:
      | Name      | Days                                     | Start Hour | Start Minute | End Hour | End Minute | Time Zone           |
      | Week Days | Monday,Tuesday,Wednesday,Thursday,Friday | 0          | 0            | 23       | 59         | America/Los_Angeles |
      | Week Ends | Saturday,Sunday                          | 0          | 0            | 23       | 59         | America/New_York    |
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy has no requirement for number of factors
    And the Organization Service Policy does require jail break protection
    And the Organization Service Policy does require inherence
    And the Organization Service Policy does require knowledge
    And the Organization Service Policy does require possession
    And the Organization Service Policy has the following Time Fences:
      | Name      | Days                                     | Start Hour | Start Minute | End Hour | End Minute | Time Zone           |
      | Week Days | Monday,Tuesday,Wednesday,Thursday,Friday | 0          | 0            | 23       | 59         | America/Los_Angeles |
      | Week Ends | Saturday,Sunday                          | 0          | 0            | 23       | 59         | America/New_York    |
    And the Organization Service Policy has the following Geofence locations:
      | Name           | Latitude | Longitude | Radius |
      | Location Alpha | 12.3     | 23.4      | 500    |
      | Location Beta  | 32.1     | 43.2      | 1000   |

  Scenario Outline: Setting Amount on a Method Amount policy works as expected
    When I create a new Method Amount Policy
    And I set the amount to "<amount>"
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the amount should be set to "<amount>"
  Examples:
  | amount |
  | 0      |
  | 1      |
  | 2      |
  | 3      |
  | 4      |
  | 5      |

  Scenario: Setting Fences on a Method Amount Policy works as expected
    When I create a new Method Amount Policy
    And I add the following geo_circle fences:
    | latitude | longitude | radius | name        |
    | 300.0    | 500.0     | 15200  | Large Fence |
    | -50      | -140      | 100    | Small Fence |
    And I add the following territory fences:
    | country | admin_area | postal_code | name  |
    | US      | US-NV      | 89120       | US-NV |
    | US      | US-CA      | 90001       | US-CA |
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy has "4" fences

  Scenario Outline: Setting Factors on a Factors Policy works as expected
    When I create a new Factors Policy
    And I set the factors to <factors>
    And I set the Policy for the Current Organization Service
    When I retrieve the Policy for the Current Organization Service
    Then factors should be set to <factors>
  Examples:
  | factors                          |
  | Knowledge                        |
  | Inherence                        |
  | Possession                       |
  | Knowledge, Inherence             |
  | Knowledge, Possession            |
  | Inherence, Possession            |
  | Knowledge, Inherence, Possession |

  Scenario: Setting Fences on a Factors Policy works as expected
    When I create a new Factors Policy
    And I add the following geo_circle fences:
    | latitude | longitude | radius | name        |
    | 300.0    | 500.0     | 15200  | Large Fence |
    | -50      | -140      | 100    | Small Fence |
    And I add the following territory fences:
    | country | admin_area | postal_code | name  |
    | US      | US-NV      | 89120       | US-NV |
    | US      | US-CA      | 90001       | US-CA |
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy has "4" fences

  Scenario: Setting Inside Policy to Factors Policy works as expected
    Given the Organization Service is set to any Conditional Geofence Policy
    When I create a new Factors Policy
    And I set the factors to "Knowledge"
    And I set the inside Policy to the newly created Policy
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the inside Policy should be a FactorsPolicy

  Scenario: Setting Inside Policy to Methods Amount Policy works as expected
    Given the Organization Service is set to any Conditional Geofence Policy
    When I create a new Method Amount Policy
    And I set the amount to "2"
    And I set the inside Policy to the newly created Policy
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the inside Policy should be a MethodAmountPolicy

  Scenario: Setting Outside Policy to Factors Policy works as expected
    Given the Organization Service is set to any Conditional Geofence Policy
    When I create a new Factors Policy
    And I set the factors to "Knowledge"
    And I set the outside Policy to the newly created Policy
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the outside Policy should be a FactorsPolicy

  Scenario: Setting Outside Policy to Methods Amount Policy works as expected
    Given the Organization Service is set to any Conditional Geofence Policy
    When I create a new Method Amount Policy
    And I set the amount to "2"
    And I set the outside Policy to the newly created Policy
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the outside Policy should be a MethodAmountPolicy

  Scenario: Setting Fences on a Conditional Geofence Policy works as expected
    Given the Organization Service is set to any Conditional Geofence Policy
    When I add the following GeoCircleFence items:
    | latitude | longitude | radius | name        |
    | 300.0    | 500.0     | 15200  | Large Fence |
    | -50      | -140      | 100    | Small Fence |
    And I add the following TerritoryFence items:
    | country | admin_area | postal_code | name  |
    | US      | US-NV      | 89120       | US-NV |
    | US      | US-CA      | 90001       | US-CA |
    And I set the Policy for the Current Organization Service
    And I retrieve the Policy for the Current Organization Service
    Then the Organization Service Policy has "4" fences

  Scenario Outline: Setting device integrity checks on inside nested conditions are invalid
    When I create a new Factors Policy
    And I set the factors to "Knowledge"
    And I set <field> to <value>
    And I create a new Conditional Geofence Policy with the inside policy set to the new policy
    Then an InvalidPolicyAttributes error occurs
  Examples:
  | field                   | value |
  | deny_rooted_jailbroken  | True  |
  | deny_emulator_simulator | True  |

  Scenario Outline: Setting device integrity checks on outside nested conditions are invalid
    When I create a new Factors Policy
    And I set the factors to "Knowledge"
    And I set <field> to <value>
    And I create a new Conditional Geofence Policy with the outside policy set to the new policy
    Then an InvalidPolicyAttributes error occurs
  Examples:
  | field                   | value |
  | deny_rooted_jailbroken  | True  |
  | deny_emulator_simulator | True  |

  Scenario: Stacked Conditional Geofences are not allowed
    Given the Organization Service is set to any Conditional Geofence Policy
    When I create a new Method Amount Policy
    And I set the amount to "2"
    And I set the outside Policy to the newly created Policy
    And I create a new Method Amount Policy
    And I set the amount to "1"
    And I set the inside Policy to the newly created Policy
    And I set the Policy for the Current Organization Service
    Then an UnknownPolicyException error occurs
