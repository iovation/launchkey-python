Feature: Organization clients can add a Public Key to a Organization Service
  In order to manage the Public Keys in the Organization Service Public Key rotation
  As an Organization client
  I can add new Public Keys to an Organization Service

  Background:
    Given I created an Organization Service

  Scenario: Adding a Public Key to an Organization Service works
    When I add a Public Key to the Organization Service
    And I retrieve the current Organization Service's Public Keys
    Then the Public Key is in the list of Public Keys for the Organization Service

  Scenario: Adding multiple Public Keys to an Organization Service works
    When I add a Public Key to the Organization Service
    When I add another Public Key to the Organization Service
    And I retrieve the current Organization Service's Public Keys
    Then the Public Key is in the list of Public Keys for the Organization Service
    And the other Public Key is in the list of Public Keys for the Organization Service

  Scenario: Attempting to add a Public Key to an invalid Organization Service throws a Forbidden exception
    When I attempt to add a Public Key to the Organization Service with the ID "eba60cb8-c649-11e7-abc4-cec278b6b50a"
    Then a Forbidden error occurs

  Scenario: Attempting to add the same Public Key twice to the same Organization Service throws a PublicKeyAlreadyInUse exception
    When I add a Public Key to the Organization Service
    And I attempt to add the same Public Key to the Organization Service
    Then a PublicKeyAlreadyInUse error occurs
