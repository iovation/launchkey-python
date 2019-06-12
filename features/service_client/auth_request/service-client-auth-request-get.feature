Feature: Service Client Authorization Request: Get Response
  In order to complete an authorization request
  As a Directory Service
  I can retrieve an Authorization Request for a User

  Background:
    Given I created a Directory
    And I created a Directory Service

  Scenario: Unknown auth request returns empty response
    Given I made a Device linking request
    When I get the response for Authorization request "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then the Authorization response is not returned
