Feature: Directory Client can get list of Service Sessions for a User Identifier
  In order to manage Service Sessions for a User
  As a Directory Client
  I can get a list of all User Service Sessions

  Background:
    Given I created a Directory

  Scenario: Retrieving a list of Service User Sessions for a valid user returns an empty list
    Given I made a Device linking request
    When I retrieve the Session list for the current User
    Then the Service User Session List has 0 Sessions

  Scenario: Retrieving a list of Service User Sessions for an invalid user raises an EntityNotFound exception
    When I attempt to retrieve the Session list for the User "Myxlplix"
    Then a EntityNotFound error occurs
