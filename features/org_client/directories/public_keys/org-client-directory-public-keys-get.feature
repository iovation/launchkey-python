Feature: Organization clients can retrieve a list of Public Keys for a Directory
  In order to manage the Public Keys in the Directory Public Key rotation
  As an Organization client
  I can get a list of Public Keys for a Directory

  Background:
    Given I created a Directory

  Scenario: No Public Keys returns an empty list
    When I retrieve the current Directory's Public Keys
    Then the Directory Public Keys list is empty

  Scenario: Adding a Public Key to a Directory works
    Given I added a Public Key to the Directory which is inactive and expires on "2000-01-01T00:00:00Z"
    When I retrieve the current Directory's Public Keys
    Then the Public Key is in the list of Public Keys for the Directory
    And the Directory Public Key is inactive
    And the Directory Public Key Expiration Date is "2000-01-01T00:00:00Z"

  Scenario: Attempting to get the Public Keys for an invalid Directory throws a Forbidden exception
    When I attempt to retrieve the Public Keys for the Directory with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
