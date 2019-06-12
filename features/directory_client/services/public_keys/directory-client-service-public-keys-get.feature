Feature: Directory clients can retrieve a list of Public Keys for a Directory Service
  In order to manage the Public Keys in the Directory Public Key rotation
  As a Directory client
  I can get a list of Public Keys

  Background:
    Given I created a Directory
    And I created a Directory Service

  Scenario: No Public Keys returns an empty list
    When I retrieve the current Directory Service's Public Keys
    Then the Directory Service Public Keys list is empty

  Scenario: Adding a Public Key to a Directory Service works
    Given I added a Public Key to the Directory Service which is inactive and expires on "2000-01-01T00:00:00Z"
    When I retrieve the current Directory Service's Public Keys
    Then the Public Key is in the list of Public Keys for the Directory Service
    And the Directory Service Public Key is inactive
    And the Directory Service Public Key Expiration Date is "2000-01-01T00:00:00Z"

  Scenario: Attempting to get the Public Keys for an invalid Directory throws a Forbidden exception
    When I attempt to retrieve the Public Keys for the Directory Service with the Service ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
