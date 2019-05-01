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
