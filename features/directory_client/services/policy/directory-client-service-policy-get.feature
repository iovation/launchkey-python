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
