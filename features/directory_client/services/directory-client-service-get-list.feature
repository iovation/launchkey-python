Feature: Directory clients can get a list of their Directory Services by ID
  In order to provide for management of Directory Service entities
  As a Directory client
  I can get a list all my Directory Services by ID

  Background:
    Given I created a Directory

  Scenario: Getting a list of Directory Services includes the expected data
    Given I created a Directory Service
    When I retrieve a list of Directory Services with the created Service's ID
    Then the current Directory Service list is a list with only the current Service

  Scenario: Get an invalid Service raises an exception
    When I attempt retrieve a list of Directory Services with the Service ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
