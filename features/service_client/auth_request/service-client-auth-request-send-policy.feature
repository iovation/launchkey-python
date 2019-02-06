Feature: Service Client Authorization Request: Can Send Policy
  In order to begin an authorization request
  As a Directory Service
  I can create an Authorization Request for a User

  # As we cannot link devices to properly attempt authorization requests, we will simply verify that the
  # Policy requests are formatted properly andxx can be accepted by the API

  Background:
    Given I created a Directory
    And I created a Directory Service

  Scenario: Making a request with a quantity of required factors for an invalid User Throws EntityNotFound
    Given the current Authorization Policy requires 3 factors
    When I attempt to make an Policy based Authorization request for the User identified by "User does not matter"
    Then a EntityNotFound error occurs

  Scenario: Making a request with required factor types for an invalid User Throws EntityNotFound
    Given the current Authorization Policy requires inherence
    And the current Authorization Policy requires knowledge
    And the current Authorization Policy requires possession
    When I attempt to make an Policy based Authorization request for the User identified by "User does not matter"
    Then a EntityNotFound error occurs

  Scenario: Making a request with a couple geofences for an invalid User Throws EntityNotFound
    Given the current Authorization Policy requires a geofence with a radius of 1.0, a latitude of 23.4, and a longitude of -56.7
    And the current Authorization Policy requires a geofence with a radius of 100.0, a latitude of -23.4, and a longitude of 56.7
    When I attempt to make an Policy based Authorization request for the User identified by "User does not matter"
    Then a EntityNotFound error occurs
