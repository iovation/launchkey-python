@device_testing
Feature: Service Client Authorization Request: Get Device Response Policy
  In order to understand an auth response
  As a Directory Service
  I can retrieve an Authorization Requests that been responded to and determine
  the policy that was used

  Background:
    Given I created a Directory
    And I have added an SDK Key to the Directory
    And I created a Directory Service
    And I have a linked Device

  Scenario: Verify that geofences without names received from a device can be parsed
    Given the current Authorization Policy requires a geofence with a radius of 150.0, a latitude of 23.4, and a longitude of -56.7
    And the current Authorization Policy requires a geofence with a radius of 100.0, a latitude of -23.4, and a longitude of 56.7
    When I make a Policy based Authorization request for the User
    And I deny the auth request
    And I get the response for the Authorization request
    Then the Authorization response should contain a geofence with a radius of 150.0, a latitude of 23.4, and a longitude of -56.7
    And the Authorization response should contain a geofence with a radius of 100.0, a latitude of -23.4, and a longitude of 56.7

  Scenario: Verify that geofences containing names received from a device can be parsed
    Given the current Authorization Policy requires a geofence with a radius of 150.0, a latitude of 23.4, a longitude of -56.7, and a name of "geo 1"
    And the current Authorization Policy requires a geofence with a radius of 100.0, a latitude of -23.4, a longitude of 56.7, and a name of "geo 2"
    When I make a Policy based Authorization request for the User
    And I deny the auth request
    And I get the response for the Authorization request
    Then the Authorization response should contain a geofence with a radius of 150.0, a latitude of 23.4, a longitude of -56.7, and a name of "geo 1"
    And the Authorization response should contain a geofence with a radius of 100.0, a latitude of -23.4, a longitude of 56.7, and a name of "geo 2"

  Scenario: Verify that required factor counts received from a device can be parsed
    Given the current Authorization Policy requires 3 factors
    When I make a Policy based Authorization request for the User
    And I deny the auth request
    And I get the response for the Authorization request
    Then the Authorization response should require 3 factors

  Scenario: Verify that required factor types received from a device can be parsed
    Given the current Authorization Policy requires inherence
    And the current Authorization Policy requires possession
    When I make a Policy based Authorization request for the User
    And I deny the auth request
    And I get the response for the Authorization request
    Then the Authorization response should require inherence
    And the Authorization response should require possession
    And the Authorization response should not require knowledge