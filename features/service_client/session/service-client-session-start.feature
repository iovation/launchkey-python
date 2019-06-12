Feature: Service Session Start
  In order to manager User Service Sessions
  As a Service Client
  I can start User Service Sessions

  Background:
    Given I created a Directory
    And I created a Directory Service
    And I made a Device linking request

  Scenario: Sending Session Start with valid user and no auth request succeeds
    When I send a Session Start request with no Auth Request ID
    Then there are no errors

  Scenario: Sending Session Start with valid user and some auth request succeeds
    When I send a Session Start request with Auth Request ID "824d59a4-ffec-47b3-b5e0-54e32777f879"
    Then there are no errors

  Scenario: Sending Session Start with invalid user raise No Such User error
    When I attempt to send a Session Start request for user "This is not a valid User"
    Then a EntityNotFound error occurs

