Feature: Directory clients can get a list of all of their Organization Services
  In order to provide for management of Directory Service entities
  As a Directory client
  I can list all my Directory Services

  Background:
    Given I created a Directory

  Scenario: Getting a list of Directory Services is empty list when no Services created
    When I retrieve a list of all Directory Services
    Then the current Directory Service list is an empty list

  Scenario: Getting a list of all Services includes the expected data
    Given I created a Directory Service
    When I retrieve a list of all Directory Services
    Then the current Directory Service is in the Services list
