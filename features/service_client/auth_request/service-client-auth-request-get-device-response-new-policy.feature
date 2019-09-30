@device_testing
Feature: Service Client Authorization Request: Get Device Response Policy - New Format
  In order to understand an auth response
  As a Directory Service
  I can retrieve an Authorization Requests that been responded to and determine the policy that was last processed by the device in the new policy format
​
  Background:
    Given I created a Directory
    And I have added an SDK Key to the Directory
    And I created a Directory Service
    And I have a linked device
​
  Scenario: Verify that a Factors Policy can be parsed
    When I create a new Factors Policy
    And I set the factors to "INHERENCE"
    And I set the Policy for the Current Directory Service
    And I make an Authorization request
    And I approve the auth request
    And I get the response for the Advanced Authorization request
    Then the Advanced Authorization response should be approved
    And the Advanced Authorization response should require Inherence
    And the Advanced Authorization response should have the requirement "types"
​
​
  Scenario: Verify that a Method Amount Policy can be parsed
    When I create a new MethodAmountPolicy
    And I set the amount to "2"
    And I set the Policy for the Current Directory Service
    And I make an Authorization request
    And I approve the auth request
    And I get the response for the Advanced Authorization request
    Then the Advanced Authorization response should be approved
    And the Advanced Authorization response should have amount set to 2
    And the Advanced Authorization response should have the requirement "amount"
​
​
  Scenario: Verify that a Conditional Geofence Policy can be parsed
    Given the Directory Service is set to any Conditional Geofence Policy
    When I add the following GeoCircleFence items
    | latitude | longitude | radius  | name        |
    | 41       | -141      | 234400  | Large Fence |
    And I set the Policy for the Current Directory Service to the new policy
    And I make an Authorization request
    And I receive the auth request and acknowledge the failure message
    And I get the response for the Advanced Authorization request
    Then the Advanced Authorization response should be denied
    And the Advanced Authorization response should contain a GeoCircleFence with a radius of 234400, a latitude of 41, a longitude of -141, and a name of "Large Fence"
    And the Advanced Authorization response should have the requirement "cond_geo"
​
  Scenario: Verify that GeoCircleFence fences can be parsed from Fences on a Factors Policy
    When I create a new Factors Policy
    And I add the following GeoCircleFence items
    | latitude | longitude | radius | name        |
    | 45.1250  | 150.51    | 15200  | Large Fence |
    | -50.01   | -140      | 100    | Small Fence |
    And I set the Policy for the Current Directory Service to the new policy
    And I make an Authorization request
    And I receive the auth request and acknowledge the failure message
    And I get the response for the Advanced Authorization request
    Then the Advanced Authorization response should be denied
    And the Advanced Authorization response should contain a GeoCircleFence with a radius of 15200, a latitude of 45.1250, a longitude of 150.51, and a name of "Large Fence"
    And the Advanced Authorization response should contain a GeoCircleFence with a radius of 100, a latitude of -50.01, a longitude of -140, and a name of "Small Fence"
    And the Advanced Authorization response should have the requirement "types"
​
  Scenario: Verify that GeoCircleFence fences can be parsed from Fences on a Methods Amount Policy
    When I create a new MethodAmountPolicy
    And I set the amount to "4"
    And I add the following GeoCircleFence items
    | latitude | longitude | radius | name        |
    | 45.1250  | 150.51    | 15200  | Large Fence |
    | -50.01   | -140      | 100    | Small Fence |
    And I set the Policy for the Current Directory Service to the new policy
    And I make an Authorization request
    And I receive the auth request and acknowledge the failure message
    And I get the response for the Advanced Authorization request
    Then the Advanced Authorization response should be denied
    And the Advanced Authorization response should contain a GeoCircleFence with a radius of 15200, a latitude of 45.1250, a longitude of 150.51, and a name of "Large Fence"
    And the Advanced Authorization response should contain a GeoCircleFence with a radius of 100, a latitude of -50.01, a longitude of -140, and a name of "Small Fence"
    And the Advanced Authorization response should have the requirement "amount"
​
  Scenario: Verify that TerritoryFence fences can be parsed from Fences on a Factors Policy
    When I create a new Factors Policy
    And I add the following TerritoryFence items
    | country | admin_area | postal_code | name  |
    | US      | US-NV      | 89120       | US-NV |
    And I set the Policy for the Current Directory Service to the new policy
    And I make an Authorization request
    And I receive the auth request and acknowledge the failure message
    And I get the response for the Advanced Authorization request
    Then the Advanced Authorization response should be denied
    And the Advanced Authorization response should contain a TerritoryFence with a country of "US", a administrative area of "US-NV", a postal code of "89120", and a name of "US-NV"
    And the Advanced Authorization response should have the requirement "types"
​
  Scenario: Verify that TerritoryFence fences can be parsed from Fences on a Methods Amount Policy
    When I create a new MethodAmountPolicy
    And I add the following TerritoryFence items
    | country | admin_area | postal_code | name  |
    | US      | US-NV      | 89120       | US-NV |
    And I set the Policy for the Current Directory Service to the new policy
    And I make an Authorization request
    And I receive the auth request and acknowledge the failure message
    And I get the response for the Advanced Authorization request
    Then the Advanced Authorization response should be denied
    And the Advanced Authorization response should contain a TerritoryFence with a country of "US", a administrative area of "US-NV", a postal code of "89120", and a name of "US-NV"
    And the Advanced Authorization response should have the requirement "amount"
​
  Scenario: Verify that TerritoryFence fences can be parsed from Fences on a Conditional Geofence Policy
    Given the Directory Service is set to any Conditional Geofence Policy
    When I add the following TerritoryFence items
    | country | admin_area | postal_code | name  |
    | US      | US-NV      | 89120       | US-NV |
    And I set the Policy for the Current Directory Service to the new policy
    And I make an Authorization request
    And I receive the auth request and acknowledge the failure message
    And I get the response for the Advanced Authorization request
    Then the Advanced Authorization response should be denied
    And the Advanced Authorization response should contain a TerritoryFence with a country of "US", a administrative area of "US-NV", a postal code of "89120", and a name of "US-NV"
    And the Advanced Authorization response should have the requirement "cond_geo"
