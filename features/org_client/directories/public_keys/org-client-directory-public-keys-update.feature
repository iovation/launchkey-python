Feature: Organization clients can update Directory Public Keys
  In order to manage the Public Keys in the Directory Public Key rotation
  As an Organization client
  I can update a Public Key for a Directory

  Background:
    Given I created a Directory
    And I added a Public Key to the Directory which is active and expires on "2000-01-01T00:00:00Z"

  Scenario: Updating active flag actually updates the record
    When I update the Directory Public Key to inactive
    And I retrieve the current Directory's Public Keys
    Then the Directory Public Key is inactive

  Scenario: Updating expires actually updates the record
    When I updated the Directory Public Key expiration date to "2001-02-03T04:05:06Z"
    And I retrieve the current Directory's Public Keys
    Then the Directory Public Key Expiration Date is "2001-02-03T04:05:06Z"

  Scenario: Attempting to update a Public Key for an invalid Directory throws a Forbidden exception
    When I attempt to update a Public Key for the Directory with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs

  Scenario: Attempting to update a Public Key for an invalid Directory throws a Forbidden exception 2
    When I attempt to update a Public Key identified by "aa:bb:cc:dd:ee:ff:11:22:33:44:55:66:77:88:99:00" for the Directory
    Then a PublicKeyDoesNotExist error occurs
