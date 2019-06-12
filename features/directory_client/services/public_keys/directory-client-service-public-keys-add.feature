Feature: Directory clients can add a Public Key to a Directory Service
  In order to manage the Public Keys in the Directory Service Public Key rotation
  As a Directory client
  I can add new Directory Service Public Keys

  Background:
    Given I created a Directory
    And I created a Directory Service

  Scenario: Adding a Public Key to a Directory Service works
    When I add a Public Key to the Directory Service
    And I retrieve the current Directory Service's Public Keys
    Then the Directory Service Public Key is in the list of Public Keys for the Directory Service

  Scenario: Adding multiple Public Keys to a Directory Service works
    When I add a Public Key to the Directory Service
    When I add another Public Key to the Directory Service
    And I retrieve the current Directory Service's Public Keys
    Then the Directory Service Public Key is in the list of Public Keys for the Directory Service
    And the other Public Key is in the list of Public Keys for the Directory Service

  Scenario: Attempting to add a Public Key to an invalid Directory Service throws a Forbidden exception
    When I attempt to add a Public Key to the Directory Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs

  Scenario: Attempting to add the same Public Key twice to the same Directory Service throws a PublicKeyAlreadyInUse exception
    When I add a Public Key to the Directory Service
    And I attempt to add the same Public Key to the Directory Service
    Then a PublicKeyAlreadyInUse error occurs
