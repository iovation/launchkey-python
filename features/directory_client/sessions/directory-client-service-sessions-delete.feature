Feature: Directory Client can remove Service Sessions for a User Identifier
  In order to manage Service Sessions for a User
  As a Directory Client
  I can end all User Service Sessions

  Background:
    Given I created a Directory

  Scenario: Deleting Service User Sessions for a valid user succeeds
    Given I made a Device linking request
    When I delete the Sessions for the current User
    And I retrieve the Session list for the current User
    Then the Service User Session List has 0 Sessions

  Scenario: Deleting Service User Sessions for an invalid user raises an EntityNotFound exception
    When I attempt to delete the Sessions for the User "Myxlplix"
    Then an EntityNotFound error occurs
