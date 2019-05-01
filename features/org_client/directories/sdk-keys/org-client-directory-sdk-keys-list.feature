Feature: Organization clients can list the available SDK Keys for a Directory
  In order to provide for adding new Directory SDK Keys in the Directory SDK Key rotation
  As an Organization client
  I can generate and add new Directory SDK Keys

  Background:
    Given I created a Directory

  Scenario: Listing the SDK Keys for a Directory contains all of its SDK Keys
    When I generate and add an SDK Key to the Directory
    And I retrieve the current Directory's SDK Keys
    Then all of the SDK Keys for the Directory are in the SDK Keys list

  Scenario: Attempting to list the SDK Keys for an invalid Directory throws Forbidden exception
    When I attempt to retrieve the current Directory SDK Keys for the Directory with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
