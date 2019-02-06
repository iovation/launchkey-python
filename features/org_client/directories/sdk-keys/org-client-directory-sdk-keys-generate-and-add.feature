Feature: Organization clients can generate and add an SDK Key to a Directory
  In order to provide for adding new Directory SDK Keys in the Directory SDK Key rotation
  As an Organization client
  I can generate and add new Directory SDK Keys

  Background:
    Given I created a Directory

  Scenario: Generating and adding a key returns a key that is now in the list of valid keys
    When I generate and add an SDK Key to the Directory
    And I retrieve the current Directory
    Then the SDK Key is in the list for the Directory

  Scenario: Attempting to add an SDK key to an invalid Directory throws a Forbidden exception
    When I attempt to generate and add an SDK Key to the Directory with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs
