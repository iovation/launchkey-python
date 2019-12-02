@device_testing
Feature: Service Client Authorization Request: Get Device Response
  In order to complete an authorization request
  As a Directory Service
  I can retrieve an Authorization Requests that been responded to

  Background:
    Given I created a Directory
    And I have added an SDK Key to the Directory
    And I created a Directory Service
    And I have a linked Device
    And I retrieve the Devices list for the current User
    And I made an Authorization request

  Scenario: Verify that a device approval response can be parsed
    When I approve the auth request
    And I get the response for the Authorization request
    Then the Authorization response should be approved

  Scenario: Verify that a device denial response can be parsed
    When I deny the auth request
    And I get the response for the Authorization request
    Then the Authorization response should be denied