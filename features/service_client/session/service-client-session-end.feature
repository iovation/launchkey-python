Feature: Service Session End
  In order to manager User Service Sessions
  As a Service Client
  I can end User Service Sessions

  Background:
    Given I created a Directory
    And I created a Directory Service
    And I made a Device linking request

  Scenario: Sending Session End with valid user and no existing Service Session Succeeds
    When I send a Session End request
    Then there are no errors

  Scenario: Sending Session End with valid user and an existing Service Session Succeeds
    Given I sent a Session Start request
    When I send a Session End request
    Then there are no errors

  Scenario: Sending Session End with invalid user raise No Such User error
    When I attempt to send a Session End request for user "This is not a valid User"
    Then a EntityNotFound error occurs
