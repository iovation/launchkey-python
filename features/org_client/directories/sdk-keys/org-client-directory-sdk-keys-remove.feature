Feature: Organization clients can create remove an SDK Key from a Directory
  In order to provide for removing Directory SDK Keys from the Directory SDK Key rotation
  As an Organization client
  I can generate and remove Directory SDK Keys

  Background:
    Given I created a Directory

  Scenario: Removing an SDK key properly removed the SDK key from the list of SDK keys for a Directory
    Given I generated and added 2 SDK Keys to the Directory
    When I remove the last generated SDK Key from the Directory
    And I retrieve the current Directory's SDK Keys
    Then the last generated SDK Key is not in the list for the Directory

  Scenario: Attempting to remove an SDK Key to an invalid Directory throws a Forbidden exception
    Given I generated and added 2 SDK Keys to the Directory
    When I attempt to remove the last generated SDK Key from the Directory with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs

  Scenario: Attempting to remove an SDK Key that does not exist throw an InvalidSDKKey exception
    Given I generated and added 2 SDK Keys to the Directory
    When I attempt to remove the last generated SDK Key "eba60cb8-c649-11e7-abc4-cec278b6b50a" from the Directory
    Then a InvalidSDKKey error occurs

  Scenario: Attempting to remove the last SDK Key from a Directory throw an LastRemainingSDKKey exception
    Given I generated and added 1 SDK Key to the Directory
    When I attempt to remove the last generated SDK Key from the Directory
    Then a LastRemainingSDKKey error occurs