Feature: Directory Client can retrieve Directory Service Policy
  In order to manage the Authorization Policy of a Directory Service
  As a Directory Client
  I can retrieve the Authorization Policy of a Directory Service

  Background:
    Given I created a Directory
    And I created a Directory Service

  Scenario: Getting the policy when none is set returns a blank Policy
    When I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy has no requirement for inherence
    Then the Directory Service Policy has no requirement for knowledge
    Then the Directory Service Policy has no requirement for possession
    Then the Directory Service Policy has no requirement for number of factors

  Scenario: Getting the required factors works as expected
    Given the Directory Service Policy is set to require 2 factors
    And I set the Policy for the Current Directory Service
    When I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy requires 2 factors

  Scenario: Getting the factor requirements works as expected
    Given the Directory Service Policy is set to require inherence
    Given the Directory Service Policy is set to require knowledge
    Given the Directory Service Policy is set to require possession
    And I set the Policy for the Current Directory Service
    When I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy does require inherence
    Then the Directory Service Policy does require knowledge
    Then the Directory Service Policy does require possession

  Scenario: Getting jail break protection works as expected
    Given the Directory Service Policy is set to require jail break protection
    And I set the Policy for the Current Directory Service
    When I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy does require jail break protection

  Scenario: Time Fences work as expected
    Given the Directory Service Policy is set to have the following Time Fences:
      | Name      | Days                                     | Start Hour | Start Minute | End Hour | End Minute | Time Zone           |
      | Week Days | Monday,Tuesday,Wednesday,Thursday,Friday | 0          | 0            | 23       | 59         | America/Los_Angeles |
      | Week Ends | Saturday,Sunday                          | 0          | 0            | 23       | 59         | America/New_York |
    And I set the Policy for the Current Directory Service
    When I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy has the following Time Fences:
      | Name      | Days                                     | Start Hour | Start Minute | End Hour | End Minute | Time Zone           |
      | Week Days | Monday,Tuesday,Wednesday,Thursday,Friday | 0          | 0            | 23       | 59         | America/Los_Angeles |
      | Week Ends | Saturday,Sunday                          | 0          | 0            | 23       | 59         | America/New_York |

  Scenario: Geofence locations work as expected
    Given the Directory Service Policy is set to have the following Geofence locations:
      | Name           | Latitude | Longitude | Radius |
      | Location Alpha | 12.3     | 23.4      | 500    |
      | Location Beta  | 32.1     | 43.2      | 1000   |
    And I set the Policy for the Current Directory Service
    When I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy has the following Geofence locations:
      | Name           | Latitude | Longitude | Radius |
      | Location Alpha | 12.3     | 23.4      | 500    |
      | Location Beta  | 32.1     | 43.2      | 1000   |

  Scenario: Getting the policy for invalid Service throws Forbidden
    When I attempt to retrieve the Policy for the Directory Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a ServiceNotFound error occurs

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
    And I set the Policy for the Current Directory Service
    And I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy has "4" fences
    And the Directory Service Policy contains the GeoCircleFence "Large Fence"
    And that fence has a latitude of "300.0"
    And that fence has a longitude of "500.0"
    And that fence has a radius of "15200"
    And the Directory Service Policy contains the GeoCircleFence "Small Fence"
    And that fence has a latitude of "-50"
    And that fence has a longitude of "-140"
    And that fence has a radius of "100"
    And the Directory Service Policy contains the TerritoryFence "US-NV"
    And that fence has a country of "US"
    And that fence has an administrative_area of "US-NV"
    And that fence has a postal_code of "89120"
    And the Directory Service Policy contains the TerritoryFence "US-CA"
    And that fence has a country of "US"
    And that fence has an administrative_area of "US-CA"
    And that fence has a postal_code of "90001"

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
    And I set the Policy for the Current Directory Service
    And I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy has "4" fences
    And the Directory Service Policy contains the GeoCircleFence "Large Fence"
    And that fence has a latitude of "300.0"
    And that fence has a longitude of "500.0"
    And that fence has a radius of "15200"
    And the Directory Service Policy contains the GeoCircleFence "Small Fence"
    And that fence has a latitude of "-50"
    And that fence has a longitude of "-140"
    And that fence has a radius of "100"
    And the Directory Service Policy contains the TerritoryFence "US-NV"
    And that fence has a country of "US"
    And that fence has an administrative_area of "US-NV"
    And that fence has a postal_code of "89120"
    And the Directory Service Policy contains the TerritoryFence "US-CA"
    And that fence has a country of "US"
    And that fence has an administrative_area of "US-CA"
    And that fence has a postal_code of "90001"

  Scenario: Setting Inside Policy to Factors Policy works as expected
    Given the Directory Service is set to any Conditional Geofence Policy
    When I create a new Factors Policy
    And I set the factors to "Knowledge"
    And I set the inside Policy to the newly created Policy
    And I set the Policy for the Current Directory Service
    And I retrieve the Policy for the Current Directory Service
    Then the inside Policy should be a FactorsPolicy
    And factors should be set to "Knowledge"
    And deny_rooted_jailbroken should be set to "False"
    And deny_emulator_simulator should be set to "False"
    And fences should be empty

  Scenario: Setting Inside Policy to Methods Amount Policy works as expected
    Given the Directory Service is set to any Conditional Geofence Policy
    When I create a new Method Amount Policy
    And I set the amount to "2"
    And I set the inside Policy to the newly created Policy
    And I set the Policy for the Current Directory Service
    And I retrieve the Policy for the Current Directory Service
    Then the inside Policy should be a MethodAmountPolicy
    And amount should be set to "2"
    And deny_rooted_jailbroken should be set to "False"
    And deny_emulator_simulator should be set to "False"
    And fences should be empty

  Scenario: Setting Outside Policy to Factors Policy works as expected
    Given the Directory Service is set to any Conditional Geofence Policy
    When I create a new Factors Policy
    And I set the factors to "Knowledge"
    And I set the outside Policy to the newly created Policy
    And I set the Policy for the Current Directory Service
    And I retrieve the Policy for the Current Directory Service
    Then the outside Policy should be a FactorsPolicy
    And factors should be set to "Knowledge"
    And deny_rooted_jailbroken should be set to "False"
    And deny_emulator_simulator should be set to "False"
    And fences should be empty

  Scenario: Setting Outside Policy to Methods Amount Policy works as expected
    Given the Directory Service is set to any Conditional Geofence Policy
    When I create a new Method Amount Policy
    And I set the amount to "2"
    And I set the outside Policy to the newly created Policy
    And I set the Policy for the Current Directory Service
    And I retrieve the Policy for the Current Directory Service
    Then the outside Policy should be a MethodAmountPolicy
    And amount should be set to "2"
    And deny_rooted_jailbroken should be set to "False"
    And deny_emulator_simulator should be set to "False"
    And fences should be empty

  Scenario: Setting Fences on a Conditional Geofence Policy works as expected
    Given the Directory Service is set to any Conditional Geofence Policy
    When I add the following GeoCircleFence items:
    | latitude | longitude | radius | name        |
    | 300.0    | 500.0     | 15200  | Large Fence |
    | -50      | -140      | 100    | Small Fence |
    And I add the following TerritoryFence items:
    | country | admin_area | postal_code | name  |
    | US      | US-NV      | 89120       | US-NV |
    | US      | US-CA      | 90001       | US-CA |
    And I set the Policy for the Current Directory Service
    And I retrieve the Policy for the Current Directory Service
    Then the Directory Service Policy has "4" fences
    And the Directory Service Policy contains the GeoCircleFence "Large Fence"
    And that fence has a latitude of "300.0"
    And that fence has a longitude of "500.0"
    And that fence has a radius of "15200"
    And the Directory Service Policy contains the GeoCircleFence "Small Fence"
    And that fence has a latitude of "-50"
    And that fence has a longitude of "-140"
    And that fence has a radius of "100"
    And the Directory Service Policy contains the TerritoryFence "US-NV"
    And that fence has a country of "US"
    And that fence has an administrative_area of "US-NV"
    And that fence has a postal_code of "89120"
    And the Directory Service Policy contains the TerritoryFence "US-CA"
    And that fence has a country of "US"
    And that fence has an administrative_area of "US-CA"
    And that fence has a postal_code of "90001"
